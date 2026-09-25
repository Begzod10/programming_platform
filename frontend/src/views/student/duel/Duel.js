import React, { useCallback, useEffect, useRef, useState } from 'react';
import './Duel.css';
import { useNavigate } from 'react-router-dom';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { useSessionSocket } from '../../../hooks/useSessionSocket';
import { useTranslation } from '../../../i18n/useTranslation';
import { playSynth } from '../../../utils/soundSynth';

const TEXT = {
    uz: {
        title: 'Poyga',
        sub: "Do'stlaring (2–4 kishi) yoki kompyuter bilan bir xil savollarga kim tezroq javob beradi?",
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
        left: "Boshqa o'yinchilar chiqib ketdi",
        again: 'Yana o‘ynash',
        pickGames: "O'yin turlarini tanlang",
        levelTitle: 'Qiyinlik',
        levels: { easy: '🟢 Oson', medium: '🟡 O\'rta', hard: '🔴 Qiyin' },
        addBot: '🤖 Kompyuter qo\'shish',
        removeBot: '🤖 Kompyuterni olib tashlash',
        players: (n, m) => `O'yinchilar: ${n}/${m}`,
        leaderboard: '🏆 Eng ko\'p yutganlar',
        wins: 'yutuq',
        games: "o'yin",
        yourStats: (w, g) => `Sizning natijangiz: ${w} yutuq / ${g} o'yin`,
        winner: (n) => `🏆 ${n} yutdi!`,
        offlineTag: 'chiqib ketdi',
        teamMode: '👥 2 ga 2 (jamoaviy)',
        teamNeeds: '2 ga 2 uchun 4 kishi kerak (kompyuter ham bo\'ladi)',
        teamName: ['🔵 A jamoa', '🔴 B jamoa'],
        teamWin: (n) => `🏆 ${n} yutdi!`,
        teamGoal: (n) => `Jamoangiz birgalikda ${n} ta to'g'ri javob bersin!`,
        addBotOne: '🤖 + Kompyuter',
        removeBotOne: '🤖 − Kompyuter',
        badges: [
            { emoji: '🥉', label: "Birinchi g'alaba", need: (w) => w >= 1 },
            { emoji: '🥈', label: "10 ta g'alaba", need: (w) => w >= 10 },
            { emoji: '🥇', label: "50 ta g'alaba", need: (w) => w >= 50 },
            { emoji: '🎮', label: "10 ta o'yin", need: (w, g) => g >= 10 },
        ],
        hostPicks: 'Turlarni xona egasi tanlaydi',
        kindNames: {
            arith: '➕ Hisob', compare: '⚖️ Katta-kichik', count: '🍎 Sanash',
            pattern: '🔴 Naqsh', sequence: '🔢 Ketma-ketlik', odd: '🧩 Ortiqchasi',
            mult: '✖️ Ko\'paytirish', clock: '🕒 Soat', color: '🎨 Rang', word: '🔤 So\'z', quiz: '🌍 Bilim',
        },
        hints: {
            arith: 'Hisobla',
            compare: 'Qaysi belgi kerak?',
            count: 'Nechta?',
            pattern: 'Keyingisi qaysi?',
            sequence: 'Keyingi son qaysi?',
            odd: 'Ortiqchasini top!',
            mult: 'Ko\'paytir',
            clock: 'Soat nechchi?',
            color: 'Matn RANGI qaysi? (so\'zni emas!)',
            word: 'Yetishmayotgan harf qaysi?',
            quiz: 'Savolga javob ber',
        },
        namePlaceholder: 'Ismingiz (ixtiyoriy)',
        backToGames: "O'yinlarga qaytish",
        errors: {
            not_found: 'Bunday xona topilmadi. Kodni tekshiring.',
            full: 'Bu xona to\'lgan (4 kishi).',
            started: "O'yin allaqachon boshlangan.",
            host_left: 'Xona egasi chiqib ketdi.',
            create: 'Xona yaratib bo‘lmadi, qayta urining.',
        },
    },
    ru: {
        title: 'Гонка',
        sub: 'Кто быстрее ответит на одинаковые вопросы — с друзьями (2–4) или с компьютером?',
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
        left: 'Остальные игроки вышли',
        again: 'Играть ещё',
        pickGames: 'Выбери виды игр',
        levelTitle: 'Сложность',
        levels: { easy: '🟢 Лёгкий', medium: '🟡 Средний', hard: '🔴 Сложный' },
        addBot: '🤖 Добавить компьютер',
        removeBot: '🤖 Убрать компьютер',
        players: (n, m) => `Игроки: ${n}/${m}`,
        leaderboard: '🏆 Больше всех побед',
        wins: 'побед',
        games: 'игр',
        yourStats: (w, g) => `Твой счёт: ${w} побед / ${g} игр`,
        winner: (n) => `🏆 Победил ${n}!`,
        offlineTag: 'вышел',
        teamMode: '👥 2 на 2 (командная)',
        teamNeeds: 'Для 2 на 2 нужно 4 игрока (можно с компьютером)',
        teamName: ['🔵 Команда A', '🔴 Команда B'],
        teamWin: (n) => `🏆 Победила ${n}!`,
        teamGoal: (n) => `Командой ответьте верно ${n} раз!`,
        addBotOne: '🤖 + Компьютер',
        removeBotOne: '🤖 − Компьютер',
        badges: [
            { emoji: '🥉', label: 'Первая победа', need: (w) => w >= 1 },
            { emoji: '🥈', label: '10 побед', need: (w) => w >= 10 },
            { emoji: '🥇', label: '50 побед', need: (w) => w >= 50 },
            { emoji: '🎮', label: '10 игр', need: (w, g) => g >= 10 },
        ],
        hostPicks: 'Виды выбирает хозяин комнаты',
        kindNames: {
            arith: '➕ Счёт', compare: '⚖️ Больше-меньше', count: '🍎 Сколько',
            pattern: '🔴 Узор', sequence: '🔢 Числа', odd: '🧩 Лишнее',
            mult: '✖️ Умножение', clock: '🕒 Часы', color: '🎨 Цвет', word: '🔤 Слово', quiz: '🌍 Знания',
        },
        hints: {
            arith: 'Посчитай',
            compare: 'Какой знак?',
            count: 'Сколько?',
            pattern: 'Что дальше?',
            sequence: 'Какое число дальше?',
            odd: 'Найди лишнее!',
            mult: 'Умножь',
            clock: 'Сколько времени?',
            color: 'Какого ЦВЕТА буквы? (не слово!)',
            word: 'Какой буквы не хватает?',
            quiz: 'Ответь на вопрос',
        },
        namePlaceholder: 'Твоё имя (необязательно)',
        backToGames: 'Назад к играм',
        errors: {
            not_found: 'Такой комнаты нет. Проверь код.',
            full: 'Комната заполнена (4 игрока).',
            started: 'Игра уже началась.',
            host_left: 'Хозяин комнаты вышел.',
            create: 'Не удалось создать комнату, попробуй ещё раз.',
        },
    },
};

