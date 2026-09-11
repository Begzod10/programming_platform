import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './Quiz.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { HelpCircle, CheckCircle2, XCircle, Trophy, ArrowLeft, Clock, BookOpen, Sparkles } from 'lucide-react';

const OPTION_KEYS = ['A', 'B', 'C', 'D'];

const DIFF_EMOJI = { beginner: '🌱', intermediate: '🔥', advanced: '⚡' };

function QuizCard({ quiz, myResult, onStart }) {
    const passed = myResult?.passed;
    const diffKey = (quiz.difficulty_level || 'beginner').toLowerCase();
    return (
        <button className={`qz-card qz-card--${diffKey}`} onClick={() => onStart(quiz.id)}>
            <div className="qz-card-glow" aria-hidden="true" />
            <div className="qz-card-top">
                <span className="qz-card-diff">
                    {DIFF_EMOJI[diffKey] || '📘'} {quiz.difficulty_level}
                </span>
                {passed && (
                    <span className="qz-card-passed" title="O'tilgan">
                        <CheckCircle2 size={15} /> {myResult.score}%
                    </span>
                )}
            </div>
            <h3 className="qz-card-title">{quiz.title}</h3>
            {quiz.description && <p className="qz-card-desc">{quiz.description}</p>}
            {quiz.course_title && (
                <span className="qz-card-course"><BookOpen size={12} /> {quiz.course_title}</span>
            )}
            <div className="qz-card-meta">
                {quiz.time_limit_minutes && (
                    <span><Clock size={13} /> {quiz.time_limit_minutes} daq</span>
                )}
                {quiz.points_reward > 0 && (
                    <span className="qz-card-pts"><Sparkles size={13} /> +{quiz.points_reward}</span>
                )}
            </div>
            <span className="qz-card-cta">{passed ? 'Qayta urinish' : 'Boshlash'} →</span>
        </button>
    );
}

