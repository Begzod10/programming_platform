import './ProjectCard.css';
import { Code2, ArrowRight } from 'lucide-react';

const STATUS_META = {
    Draft:          { cls: 'draft',    ru: 'Черновик',    uz: 'Qoralama' },
    Submitted:      { cls: 'review',   ru: 'На проверке', uz: 'Tekshiruvda' },
    'Under Review': { cls: 'review',   ru: 'На проверке', uz: 'Tekshiruvda' },
    Reviewed:       { cls: 'approved', ru: 'Одобрен',     uz: 'Tasdiqlangan' },
    Approved:       { cls: 'approved', ru: 'Одобрен',     uz: 'Tasdiqlangan' },
    Rejected:       { cls: 'rejected', ru: 'Отклонён',    uz: 'Rad etilgan' },
};

const DIFF_CLS = { Easy: 'easy', Medium: 'medium', Hard: 'hard' };

// Known tech stacks get a branded accent; everything else is neutral.
const TECH_CLS = (t) => {
    const k = String(t || '').toLowerCase();
    if (/^(js|javascript)$/.test(k)) return 'tech--js';
    if (/react/.test(k)) return 'tech--react';
    if (/python/.test(k)) return 'tech--py';
    if (/css|sass|scss|tailwind/.test(k)) return 'tech--css';
    if (/html/.test(k)) return 'tech--html';
    if (/node/.test(k)) return 'tech--node';
    return '';
};

function ProjectCard({ title, status, difficulty, points, techStack, grade, githubUrl, onDetails, onViewCode, ru }) {
    const st = STATUS_META[status] || { cls: 'draft', ru: status, uz: status };
    return (
        <div className="pc-card">
            <div className="pc-glow" />
            <div className="pc-head">
                <span className={`pc-diff pc-diff--${DIFF_CLS[difficulty] || 'easy'}`}>{difficulty || 'Easy'}</span>
                <div className="pc-head-right">
                    {grade && <span className={`pc-grade pc-grade--${grade}`}>{grade}</span>}
                    <span className="pc-pts">+{points ?? 0} pts</span>
                </div>
            </div>

            <h3 className="pc-title">{title}</h3>

            <div className="pc-row">
                <div className="pc-tech">
                    {(techStack || []).slice(0, 3).map((t, i) => (
                        <span key={i} className={`pc-tag ${TECH_CLS(t)}`}>{t}</span>
                    ))}
                </div>
                <span className={`pc-status pc-status--${st.cls}`}>{ru ? st.ru : st.uz}</span>
            </div>

            <div className="pc-actions">
                <button className="pc-btn pc-btn--code" disabled={!githubUrl}
                    onClick={() => githubUrl && onViewCode?.(githubUrl)}>
                    <Code2 size={15} /> {ru ? 'Код' : 'Kod'}
                </button>
                <button className="pc-btn pc-btn--details" onClick={onDetails}>
                    {ru ? 'Детали' : 'Batafsil'} <ArrowRight size={15} />
                </button>
            </div>
        </div>
    );
}

export default ProjectCard;