const noop = () => {};

// Question text / option labels may be plain strings or {uz, ru} objects
// (options as {v, uz, ru}: show the label, but always send `v`).
const loc = (x, lang) => (x && typeof x === 'object' ? (x[lang] ?? x.uz ?? '') : x);
const optValue = (o) => (o && typeof o === 'object' ? o.v : o);
const EMOJI_KINDS = ['count', 'pattern', 'odd', 'clock', 'word'];

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
    const [board, setBoard] = useState(null);

    useEffect(() => {
        if (guest || code) return;
        let alive = true;
        request(`${API_URL}v1/duels/leaderboard`, 'GET', null, headers())
            .then((r) => { if (alive) setBoard(r); })
            .catch(() => {});
        return () => { alive = false; };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [guest, code]);

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
            ? `end-${game.winner_id}-${game.winner_team}-${game.finish_reason}`
            : game.last ? `q-${game.last.q}-${game.last.correct}` : null;
        if (!key || lastSoundRef.current === key) return;
        lastSoundRef.current = key;
        if (game.status === 'finished') {
            const mine = game.players.find((p) => p.id === game.you);
            const won = game.team_mode ? mine?.team === game.winner_team : game.winner_id === game.you;
            playSynth(won ? 'fanfare' : 'chime');
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
                    {board && board.top.length > 0 && (
                        <div className="duel-board">
                            <div className="duel-sub">{L.leaderboard}</div>
                            <ol>
                                {board.top.slice(0, 10).map((r, i) => (
                                    <li key={r.student_id} className={r.student_id === board.me_id ? 'is-me' : ''}>
                                        <span>{['🥇', '🥈', '🥉'][i] || `${i + 1}.`} {r.name}</span>
                                        <b>{r.wins} {L.wins}</b>
                                    </li>
                                ))}
                            </ol>
                            <div className="duel-sub">{L.yourStats(board.me.wins, board.me.games)}</div>
                            <div className="duel-badges">
                                {L.badges.map((b) => (
                                    <span key={b.label} className={`duel-badge ${b.need(board.me.wins, board.me.games) ? 'is-on' : ''}`} title={b.label}>
                                        {b.emoji} {b.label}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
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

    const isHost = game.host_id === game.you;
    const hasBot = game.players.some((p) => p.bot);
    const ranked = [...game.players].sort((x, y) => y.score - x.score);

    const myTeam = game.players.find((p) => p.id === game.you)?.team;
    const playerCell = (p) => (
        <div
            key={p.id}
            className={`duel-score ${p.id === game.you ? 'duel-score--me' : ''} ${!p.online || p.left ? 'is-offline' : ''}`}
        >
            <span className="duel-score-name">{p.id === game.you ? L.you : p.name}</span>
            <span className="duel-score-num">{p.score}{!game.team_mode && <small>/{game.target}</small>}</span>
            {p.left ? <span className="duel-offline">{L.offlineTag}</span>
                : !p.online && <span className="duel-offline">{L.offline}</span>}
        </div>
    );
    const scoreboard = game.team_mode ? (
        <div className="duel-teams">
            {[0, 1].map((tm) => (
                <div key={tm} className={`duel-team duel-team--${tm} ${myTeam === tm ? 'is-mine' : ''}`}>
                    <div className="duel-team-head">
                        <span>{L.teamName[tm]}</span>
                        <b>{game.team_scores?.[tm] ?? 0}<small>/{game.team_target}</small></b>
                    </div>
                    <div className="duel-scores duel-scores--multi">
                        {game.players.filter((p) => p.team === tm).map(playerCell)}
                    </div>
                </div>
            ))}
        </div>
    ) : (
        <div className="duel-scores duel-scores--multi">{game.players.map(playerCell)}</div>
    );

    const toggleKind = (k) => {
        const cur = game.kinds || [];
        const next = cur.includes(k) ? cur.filter((x) => x !== k) : [...cur, k];
        if (next.length) send({ type: 'kinds', kinds: next });
    };
    const kindPicker = (
        <div className="duel-kinds">
            <div className="duel-sub">{L.pickGames}</div>
            <div className="duel-kind-row">
                {(game.all_kinds || []).map((k) => {
                    const on = (game.kinds || []).includes(k);
                    return (
                        <button
                            key={k}
                            type="button"
                            className={`duel-kind ${on ? 'is-on' : ''}`}
                            disabled={!isHost}
                            onClick={() => toggleKind(k)}
                        >
                            {L.kindNames[k]}
                        </button>
                    );
                })}
            </div>
            <div className="duel-sub">{L.levelTitle}</div>
            <div className="duel-kind-row">
                {['easy', 'medium', 'hard'].map((lv) => (
                    <button
                        key={lv}
                        type="button"
                        className={`duel-kind ${game.level === lv ? 'is-on' : ''}`}
                        disabled={!isHost}
                        onClick={() => send({ type: 'level', level: lv })}
                    >
                        {L.levels[lv]}
                    </button>
                ))}
            </div>
            {isHost && (
                <>
                    <button
                        type="button"
                        className={`duel-kind ${game.team_mode ? 'is-on' : ''}`}
                        onClick={() => send({ type: 'team_mode', on: !game.team_mode })}
                    >
                        {L.teamMode}
                    </button>
                    {game.team_mode && game.players.length < game.max_players && <div className="duel-sub">{L.teamNeeds}</div>}
                    <div className="duel-kind-row">
                        {game.players.length < game.max_players && (
                            <button type="button" className="duel-btn" onClick={() => send({ type: 'add_bot' })}>{L.addBotOne}</button>
                        )}
                        {hasBot && (
                            <button type="button" className="duel-btn duel-btn--ghost" onClick={() => send({ type: 'remove_bot' })}>{L.removeBotOne}</button>
                        )}
                    </div>
                </>
            )}
            {!isHost && game.team_mode && <div className="duel-sub">{L.teamMode}</div>}
            {!isHost && <div className="duel-sub">{L.hostPicks}</div>}
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
                            <li key={p.id}>{p.bot ? '🤖' : '👤'} {p.name}{p.id === game.you ? ` (${L.you})` : ''}{game.team_mode ? ` — ${L.teamName[p.team]}` : ''}</li>
                        ))}
                        {game.players.length < 2 && <li className="duel-waiting">⏳ {L.waitingFriend}</li>}
                    </ul>
                    <p className="duel-sub">{L.players(game.players.length, game.max_players)}</p>
                    {kindPicker}
                    {isHost ? (
                        <button
                            className="duel-btn duel-btn--primary"
                            disabled={game.team_mode ? game.players.length !== game.max_players : game.players.length < 2}
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
        const won = game.team_mode ? myTeam === game.winner_team : game.winner_id === game.you;
        const draw = game.team_mode ? game.winner_team == null : game.winner_id == null;
        const winnerName = game.players.find((p) => p.id === game.winner_id)?.name;
        return (
            <div className="duel-page">
                <div className="duel-card">
                    {scoreboard}
                    <div className={`duel-result ${won ? 'is-win' : ''}`}>
                        {draw ? L.draw : won ? L.win : game.team_mode ? L.teamWin(L.teamName[game.winner_team]) : L.winner(winnerName)}
                    </div>
                    {!game.team_mode && ranked.length > 2 && (
                        <ol className="duel-ranking">
                            {ranked.map((p, i) => (
                                <li key={p.id}>{['🥇', '🥈', '🥉'][i] || `${i + 1}.`} {p.id === game.you ? L.you : p.name} — {p.score}</li>
                            ))}
                        </ol>
                    )}
                    {game.finish_reason === 'left' && <p className="duel-sub">{L.left}</p>}
                    {isHost && kindPicker}
                    {isHost && game.players.filter((p) => p.online && !p.left).length >= 2
                        && (!game.team_mode || game.players.length === game.max_players) && (
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
        banner = last.correct ? L.correct : `${L.wrongNow} — ${L.rightWas}: ${last.answer_label?.[lang] ?? last.answer}`;
    }

    return (
        <div className="duel-page">
            <div className="duel-card">
                {scoreboard}
                <div className="duel-progress">{game.team_mode ? L.teamGoal(game.team_target) : L.goal(game.target)}</div>
                {q && (
                    <>
                        {L.hints[q.kind] && <div className="duel-hint">{L.hints[q.kind]}</div>}
                        <div
                            className={`duel-question ${EMOJI_KINDS.includes(q.kind) ? 'is-emoji' : ''} ${q.kind === 'quiz' ? 'is-quiz' : ''}`}
                            style={q.ink ? { color: q.ink, fontWeight: 900 } : undefined}
                            key={game.q_index}
                        >
                            {loc(q.text, lang)}{q.kind === 'arith' || q.kind === 'mult' ? ' = ?' : ''}
                        </div>
                        <div className="duel-options">
                            {q.options.map((opt) => (
                                <button
                                    key={`${game.q_index}-${optValue(opt)}`}
                                    className="duel-option"
                                    disabled={answered}
                                    onClick={() => submit(optValue(opt))}
                                >
                                    {loc(opt, lang)}
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
