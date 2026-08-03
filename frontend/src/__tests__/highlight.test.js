/**
 * Regression test for a real production bug: sequential regex passes on a
 * single growing HTML string let a later rule re-match text INSIDE a span
 * an earlier rule just inserted -- e.g. the string-highlighting rule
 * matching the literal "hl-kw" inside class="hl-kw" from the keyword rule.
 * That produced invalid nested markup (<span class=<span ...>"hl-kw"</span>>)
 * which browsers render as visible garbage text in the bug-hunt code view.
 */
import { highlight } from '../utils/highlight';

describe('highlight', () => {
  test('python keyword highlighting does not corrupt the injected span', () => {
    const result = highlight('class Inson:', 'python');
    expect(result).toBe('<span class="hl-kw">class</span> Inson:');
  });

  test('python def keyword next to a string does not cross-contaminate spans', () => {
    const result = highlight('def __init__(self, ism, yosh):', 'python');
    expect(result).toBe('<span class="hl-kw">def</span> __init__(self, ism, yosh):');
  });

  test('a real string literal is still highlighted as a string, not swallowed', () => {
    const result = highlight('return "hello"', 'python');
    expect(result).toContain('<span class="hl-str">"hello"</span>');
    expect(result).toContain('<span class="hl-kw">return</span>');
  });

  test('javascript keyword + string on the same line stays well-formed', () => {
    const result = highlight('const x = "test";', 'javascript');
    expect(result).not.toMatch(/<span class=<span/);
  });

  test('css class selector highlighting stays well-formed', () => {
    const result = highlight('.card { color: red; }', 'css');
    expect(result).not.toMatch(/<span class=<span/);
  });
});
