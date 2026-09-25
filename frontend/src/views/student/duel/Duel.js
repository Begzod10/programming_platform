import React, { useCallback, useEffect, useRef, useState } from 'react';
import './Duel.css';
import { useNavigate } from 'react-router-dom';
import { API_URL, useHttp, headers } from '../../../api/search/base';
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
        wrongNow: 'Xato',
        rightWas: "To'g'ri javob",
        goal: (n) => `Birinchi bo'lib ${n} ta to'g'ri javob bergan yutadi!`,
        win: '🏆 Siz yutdingiz!',
        lose: 'Bu safar raqib yutdi',
        draw: '🤝 Durang!',
        left: 'Raqib chiqib ketdi',
        again: 'Yana o‘ynash',
        namePlaceholder: 'Ismingiz (ixtiyoriy)',
        backToGames: "O'yinlarga qaytish",
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
        wrongNow: 'Ошибка',
        rightWas: 'Верный ответ',
        goal: (n) => `Побеждает тот, кто первым ответит верно ${n} раз!`,
        win: '🏆 Ты победил!',
        lose: 'В этот раз победил соперник',
        draw: '🤝 Ничья!',
        left: 'Соперник вышел',
        again: 'Играть ещё',
        namePlaceholder: 'Твоё имя (необязательно)',
        backToGames: 'Назад к играм',
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

// A guest (no account - the /play kids' area) is identified only by a random
// id kept in this browser; the server never shows it to the other player.
function getGuestId() {
    try {
        let id = localStorage.getItem('duel_guest_id');
        if (!id) {
            id = (window.crypto?.randomUUID?.() || `${Date.now()}${Math.random().toString(36).slice(2)}`)
                .replace(/[^A-Za-z0-9]/g, '').slice(0, 32);
            localStorage.setItem('duel_guest_id', id);
        }
        return id;
    } catch {
        return `tmp${Math.random().toString(36).slice(2)}${Date.now()}`.slice(0, 32);
    }
}

/** 1-vs-1 math race — see backend/app/api/v1/endpoints/duel.py for the
 * rules and the WebSocket protocol. This component holds no game logic at
 * all: it renders whatever `state` the server last sent and forwards
 * clicks as {type:"answer"}, so the server stays the single referee. */
function DuelInner({ guest }) {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const navigate = useNavigate();
    const L = TEXT[lang === 'ru' ? 'ru' : 'uz'];
    const [guestId] = useState(() => (guest ? getGuestId() : null));
    const [guestName, setGuestName] = useState(() => {
        try { return localStorage.getItem('duel_guest_name') || ''; } catch { return ''; }
    });

    const [code, setCode] = useState(null);
    const [game, setGame] = useState(null);
    const [error, setError] = useState('');
    const [codeInput, setCodeInput] = useState('');
    const [busy, setBusy] = useState(false);
    const lastSoundRef = useRef(null);
    const [pendingQ, setPendingQ] = useState(null);

    const onMessage = useCallback((msg) => {
        if (msg.type === 'state') {
            setGame(msg.data);
        } else if (msg.type === 'error') {
            setError(msg.reason);
            setCode(null);
            setGame(null);
        }
    }, []);

    const { send } = useSessionSocket(
        code, noop, null, onMessage, 'duels',
        guest ? `guest=${guestId}&name=${encodeURIComponent(guestName.trim())}` : '',
        !guest,
    );

    const rememberName = () => {
        try { localStorage.setItem('duel_guest_name', guestName.trim()); } catch { /* ignore */ }
    };

    // Sound cues, once per own answer / finished game.
    useEffect(() => {
        if (!game) return;
        const key = game.status === 'finished'
            ? `end-${game.winner_id}-${game.finish_reason}`
            : game.last ? `q-${game.last.q}-${game.last.correct}` : null;
        if (!key || lastSoundRef.current === key) return;
        lastSoundRef.current = key;
        if (game.status === 'finished') {
            playSynth(game.winner_id === game.you ? 'fanfare' : 'chime');
        } else {
            playSynth(game.last.correct ? 'coin' : 'laser');
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
            if (guest) rememberName();
            const res = guest
                ? await request(`${API_URL}v1/duels/guest`, 'POST', JSON.stringify({ guest_id: guestId }), { 'Content-Type': 'application/json' })
                : await request(`${API_URL}v1/duels/`, 'POST', JSON.stringify({}), headers());
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
            if (guest) rememberName();
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
                    {guest && (
                        <input
                            className="duel-name-input"
                            maxLength={20}
                            placeholder={L.namePlaceholder}
                            value={guestName}
                            onChange={(e) => setGuestName(e.target.value)}
                        />
                    )}
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
                    {guest && (
                        <button className="duel-btn duel-btn--ghost" onClick={() => navigate('/play')}>
                            ← {L.backToGames}
                        </button>
                    )}
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
    const isHost = game.host_id === game.you;

    const scoreboard = (
        <div className="duel-scores">
            <div className="duel-score duel-score--me">
                <span className="duel-score-name">{L.you}</span>
                <span className="duel-score-num">{me?.score ?? 0}<small>/{game.target}</small></span>
            </div>
            <div className="duel-vs">VS</div>
            <div className={`duel-score ${opp && !opp.online ? 'is-offline' : ''}`}>
                <span className="duel-score-name">{opp?.name || '…'}</span>
                <span className="duel-score-num">{opp?.score ?? 0}<small>/{game.target}</small></span>
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
    // No waiting anywhere: an answer (right or wrong) moves THIS player on to
    // their next question at once; the first to reach `target` wins.
    const q = game.question;
    const last = game.last;
    const answered = pendingQ === game.q_index;
    const submit = (opt) => {
        if (answered) return;
        if (send({ type: 'answer', q: game.q_index, choice: opt })) setPendingQ(game.q_index);
    };
    let banner = '';
    if (last) {
        banner = last.correct ? L.correct : `${L.wrongNow} — ${L.rightWas}: ${last.answer}`;
    }

    return (
        <div className="duel-page">
            <div className="duel-card">
                {scoreboard}
                <div className="duel-progress">{L.goal(game.target)}</div>
                {q && (
                    <>
                        <div className="duel-question" key={game.q_index}>{q.text} {q.text.includes('?') ? '' : '= ?'}</div>
                        <div className="duel-options">
                            {q.options.map((opt) => (
                                <button
                                    key={`${game.q_index}-${opt}`}
                                    className="duel-option"
                                    disabled={answered}
                                    onClick={() => submit(opt)}
                                >
                                    {opt}
                                </button>
                            ))}
                        </div>
                    </>
                )}
                <div className={`duel-banner ${last?.correct ? 'is-good' : ''}`}>{banner}&nbsp;</div>
            </div>
        </div>
    );
}

/** /student/duel (logged-in) and /play/duel (guest, no account). */
export default function Duel({ guest = false }) {
    if (guest) {
        return (
            <div className="duel-guest-shell">
                <DuelInner guest />
            </div>
        );
    }
    return <DuelInner guest={false} />;
}
