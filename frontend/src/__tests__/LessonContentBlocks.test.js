/**
 * Regression test for a real stored-XSS bug: the student-facing lesson
 * render path (LessonContentBlocks.js) injects section.html via
 * dangerouslySetInnerHTML with no sanitization. The teacher-authoring side
 * (views/teacher/courses/LessonPage/LessonPage.js) already runs the exact
 * same section.html through sanitizeHtml() before rendering it back to the
 * teacher who wrote it — the student path had silently lost that same fix
 * after a refactor split lesson rendering into LessonContentBlocks.js.
 */
import React from 'react';
import { render } from '@testing-library/react';
import { LessonContentBlocks } from '../views/student/courses/LessonPage/LessonContentBlocks';

const baseProjectStatus = {
  done: false,
  pending: false,
  failed: false,
  score: null,
  section: null,
  loading: false,
  submission: null,
  passThreshold: 75,
  quotaExhausted: false,
  quotaMessage: '',
};

const renderBlocks = (html) => {
  const lesson = {
    sections: [
      { id: 'sec-1', type: 'text', label: 'Test section', html },
    ],
  };

  window.__xss = undefined;

  return render(
    <LessonContentBlocks
      lesson={lesson}
      course={{ id: 1 }}
      activeSection="sec-1"
      setActiveSection={() => {}}
      exerciseSubmissions={{}}
      submissionsReady
      copiedId={null}
      copyCode={() => {}}
      downloadingFile={null}
      handleDownloadFile={() => {}}
      fileDownloadError={null}
      recordVideoWatch={() => {}}
      projectStatus={baseProjectStatus}
      onProjectOpen={() => {}}
    />
  );
};

describe('LessonContentBlocks XSS sanitization', () => {
  test('an onerror payload in section.html never reaches the DOM', () => {
    const { container } = renderBlocks('<img src=x onerror="window.__xss=1">');

    expect(container.querySelector('img[onerror]')).toBeNull();
    expect(window.__xss).toBeUndefined();
  });

  test('a script tag in section.html is stripped, not executed', () => {
    const { container } = renderBlocks('<p>hello</p><script>window.__xss=1</script>');

    expect(container.querySelector('script')).toBeNull();
    expect(window.__xss).toBeUndefined();
    expect(container.textContent).toContain('hello');
  });

  test('safe formatting HTML still renders normally', () => {
    const { container } = renderBlocks('<p>Salom, <strong>dunyo</strong>!</p>');

    expect(container.querySelector('strong')).not.toBeNull();
    expect(container.textContent).toContain('Salom,');
  });
});
