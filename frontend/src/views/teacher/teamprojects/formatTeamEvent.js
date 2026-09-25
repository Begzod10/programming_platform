// Human-readable label + detail line for one TeamProjectEvent row (see GET
// /teams/{team_id}/events). event_type -> label mirrors every write site in
// the backend (team_project_service.py, team_project_planner.py,
// team_project_task_review.py, team_project.py) — add an entry here
// whenever a new event_type is introduced there.
//
// Extracted into its own module (not defined inline in
// TeacherTeamProjectDetail.js, which imports react-router-dom v7 — ESM-only,
// unresolvable by this project's CRA/Jest CommonJS config) so it can be
// unit-tested directly, same reasoning as isStuckWithNoManualPlan.js.
const EVENT_LABELS = {
    team_formed: 'Jamoa tuzildi',
    plan_generated: 'AI reja yaratdi',
    plan_generation_failed: "AI reja yarata olmadi",
    plan_created_manually: "O'qituvchi qo'lda reja tuzdi",
    task_reassigned: 'Vazifa qayta tayinlandi',
    team_finalized: 'Jamoa loyihani yakunladi',
    points_awarded: 'Ballar berildi',
    task_reviewed: 'Vazifa AI tomonidan tekshirildi',
};

export function formatTeamEvent(event) {
    const label = EVENT_LABELS[event.event_type] || event.event_type;
    const p = event.payload || {};
    let detail = '';

    switch (event.event_type) {
        case 'plan_generated':
            detail = `${p.task_count ?? '?'} ta vazifa${p.provider ? ` (${p.provider})` : ''}`;
            break;
        case 'plan_generation_failed':
            detail = p.error || '';
            break;
        case 'plan_created_manually':
            detail = `${p.task_count ?? '?'} ta vazifa`;
            break;
        case 'task_reassigned':
            detail = `Vazifa #${p.task_id ?? '?'}`;
            break;
        case 'points_awarded':
            detail = p.grade ? `Baho: ${p.grade}` : '';
            break;
        case 'task_reviewed':
            detail = `${p.score ?? '?'}/100 — ${p.approved ? 'tasdiqlandi' : 'rad etildi'}`;
            break;
        default:
            detail = '';
    }

    return { label, detail };
}
