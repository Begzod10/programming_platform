import React, { useState, useEffect, useRef } from 'react';
import { Code2, Eye, ChevronDown, ChevronUp } from 'lucide-react';
import { API_URL } from '../../../../api/search/base';
import './SampleProject.css';

const TABS = [
    { key: 'html', label: 'HTML' },
    { key: 'css',  label: 'CSS'  },
    { key: 'js',   label: 'JS'   },
];

const SampleProject = ({ lessonId }) => {
    const [sample,  setSample]  = useState(null);
    const [loading, setLoading] = useState(true);
    const [tab,     setTab]     = useState('html');
    const [open,    setOpen]    = useState(false);
    const iframeRef             = useRef(null);

    useEffect(() => {
        if (!lessonId) return;
        fetch(`${API_URL}v1/lessons/${lessonId}/sample`)
            .then(r => r.ok ? r.json() : null)
            .then(data => { setSample(data); setLoading(false); })
            .catch(() => setLoading(false));
    }, [lessonId]);

    useEffect(() => {
        if (!sample) return;
        if (sample.html_code) setTab('html');
        else if (sample.css_code) setTab('css');
        else if (sample.js_code) setTab('js');
    }, [sample]);

    if (loading || !sample) return null;

    const visibleTabs = TABS.filter(t => sample[`${t.key}_code`]);
    const code   = sample[`${tab}_code`] || '';
    const srcdoc = `<!DOCTYPE html><html><head><style>${sample.css_code || ''}</style></head><body>${sample.html_code || ''}<script>${sample.js_code || ''}<\/script></body></html>`;

    return (
        <div className="sp-wrap">
            <button className="sp-toggle" onClick={() => setOpen(o => !o)}>
                <Code2 size={16} />
                <span>Namuna loyiha: {sample.title}</span>
                {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>

            {open && (
                <div className="sp-body">
                    {sample.description && <p className="sp-desc">{sample.description}</p>}

                    <div className="sp-panes">
                        <div className="sp-preview">
                            <div className="sp-pane-hd"><Eye size={13} /> Ko'rinish</div>
                            <iframe
                                ref={iframeRef}
                                className="sp-iframe"
                                srcDoc={srcdoc}
                                sandbox="allow-scripts"
                                title="sample-preview"
                            />
                        </div>

                        <div className="sp-code-panel">
                            <div className="sp-tabs">
                                {visibleTabs.map(t => (
                                    <button
                                        key={t.key}
                                        className={`sp-tab ${tab === t.key ? 'active' : ''}`}
                                        onClick={() => setTab(t.key)}
                                    >
                                        {t.label}
                                    </button>
                                ))}
                            </div>
                            <pre className="sp-pre"><code>{code}</code></pre>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SampleProject;
