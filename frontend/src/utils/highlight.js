import { sanitizeHtml } from './sanitize';

// Extracted from ExercsieFileUpload.js so bug-hunt (teacher-authored code,
// not just uploaded student files) can share the same tokenizer. The input
// is HTML-escaped before any span is injected, so this was already safe by
// construction — sanitizeHtml() is defense-in-depth, matching this
// codebase's "always sanitize before dangerouslySetInnerHTML" convention
// for any content authored outside the current request.
const RULES = {
    javascript: [
        [/(\/\/.*$)/gm, '<span class="hl-comment">$1</span>'],
        [/(\/\*[\s\S]*?\*\/)/g, '<span class="hl-comment">$1</span>'],
        [/\b(const|let|var|function|return|if|else|for|while|class|import|export|from|default|async|await|try|catch|throw|new|typeof|instanceof|of|in|switch|case|break|continue|void|null|undefined|true|false)\b/g, '<span class="hl-kw">$1</span>'],
        [/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|`(?:[^`\\]|\\.)*`)/g, '<span class="hl-str">$1</span>'],
        [/\b(\d+\.?\d*)\b/g, '<span class="hl-num">$1</span>'],
        [/\b([A-Z][a-zA-Z0-9]*)\b/g, '<span class="hl-class">$1</span>'],
    ],
    python: [
        [/(#.*$)/gm, '<span class="hl-comment">$1</span>'],
        [/("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')/g, '<span class="hl-str">$1</span>'],
        [/\b(def|class|import|from|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|lambda|yield|raise|del|and|or|not|in|is|None|True|False|async|await)\b/g, '<span class="hl-kw">$1</span>'],
        [/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, '<span class="hl-str">$1</span>'],
        [/\b(\d+\.?\d*)\b/g, '<span class="hl-num">$1</span>'],
    ],
    html: [
        [/(&lt;\/?[a-zA-Z][a-zA-Z0-9]*)/g, '<span class="hl-tag">$1</span>'],
        [/(\/?&gt;)/g, '<span class="hl-tag">$1</span>'],
        [/([a-zA-Z-]+)=/g, '<span class="hl-attr">$1</span>='],
        [/("(?:[^"\\]|\\.)*")/g, '<span class="hl-str">$1</span>'],
        [/(&lt;!--[\s\S]*?--&gt;)/g, '<span class="hl-comment">$1</span>'],
    ],
    css: [
        [/(\/\*[\s\S]*?\*\/)/g, '<span class="hl-comment">$1</span>'],
        [/([.#]?[a-zA-Z][a-zA-Z0-9-_]*)\s*\{/g, '<span class="hl-class">$1</span>{'],
        [/([a-zA-Z-]+)\s*:/g, '<span class="hl-attr">$1</span>:'],
        [/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, '<span class="hl-str">$1</span>'],
        [/\b(\d+\.?\d*(?:px|em|rem|%|vh|vw|pt|s|ms)?)\b/g, '<span class="hl-num">$1</span>'],
        [/(#[a-fA-F0-9]{3,8})\b/g, '<span class="hl-num">$1</span>'],
    ],
};

export const highlight = (code, lang) => {
    if (!code) return '';
    let escaped = code
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    const langRules = RULES[lang] || RULES.javascript;
    langRules.forEach(([pattern, replacement]) => {
        escaped = escaped.replace(pattern, replacement);
    });
    return sanitizeHtml(escaped);
};
