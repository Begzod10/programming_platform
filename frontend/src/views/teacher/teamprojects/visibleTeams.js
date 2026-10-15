// Which teams the assignment page shows. Opening a team from the list puts its
// id in the URL (?team=ID) and the page then shows only that team; without the
// parameter — or if the id no longer exists — it shows every team, so a stale
// link degrades to the full list instead of an empty page.
export function visibleTeams(teams, selectedTeamId) {
    const all = Array.isArray(teams) ? teams : [];
    const id = Number(selectedTeamId);
    if (!id) return all;
    const picked = all.filter(t => t.id === id);
    return picked.length > 0 ? picked : all;
}
