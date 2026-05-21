import DOMPurify from 'dompurify';

// Centralized HTML sanitizer for any content authored elsewhere (e.g. lesson
// sections written by teachers and stored in the DB). Always run user/teacher
// HTML through this before passing to dangerouslySetInnerHTML.
export const sanitizeHtml = (raw) => {
    if (raw === null || raw === undefined) return '';
    return DOMPurify.sanitize(String(raw), {
        USE_PROFILES: { html: true },
        FORBID_TAGS: ['style', 'script', 'iframe', 'object', 'embed'],
        FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus'],
    });
};
