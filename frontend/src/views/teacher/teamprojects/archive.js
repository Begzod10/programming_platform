// Teacher list: active projects and the archive (see backend services/team_project_archive.py).
// Pure helpers, kept out of TeacherTeamProjects.js so they can be unit-tested without react-router.

/** Projects that are over (`can_archive`) and not archived yet: what the bulk button moves to the archive. */
export function archivable(projects) {
    return (Array.isArray(projects) ? projects : []).filter(p => p && p.can_archive && !p.archived_at);
}

/** The projects shown under a tab: the active list or the archive. */
export function projectsForTab(active, archived, tab) {
    const list = tab === 'archive' ? archived : active;
    return Array.isArray(list) ? list : [];
}

export const bulkArchiveLabel = (count) => `Muddati o'tganlarni arxivlash (${count})`;
export const bulkArchiveConfirm = (count) => `${count} ta loyiha arxivga ko'chiriladi. Ularni keyin "Arxiv" yorlig'idan qaytarish mumkin. Davom etasizmi?`;
