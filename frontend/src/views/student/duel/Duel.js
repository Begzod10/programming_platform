import React, { useCallback, useEffect, useRef, useState } from 'react';
import './Duel.css';
import { API_URL, useHttp, headers, getCurrentUser } from '../../../api/search/base';
import { useSessionSocket } from '../../../hooks/useSessionSocket';
import { useTranslation } from '../../../i18n/useTranslation';
import { playSynth } from '../../../utils/soundSynth';

const TEXT = {
    uz: {
        title: '1 vs 1 poyga',
        sub: "Do'sting bilan bir xil savollarga kim tezroq javob beradi?",
        create: 'Xona yaratish',
        or: 'yoki',
        codePlaceholder: '4 xonali kod',
        join: "Qo'shilish",
        connecting: 'Ulanmoqda…',
        yourCode: 'Xona kodi',
        shareCode: "Bu kodni do'stingizga ayting",
        waitingFriend: "Do'st kutilmoqda…",
        start: 'Boshlash',
        waitHost: 'Xona egasi boshlashini kuting…',
        leave: 'Chiqish',
        ready: 'Tayyor bo‘l!',
        you: 'Siz',
        online: 'ulangan',
        offline: 'uzilgan',
        correct: "To'g'ri! +1",
        opponentFirst: 'Raqib tezroq topdi',
        nobody: 'Hech kim topa olmadi',
        wrongWait: 'Xato! Raqibni kuting…',
        win: '🏆 Siz yutdingiz!',
        lose: 'Bu safar raqib yutdi',
        draw: '🤝 Durang!',
        left: 'Raqib chiqib ketdi',
        again: 'Yana o‘ynash',
        errors: {
            not_found: 'Bunday xona topilmadi. Kodni tekshiring.',
            full: 'Bu xonada allaqachon 2 kishi bor.',
            started: "O'yin allaqachon boshlangan.",
            host_left: 'Xona egasi chiqib ketdi.',
            create: 'Xona yaratib bo‘lmadi, qayta urining.',
        },
    },
    ru: {
        title: 'Дуэль 1 на 1',
        sub: 'Кто быстрее ответит на одинаковые вопросы?',
        create: 'Создать комнату',
        or: 'или',
        codePlaceholder: 'Код из 4 цифр',
        join: 'Войти',
        connecting: 'Подключение…',
        yourCode: 'Код комнаты',
        shareCode: 'Назови этот код другу',
        waitingFriend: 'Ждём друга…',
        start: 'Начать',
        waitHost: 'Ждём, пока хозяин комнаты начнёт…',
        leave: 'Выйти',
        ready: 'Приготовься!',
        you: 'Ты',
        online: 'на связи',
        offline: 'нет связи',
        correct: 'Верно! +1',
        opponentFirst: 'Соперник был быстрее',
        nobody: 'Никто не ответил верно',
        wrongWait: 'Ошибка! Ждём соперника…',
        win: '🏆 Ты победил!',
        lose: 'В этот раз победил соперник',
        draw: '🤝 Ничья!',
        left: 'Соперник вышел',
        again: 'Играть ещё',
        errors: {
            not_found: 'Такой комнаты нет. Проверь код.',
            full: 'В этой комнате уже двое.',
            started: 'Игра уже началась.',
            host_left: 'Хозяин комнаты вышел.',
            create: 'Не удалось создать комнату, попробуй ещё раз.',
        },
    },
};

const noop = () => {};

/** 1-vs-1 math race — see backend/app/api/v1/endpoints/duel.py for the
 * rules and the WebSocket protocol. This component holds no game logic at
 * all: it renders whatever `state` the server last sent and forwards
 * clicks as {type:"answer"}, so the server stays the single referee. */
