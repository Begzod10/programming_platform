import { useEffect, useState } from 'react';
import { History, Trophy, X } from 'lucide-react';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import './TeamProjectHistory.css';

const MEDAL = { 1: '🥇', 2: '🥈', 3: '🥉' };

const STATUS_LABEL = (ru) => ({
    forming: ru ? 'Формируется' : 'Shakllanmoqda',
    working: ru ? 'В работе' : 'Ishlayapti',
    integrating: ru ? 'Сборка' : 'Birlashtirilmoqda',
    submitted: ru ? 'Сдан' : 'Topshirilgan',
    reviewed: ru ? 'Проверен' : 'Baholangan',
});

const fmtDate = (iso, ru) => {
    try { return new Date(iso).toLocaleDateString(ru ? 'ru-RU' : 'uz-UZ', { day: 'numeric', month: 'long', year: 'numeric' }); }
    catch { return ''; }
};

function PlaceBadge({ place, ru }) {
    if (!place) return <span className="tph-place tph-place--none">{ru ? 'Без места' : "O'rinsiz"}</span>;
    return <span className={`tph-place tph-place--${Math.min(place, 4)}`}>{MEDAL[place] || place}{ru ? ' место' : "-o'rin"}</span>;
}

function ProjectCard({ project, ru }) {
    const mine = project.teams.find(t => t.is_mine);
    return (
        <article className="tph-card">
            <header className="tph-card-head">
                <div>
                    <h3>{project.title}</h3>
                    <p>{fmtDate(project.created_at, ru)} · {project.total_teams} {ru ? 'команд' : 'jamoa'}</p>
                </div>
                {mine && <PlaceBadge place={mine.place} ru={ru} />}
            </header>

            {mine && (
                <div className="tph-mine">
                    <strong>{mine.name}</strong>
                    <p>{ru ? mine.summary_ru : mine.summary}</p>
                    {mine.members.length > 0 && <p className="tph-members">{mine.members.join(' · ')}</p>}
                </div>
            )}

            <div className="tph-table" role="table" aria-label={ru ? 'Итоги команд' : 'Jamoalar natijalari'}>
                {project.teams.map(t => (
                    <div key={t.team_id} role="row" className={`tph-row${t.is_mine ? ' tph-row--mine' : ''}`}>
                        <span className="tph-row-place"><PlaceBadge place={t.place} ru={ru} /></span>
                        <span className="tph-row-name">{t.name}{t.is_mine ? (ru ? ' (вы)' : ' (siz)') : ''}</span>
                        <span className="tph-row-meta">
                            {t.approved_tasks}/{t.total_tasks} {ru ? 'заданий' : 'vazifa'}
                            {t.avg_score != null ? ` · ${t.avg_score}` : ''}
                            {t.final_grade ? ` · ${t.final_grade}` : ''}
                        </span>
                        <span className="tph-row-status">{STATUS_LABEL(ru)[t.status] || t.status}</span>
                    </div>
                ))}
            </div>
            {project.finished_teams < project.total_teams && (
                <p className="tph-note">
                    {ru
                        ? 'Место получают только команды, сдавшие итоговый проект.'
                        : "O'rin faqat yakuniy loyihani topshirgan jamoalarga beriladi."}
                </p>
            )}
        </article>
    );
}

/** Icon button + slide-over panel listing every team project the student took part in. */
export default function TeamProjectHistory({ ru }) {
    const { request } = useHttp();
    const [open, setOpen] = useState(false);
    const [state, setState] = useState({ loading: false, error: null, items: null });

    useEffect(() => {
        if (!open || state.items) return undefined;
        let cancelled = false;
        setState({ loading: true, error: null, items: null });
        (async () => {
            try {
                const data = await request(`${API_URL}v1/team-projects/my/history`, 'GET', null, headers());
                if (!cancelled) setState({ loading: false, error: null, items: Array.isArray(data) ? data : [] });
            } catch (e) {
                if (!cancelled) setState({
                    loading: false, items: null,
                    error: e?.response?.data?.detail || (ru ? 'Не удалось загрузить итоги.' : "Natijalarni yuklab bo'lmadi."),
                });
            }
        })();
        return () => { cancelled = true; };
    }, [open, request, ru, state.items]);

    const label = ru ? 'Итоги и архив проектов' : 'Natijalar va loyihalar arxivi';
    return (
        <>
            <button type="button" className="tph-open" onClick={() => setOpen(true)} aria-label={label} title={label}>
                <History size={18} />
                <span>{ru ? 'Итоги' : 'Natijalar'}</span>
            </button>

            {open && (
                <div className="tph-overlay" onClick={() => setOpen(false)}>
                    <aside className="tph-panel" role="dialog" aria-modal="true" aria-label={label} onClick={e => e.stopPropagation()}>
                        <header className="tph-panel-head">
                            <h2><Trophy size={18} /> {label}</h2>
                            <button type="button" className="tph-close" onClick={() => setOpen(false)} aria-label={ru ? 'Закрыть' : 'Yopish'}>
                                <X size={18} />
                            </button>
                        </header>
                        <div className="tph-body">
                            {state.loading && <p className="tph-muted">{ru ? 'Загрузка…' : 'Yuklanmoqda…'}</p>}
                            {state.error && <p className="tph-error" role="alert">{state.error}</p>}
                            {state.items && state.items.length === 0 && (
                                <p className="tph-muted">{ru ? 'Пока нет командных проектов.' : "Hozircha jamoaviy loyihalar yo'q."}</p>
                            )}
                            {state.items && state.items.map(p => <ProjectCard key={p.team_project_id} project={p} ru={ru} />)}
                        </div>
                    </aside>
                </div>
            )}
        </>
    );
}
