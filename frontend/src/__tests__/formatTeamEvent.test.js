import { formatTeamEvent } from '../views/teacher/teamprojects/formatTeamEvent';

describe('formatTeamEvent', () => {
  test('team_formed has no payload-driven detail', () => {
    expect(formatTeamEvent({ event_type: 'team_formed', payload: {} }))
      .toEqual({ label: 'Jamoa tuzildi', detail: '' });
  });

  test('plan_generated includes task count and provider', () => {
    expect(formatTeamEvent({ event_type: 'plan_generated', payload: { task_count: 3, provider: 'openai' } }))
      .toEqual({ label: 'AI reja yaratdi', detail: '3 ta vazifa (openai)' });
  });

  test('plan_generation_failed surfaces the error text', () => {
    expect(formatTeamEvent({ event_type: 'plan_generation_failed', payload: { error: 'timeout' } }))
      .toEqual({ label: "AI reja yarata olmadi", detail: 'timeout' });
  });

  test('task_reassigned includes the task id', () => {
    expect(formatTeamEvent({ event_type: 'task_reassigned', payload: { task_id: 7, to_student_id: 12 } }))
      .toEqual({ label: 'Vazifa qayta tayinlandi', detail: 'Vazifa #7' });
  });

  test('points_awarded includes the grade', () => {
    expect(formatTeamEvent({ event_type: 'points_awarded', payload: { grade: 'B' } }))
      .toEqual({ label: 'Ballar berildi', detail: 'Baho: B' });
  });

  test('task_reviewed shows score and approved/rejected wording', () => {
    expect(formatTeamEvent({ event_type: 'task_reviewed', payload: { score: 85, approved: true } }))
      .toEqual({ label: 'Vazifa AI tomonidan tekshirildi', detail: '85/100 — tasdiqlandi' });
    expect(formatTeamEvent({ event_type: 'task_reviewed', payload: { score: 40, approved: false } }))
      .toEqual({ label: 'Vazifa AI tomonidan tekshirildi', detail: '40/100 — rad etildi' });
  });

  test('unknown event_type falls back to the raw type as the label', () => {
    expect(formatTeamEvent({ event_type: 'some_future_event', payload: {} }))
      .toEqual({ label: 'some_future_event', detail: '' });
  });

  test('missing payload does not throw', () => {
    expect(() => formatTeamEvent({ event_type: 'team_finalized' })).not.toThrow();
  });
});
