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
        <div className="pcard-card">
            <div className="pcard-glow" />
            <div className="pcard-head">
                <span className={`pcard-diff pcard-diff--${DIFF_CLS[difficulty] || 'easy'}`}>{difficulty || 'Easy'}</span>
                <div className="pcard-head-right">
                    {grade && <span className={`pcard-grade pcard-grade--${grade}`}>{grade}</span>}
                    <span className="pcard-pts">+{points ?? 0} pts</span>
                </div>
            </div>

            <h3 className="pcard-title">{title}</h3>

            <div className="pcard-row">
                <div className="pcard-tech">
                    {(techStack || []).slice(0, 3).map((t, i) => (
                        <span key={i} className={`pcard-tag ${TECH_CLS(t)}`}>{t}</span>
                    ))}
                </div>
                <span className={`pcard-status pcard-status--${st.cls}`}>{ru ? st.ru : st.uz}</span>
            </div>

            <div className="pcard-actions">
                <button className="pcard-btn pcard-btn--code" disabled={!githubUrl}
                    onClick={() => githubUrl && onViewCode?.(githubUrl)}>
                    <Code2 size={15} /> {ru ? 'Код' : 'Kod'}
                </button>
                <button className="pcard-btn pcard-btn--details" onClick={onDetails}>
                    {ru ? 'Детали' : 'Batafsil'} <ArrowRight size={15} />
                </button>
            </div>
        </div>
    );
}

export default ProjectCard;
