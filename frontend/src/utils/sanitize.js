import DOMPurify from 'dompurify';

// Formatting/highlighting tags that may legitimately appear inside a code
// block. Exact lowercase only: an uppercase `<B>` or `<T>` inside code is a
// generic type parameter, not markup.
const CODE_MARKUP = new Set(['code', 'span', 'b', 'strong', 'i', 'em', 'br', 'mark', 'u', 's', 'sub', 'sup', 'small']);
const BLOCK_RE = /(<(pre|code)\b[^>]*>)([\s\S]*?)(<\/\2>)/gi;
const TAG_START_RE = /<(\/?)([A-Za-z][A-Za-z0-9-]*)/g;

/** Lesson HTML often carries code examples whose tags were never escaped
 * (`<pre><code>Har bir <input> uchun <label>…`, `Array<T>`). The browser
 * would build real elements from them — an empty input box in the middle of
 * a lesson, words that vanish. Inside every <pre>/<code> block, turn the `<`
 * of anything that is not plain formatting into `&lt;` so it shows as text. */
export const escapeCodeTags = (html) => {
    if (!html || (html.indexOf('<pre') === -1 && html.indexOf('<code') === -1
        && html.indexOf('<PRE') === -1 && html.indexOf('<CODE') === -1)) return html;
    return html.replace(BLOCK_RE, (whole, open, _name, inner, close) => (
        open + inner.replace(TAG_START_RE, (m, slash, tag) => (CODE_MARKUP.has(tag) ? m : `&lt;${slash}${tag}`)) + close
    ));
};

// Centralized HTML sanitizer for any content authored elsewhere (e.g. lesson
// sections written by teachers and stored in the DB). Always run user/teacher
// HTML through this before passing to dangerouslySetInnerHTML.
export const sanitizeHtml = (raw) => {
    if (raw === null || raw === undefined) return '';
    return DOMPurify.sanitize(escapeCodeTags(String(raw)), {
        USE_PROFILES: { html: true },
        FORBID_TAGS: ['style', 'script', 'iframe', 'object', 'embed'],
        FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus'],
    });
};
