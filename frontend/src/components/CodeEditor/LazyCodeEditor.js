import React, { Suspense } from 'react';
import { useTranslation } from '../../i18n/useTranslation';

const CodeEditor = React.lazy(() => import('./CodeEditor'));

/** Same props as CodeEditor; the editor (and CodeMirror with it) is fetched only when a page needs it,
 *  so the rest of the site does not pay for it. */
export default function LazyCodeEditor(props) {
    const { lang } = useTranslation();
    return (
        <Suspense fallback={<div className="code-editor-loading" role="status">
            {lang === 'uz' ? 'Muharrir yuklanmoqda…' : 'Редактор загружается…'}</div>}>
            <CodeEditor {...props} />
        </Suspense>
    );
}
