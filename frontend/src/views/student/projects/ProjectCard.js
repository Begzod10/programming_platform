import './ProjectCard.css';

const statusLabel = {
    Draft: 'Черновик',
    Submitted: 'Отправлен',
    'Under Review': 'На проверке',
    Approved: 'Одобрен',
    Rejected: 'Отклонён',
};

const statusClass = {
    Draft: 'status-draft',
    Submitted: 'status-pending',
    'Under Review': 'status-pending',
    Approved: 'status-approved',
    Rejected: 'status-denied',
};

const diffClass = {
    Easy: 'easy',
    Medium: 'medium',
    Hard: 'hard',
};

function ProjectCard({
    title, status, difficulty, points, techStack,
    grade, liked, likesCount, viewsCount, onDetails, onLike,
}) {
    return (
        <div className="project-card">
            <div className="project-header">
                <span className={`difficulty-badge ${diffClass[difficulty] || difficulty?.toLowerCase()}`}>
                    {difficulty}
                </span>
                <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                    {grade && <span className={`grade-badge grade-${grade}`}>{grade}</span>}
                    <span className="points-badge">+{points ?? 0} pts</span>
                </div>
            </div>

            <h3 className="project-title">{title}</h3>

            <div className="tech-stack">
                {(techStack || []).map((tech, index) => (
                    <span key={index} className="tech-tag">{tech}</span>
                ))}
            </div>

            <div className="project-meta">
                <span className="meta-item">👁️ {viewsCount ?? 0}</span>
                <span className="meta-item">❤️ {likesCount ?? 0}</span>
            </div>

            <div className="project-footer">
                <div className={`status-indicator ${statusClass[status] || 'status-draft'}`}>
                    {statusLabel[status] || status}
                </div>
                <div style={{ display: 'flex', gap: '6px' }}>
                    <button
                        className={`like-btn ${liked ? 'liked' : ''}`}
                        onClick={e => { e.stopPropagation(); onLike?.(); }}
                        disabled={liked}
                        title="Лайк"
                    >
                        {liked ? '❤️' : '🤍'}
                    </button>
                    <button className="details-btn" onClick={onDetails}>Детали</button>
                </div>
            </div>
        </div>
    );
}

export default ProjectCard;