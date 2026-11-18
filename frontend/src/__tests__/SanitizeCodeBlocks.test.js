import { sanitizeHtml, escapeCodeTags } from '../utils/sanitize';

const textOf = (html) => {
    const div = document.createElement('div');
    div.innerHTML = html;
    return div;
};

test('tags written inside a code block show as text, not as elements', () => {
    const raw = '<pre><code># - Har bir <input> uchun <label> (yoki aria-label) bormi?\n# - <img>larda alt</code></pre>';
    const div = textOf(sanitizeHtml(raw));
    expect(div.querySelector('input')).toBeNull();
    expect(div.querySelector('label')).toBeNull();
    expect(div.querySelector('img')).toBeNull();
    expect(div.textContent).toContain('Har bir <input> uchun <label> (yoki aria-label) bormi?');
    expect(div.textContent).toContain('<img>larda alt');
});

test('generic types and HTML examples keep their angle brackets', () => {
    const raw = '<pre><code>function first&lt;T&gt;(a: T[]): T {}\nconst xs: Array<T> = [];\n<ul><li>bir</li></ul></code></pre>';
    const div = textOf(sanitizeHtml(raw));
    expect(div.textContent).toContain('Array<T> = [];');
    expect(div.textContent).toContain('<ul><li>bir</li></ul>');
    expect(div.textContent).toContain('first<T>(a: T[])');
    expect(div.querySelector('pre ul')).toBeNull();
});

test('highlighting and formatting tags inside code keep working', () => {
    const raw = '<pre><code><span class="kw">const</span> <b>x</b> = 1;<br></code></pre>';
    const div = textOf(sanitizeHtml(raw));
    expect(div.querySelector('pre span.kw').textContent).toBe('const');
    expect(div.querySelector('pre b').textContent).toBe('x');
});

test('inline code outside a pre block is fixed too, normal HTML is untouched', () => {
    const raw = '<p>Har bir <code><button></code> uchun matn.</p><ul><li>oddiy ro\'yxat</li></ul>';
    const div = textOf(sanitizeHtml(raw));
    expect(div.querySelector('p button')).toBeNull();
    expect(div.querySelector('p code').textContent).toBe('<button>');
    expect(div.querySelector('ul li').textContent).toBe("oddiy ro'yxat");
});

test('escapeCodeTags leaves text without code blocks unchanged', () => {
    const raw = '<h2>Sarlavha</h2><p>a &lt; b</p>';
    expect(escapeCodeTags(raw)).toBe(raw);
});
