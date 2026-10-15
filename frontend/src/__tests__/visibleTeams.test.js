import { visibleTeams } from '../views/teacher/teamprojects/visibleTeams';

const teams = [{ id: 11, name: 'Team 1' }, { id: 12, name: 'Team 2' }, { id: 13, name: 'Team 3' }];

describe('visibleTeams', () => {
  test('shows only the selected team', () => {
    expect(visibleTeams(teams, '12')).toEqual([{ id: 12, name: 'Team 2' }]);
    expect(visibleTeams(teams, 12)).toEqual([{ id: 12, name: 'Team 2' }]);
  });

  test('shows every team when nothing is selected', () => {
    expect(visibleTeams(teams, null)).toEqual(teams);
    expect(visibleTeams(teams, '')).toEqual(teams);
    expect(visibleTeams(teams, '0')).toEqual(teams);
  });

  test('falls back to every team when the selected id no longer exists', () => {
    expect(visibleTeams(teams, '999')).toEqual(teams);
    expect(visibleTeams(teams, 'abc')).toEqual(teams);
  });

  test('tolerates a missing team list', () => {
    expect(visibleTeams(undefined, '12')).toEqual([]);
  });
});