export default function Duel() {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const L = TEXT[lang === 'ru' ? 'ru' : 'uz'];
    const meId = getCurrentUser()?.id;

    const [code, setCode] = useState(null);
    const [game, setGame] = useState(null);
    const [error, setError] = useState('');
    const [codeInput, setCodeInput] = useState('');
    const [busy, setBusy] = useState(false);
    const lastSoundRef = useRef(null);

    const onMessage = useCallback((msg) => {
        if (msg.type === 'state') {
            setGame(msg.data);
        } else if (msg.type === 'error') {
            setError(msg.reason);
            setCode(null);
            setGame(null);
        }
    }, []);

    const { send } = useSessionSocket(code, noop, null, onMessage, 'duels');

    // Sound cues, once per resolved question / finished game.
    useEffect(() => {
        if (!game) return;
        const key = game.status === 'finished'
            ? `end-${game.winner_id}-${game.finish_reason}`
            : game.last_result ? `q-${game.last_result.q}-${game.last_result.winner_id}` : null;
        if (!key || lastSoundRef.current === key) return;
        lastSoundRef.current = key;
        if (game.status === 'finished') {
            playSynth(game.winner_id === game.you ? 'fanfare' : 'chime');
        } else if (game.last_result.winner_id === game.you) {
            playSynth('coin');
        } else if (game.last_result.winner_id) {
            playSynth('laser');
        }
    }, [game]);

    const leave = () => {
        setCode(null);
        setGame(null);
        setError('');
        lastSoundRef.current = null;
    };

    const createRoom = async () => {
        setBusy(true);
        setError('');
        try {
            const res = await request(`${API_URL}v1/duels/`, 'POST', JSON.stringify({}), headers());
            setCode(res.code);
        } catch {
            setError('create');
        } finally {
            setBusy(false);
        }
    };

    const joinRoom = (e) => {
        e.preventDefault();
        const c = codeInput.trim();
        if (c.length === 4) {
            setError('');
            setCode(c);
        }
    };

    // ── lobby ──
    if (!code) {
        return (
            <div className="duel-page">
                <div className="duel-card">
                    <div className="duel-emoji">⚔️</div>
                    <h2>{L.title}</h2>
                    <p className="duel-sub">{L.sub}</p>
                    {error && <div className="duel-error">{L.errors[error] || error}</div>}
                    <button className="duel-btn duel-btn--primary" onClick={createRoom} disabled={busy}>
                        {L.create}
                    </button>
                    <div className="duel-or">{L.or}</div>
                    <form className="duel-join" onSubmit={joinRoom}>
                        <input
                            className="duel-code-input"
                            inputMode="numeric"
                            maxLength={4}
                            placeholder={L.codePlaceholder}
                            value={codeInput}
                            onChange={(e) => setCodeInput(e.target.value.replace(/\D/g, ''))}
                        />
                        <button className="duel-btn" type="submit" disabled={codeInput.length !== 4}>
                            {L.join}
                        </button>
                    </form>
                </div>
            </div>
        );
    }

    if (!game) {
        return (
            <div className="duel-page">
                <div className="duel-card"><p className="duel-sub">{L.connecting}</p></div>
            </div>
        );
    }

    const me = game.players.find((p) => p.id === game.you);
    const opp = game.players.find((p) => p.id !== game.you);
    const isHost = game.host_id === game.you || game.host_id === meId;

    const scoreboard = (
        <div className="duel-scores">
            <div className="duel-score duel-score--me">
                <span className="duel-score-name">{L.you}</span>
                <span className="duel-score-num">{me?.score ?? 0}</span>
            </div>
            <div className="duel-vs">VS</div>
            <div className={`duel-score ${opp && !opp.online ? 'is-offline' : ''}`}>
                <span className="duel-score-name">{opp?.name || '…'}</span>
                <span className="duel-score-num">{opp?.score ?? 0}</span>
                {opp && !opp.online && <span className="duel-offline">{L.offline}</span>}
            </div>
        </div>
    );

    // ── waiting room ──
    if (game.status === 'waiting') {
        return (
            <div className="duel-page">
                <div className="duel-card">
                    <p className="duel-sub">{L.shareCode}</p>
                    <div className="duel-code">{game.code}</div>
                    <ul className="duel-players">
                        {game.players.map((p) => (
                            <li key={p.id}>👤 {p.name}{p.id === game.you ? ` (${L.you})` : ''}</li>
                        ))}
                        {game.players.length < 2 && <li className="duel-waiting">⏳ {L.waitingFriend}</li>}
                    </ul>
                    {isHost ? (
                        <button
                            className="duel-btn duel-btn--primary"
                            disabled={game.players.length < 2}
                            onClick={() => send({ type: 'start' })}
                        >
                            {L.start}
                        </button>
                    ) : (
                        <p className="duel-sub">{L.waitHost}</p>
                    )}
                    <button className="duel-btn duel-btn--ghost" onClick={leave}>{L.leave}</button>
                </div>
            </div>
        );
    }

    if (game.status === 'countdown') {
        return (
            <div className="duel-page">
                <div className="duel-card">
                    {scoreboard}
                    <div className="duel-countdown">{L.ready}</div>
                </div>
            </div>
        );
    }

    // ── finished ──
    if (game.status === 'finished') {
        const won = game.winner_id === game.you;
        const draw = game.winner_id == null;
        return (
            <div className="duel-page">
                <div className="duel-card">
                    {scoreboard}
                    <div className={`duel-result ${won ? 'is-win' : ''}`}>
                        {draw ? L.draw : won ? L.win : L.lose}
                    </div>
                    {game.finish_reason === 'left' && <p className="duel-sub">{L.left}</p>}
                    {isHost && game.players.length === 2 && opp?.online && (
                        <button className="duel-btn duel-btn--primary" onClick={() => send({ type: 'rematch' })}>
                            {L.again}
                        </button>
                    )}
                    <button className="duel-btn duel-btn--ghost" onClick={leave}>{L.leave}</button>
                </div>
            </div>
        );
    }

    // ── playing ──
    const q = game.question;
    const result = game.last_result;
    let banner = '';
    if (result) {
        banner = result.winner_id === game.you ? L.correct : result.winner_id ? L.opponentFirst : L.nobody;
    } else if (me?.locked) {
        banner = L.wrongWait;
    }
    const disabled = game.resolved || me?.locked;

    return (
        <div className="duel-page">
            <div className="duel-card">
                {scoreboard}
                <div className="duel-progress">{game.q_index + 1} / {game.total}</div>
                {q && (
                    <>
                        <div className="duel-question">{q.text} {q.text.includes('?') ? '' : '= ?'}</div>
                        <div className="duel-options">
                            {q.options.map((opt) => (
                                <button
                                    key={opt}
                                    className={`duel-option ${result && result.answer === opt ? 'is-correct' : ''}`}
                                    disabled={disabled}
                                    onClick={() => send({ type: 'answer', q: game.q_index, choice: opt })}
                                >
                                    {opt}
                                </button>
                            ))}
                        </div>
                    </>
                )}
                <div className={`duel-banner ${result?.winner_id === game.you ? 'is-good' : ''}`}>{banner}&nbsp;</div>
            </div>
        </div>
    );
}
