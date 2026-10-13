import { archivable, projectsForTab, bulkArchiveLabel, bulkArchiveConfirm } from '../views/teacher/teamprojects/archive';

const p = (id, extra = {}) => ({ id, can_archive: false, archived_at: null, ...extra });

describe('archivable', () => {
  test('keeps only finished, not yet archived projects', () => {
    const list = [p(1, { can_archive: true }), p(2), p(3, { can_archive: true, archived_at: '2026-10-13T10:00:00Z' })];
    expect(archivable(list).map(x => x.id)).toEqual([1]);
  });

  test('is safe on missing or malformed data', () => {
    expect(archivable(undefined)).toEqual([]);
    expect(archivable(null)).toEqual([]);
    expect(archivable([null, undefined, p(5, { can_archive: true })]).map(x => x.id)).toEqual([5]);
  });
});

describe('projectsForTab', () => {
  const active = [p(1), p(2)];
  const archived = [p(3, { archived_at: 'x' })];

  test('the active tab shows the active list, the archive tab the archived one', () => {
    expect(projectsForTab(active, archived, 'active')).toBe(active);
    expect(projectsForTab(active, archived, 'archive')).toBe(archived);
  });

  test('an unknown tab falls back to the active list and bad data to an empty list', () => {
    expect(projectsForTab(active, archived, 'nope')).toBe(active);
    expect(projectsForTab(undefined, undefined, 'archive')).toEqual([]);
  });
});

describe('texts', () => {
  test('the bulk button and its confirmation carry the number', () => {
    expect(bulkArchiveLabel(3)).toBe("Muddati o'tganlarni arxivlash (3)");
    expect(bulkArchiveConfirm(3)).toContain('3 ta loyiha');
    expect(bulkArchiveConfirm(3)).toContain('Arxiv');
  });
});