export default function Quiz() {
    const { quizId } = useParams();
    const navigate = useNavigate();
    const { request } = useHttp();

    const [quizzes,   setQuizzes]   = useState([]);
    const [myResults, setMyResults] = useState([]);
    const [loading,   setLoading]   = useState(true);
    const [error,     setError]     = useState('');

    const [activeQuiz, setActiveQuiz] = useState(null); // full quiz w/ questions
    const [qIndex,      setQIndex]      = useState(0);
    const [answers,     setAnswers]     = useState({}); // { questionId: 'A' }
    const [startedAt,   setStartedAt]   = useState(null);
    const [result,      setResult]      = useState(null); // submit response

    const loadList = useCallback(() => {
        setLoading(true);
        setError('');
        Promise.all([
            request(`${API_URL}v1/quizzes/?limit=100`, 'GET', null, headers()),
            request(`${API_URL}v1/quizzes/my-results`, 'GET', null, headers()),
        ])
            .then(([qz, res]) => { setQuizzes(qz || []); setMyResults(res || []); })
            .catch(() => setError("Viktorinalarni yuklab bo'lmadi"))
            .finally(() => setLoading(false));
    }, [request]);

    const loadQuiz = useCallback((id) => {
        setLoading(true);
        setError('');
        setResult(null);
        setAnswers({});
        setQIndex(0);
        request(`${API_URL}v1/quizzes/${id}`, 'GET', null, headers())
            .then(q => { setActiveQuiz(q); setStartedAt(Date.now()); })
            .catch(() => setError("Testni yuklab bo'lmadi"))
            .finally(() => setLoading(false));
    }, [request]);

    useEffect(() => {
        if (quizId) loadQuiz(quizId);
        else { setActiveQuiz(null); loadList(); }
    }, [quizId, loadQuiz, loadList]);

    const bestResultFor = (id) => {
        const mine = myResults.filter(r => r.quiz_id === id);
        if (!mine.length) return null;
        return mine.reduce((best, r) => (r.score > best.score ? r : best), mine[0]);
    };

    const handleStart = (id) => navigate(`/student/quiz/${id}`);
    const handleBack = () => navigate('/student/quiz');

    const question = activeQuiz?.questions?.[qIndex];
    const totalQuestions = activeQuiz?.questions?.length || 0;
    const isLast = qIndex === totalQuestions - 1;

    const selectAnswer = (key) => {
        if (!question) return;
        setAnswers(prev => ({ ...prev, [question.id]: key }));
    };

    const handleNext = () => {
        if (!isLast) { setQIndex(i => i + 1); return; }
        // Submit
        const payload = {
            answers: Object.entries(answers).map(([question_id, answer]) => ({
                question_id: Number(question_id), answer,
            })),
            time_spent_seconds: startedAt ? Math.round((Date.now() - startedAt) / 1000) : null,
        };
        setLoading(true);
        request(`${API_URL}v1/quizzes/${activeQuiz.id}/submit`, 'POST', payload, headers())
            .then(res => setResult(res))
            .catch(() => setError("Natijani yuborib bo'lmadi"))
            .finally(() => setLoading(false));
    };

    // ── RESULT SCREEN ──
    if (result) {
        return (
            <div className="qz-root qz-result-wrap">
                <div className={`qz-result ${result.passed ? 'qz-result--pass' : 'qz-result--fail'}`}>
                    <div className="qz-result-icon-wrap">
                        {result.passed
                            ? <CheckCircle2 size={44} className="qz-result-icon" />
                            : <XCircle size={44} className="qz-result-icon" />}
                    </div>
                    <h2>{result.passed ? "O'tdingiz!" : 'Keyingi safar!'}</h2>
                    <p className="qz-result-score">{result.score}%</p>
                    <p className="qz-result-sub">
                        {result.correct_answers} / {result.total_questions} to'g'ri javob
                    </p>
                    {result.passed && activeQuiz?.points_reward > 0 && (
                        <p className="qz-result-pts"><Trophy size={16} /> +{activeQuiz.points_reward} ball</p>
                    )}
                    <div className="qz-result-actions">
                        <button className="qz-btn qz-btn--ghost" onClick={() => loadQuiz(activeQuiz.id)}>
                            Qayta urinish
                        </button>
                        <button className="qz-btn qz-btn--primary" onClick={handleBack}>
                            Ro'yxatga qaytish
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // ── PLAY SCREEN ──
    if (activeQuiz) {
        return (
            <div className="qz-root">
                <div className="qz-play-header">
                    <button className="qz-back" onClick={handleBack}><ArrowLeft size={18} /></button>
                    <div className="qz-play-title">{activeQuiz.title}</div>
                    <div className="qz-play-progress">{qIndex + 1} / {totalQuestions}</div>
                </div>
                <div className="qz-progress-bar">
                    <div className="qz-progress-fill" style={{ width: `${((qIndex + 1) / Math.max(totalQuestions, 1)) * 100}%` }} />
                </div>

                {loading && <div className="qz-state"><div className="qz-spinner" /></div>}
                {!loading && error && <div className="qz-state qz-state--error">{error}</div>}

                {!loading && !error && question && (
                    <div className="qz-question">
                        <h3 className="qz-question-text">{question.text}</h3>
                        <div className="qz-options">
                            {OPTION_KEYS.map(key => {
                                const text = question[`option_${key.toLowerCase()}`];
                                if (!text) return null;
                                const selected = answers[question.id] === key;
                                return (
                                    <button
                                        key={key}
                                        className={`qz-option ${selected ? 'is-selected' : ''}`}
                                        onClick={() => selectAnswer(key)}
                                    >
                                        <span className="qz-option-key">{key}</span>
                                        <span>{text}</span>
                                    </button>
                                );
                            })}
                        </div>
                        <button
                            className="qz-btn qz-btn--primary qz-next"
                            disabled={!answers[question.id]}
                            onClick={handleNext}
                        >
                            {isLast ? 'Yakunlash' : 'Keyingisi'}
                        </button>
                    </div>
                )}
            </div>
        );
    }

    // ── LIST SCREEN ──
    return (
        <div className="qz-root">
            <div className="qz-header">
                <span className="qz-header-icon"><HelpCircle size={20} /></span>
                <div>
                    <h2 className="qz-title">Viktorina</h2>
                    <p className="qz-subtitle">Savollarga javob bering, ball to'plang</p>
                </div>
            </div>

            {loading && <div className="qz-state"><div className="qz-spinner" /></div>}
            {!loading && error && <div className="qz-state qz-state--error">{error}</div>}
            {!loading && !error && quizzes.length === 0 && (
                <div className="qz-state">Hozircha sizga mos viktorina yo'q</div>
            )}

            {!loading && !error && quizzes.length > 0 && (
                <div className="qz-grid">
                    {quizzes.map(q => (
                        <QuizCard key={q.id} quiz={q} myResult={bestResultFor(q.id)} onStart={handleStart} />
                    ))}
                </div>
            )}
        </div>
    );
}
