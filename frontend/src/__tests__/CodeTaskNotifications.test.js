import { present } from '../views/student/notifications/Notifications';

jest.mock('../api/search/base', () => ({ useHttp: () => ({ request: jest.fn() }), API_URL: '/api/', headers: () => ({}), resolveImageUrl: (u) => u }));
jest.mock('../components/appheader/AppHeader', () => () => null);
jest.mock('../api/notificationsSocket', () => ({ subscribeNotifications: () => () => {} }));

const note = (o) => ({ id: 1, tone: 'wait', title: 'Bubble sort', body: null, extra: null, points: 0, ...o });

test('assigned: a new code task, in uz and ru, with the task title', () => {
    const n = note({ type: 'code_task_assigned' });
    expect(present(n, false).heading).toBe('Yangi kod vazifasi');
    expect(present(n, true).heading).toBe('Новое задание по коду');
    expect(present(n, false).text).toContain('Bubble sort');
});

test('graded: shows the points out of the maximum and the teacher note', () => {
    const n = note({ type: 'code_task_graded', tone: 'ok', points: 12, extra: '20', body: 'Barakalla' });
    expect(present(n, false).heading).toBe('Vazifa baholandi');
    expect(present(n, true).heading).toBe('Задание оценено');
    expect(present(n, false).text).toContain('12/20');
    expect(present(n, false).text).toContain('Barakalla');
});

test('returned: carries the teacher feedback', () => {
    const n = note({ type: 'code_task_returned', tone: 'bad', body: 'Funksiyaga ajrating' });
    expect(present(n, false).heading).toBe('Vazifa qaytarildi');
    expect(present(n, true).heading).toBe('Задание возвращено');
    expect(present(n, false).text).toContain('Funksiyaga ajrating');
});
