import React, { useState, useRef, useCallback, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { API_URL, useHttp, headers } from '../../../../api/search/base';
import './StudentProjectPreview.css';

/* ─────────────────────────────────────────────
   Helpers
───────────────────────────────────────────── */
const HTML_EXTS   = ['html', 'htm'];
const getExt      = (f) => (f || '').split('.').pop().toLowerCase();
const isHtml      = (f) => HTML_EXTS.includes(getExt(f));
const getFileName = (f) => f.original_name || f.filename || f.name || '';
const getCode     = (f) => f.code_content  || f.code     || f.content || '';

/* ─────────────────────────────────────────────
   Device presets
───────────────────────────────────────────── */
const DEVICES = [
    { id: 'responsive', label: 'Авто',   icon: '⬛', w: null, h: 640 },
    { id: 'desktop',    label: '1280px', icon: '🖥',  w: 1280, h: 720 },
    { id: 'laptop',     label: '1024px', icon: '💻',  w: 1024, h: 640 },
    { id: 'tablet',     label: '768px',  icon: '📱',  w: 768,  h: 600 },
    { id: 'mobile',     label: '375px',  icon: '📲',  w: 375,  h: 667 },
];

/* ═══════════════════════════════════════════════════════════
   FullscreenPreview  ─  portal-based browser modal
   Mounted via ReactDOM.createPortal → document.body
   so it never breaks parent layout (slp-lesson-hero etc.)
═══════════════════════════════════════════════════════════ */
const FullscreenPreview = ({ code, filename, onClose }) => {
    const [device,   setDevice]  = useState('responsive');
    const [customW,  setCustomW] = useState(1024);
    const [customH,  setCustomH] = useState(640);
    const [resizing, setResizing]= useState(null);
    const [full,     setFull]    = useState(false);
    const [zoom,     setZoom]    = useState(100);
    const [rKey,     setRKey]    = useState(0);
    const drag    = useRef(null);
    const stageRef= useRef(null);
    const isAuto  = device === 'responsive';

    /* ── resize drag ── */
    const startResize = useCallback((e, dir) => {
        e.preventDefault();
        setResizing(dir);
        drag.current = { x: e.clientX, y: e.clientY, w: customW, h: customH };
    }, [customW, customH]);

    useEffect(() => {
        if (!resizing) return;
        const mv = (e) => {
            const dx = e.clientX - drag.current.x;
            const dy = e.clientY - drag.current.y;
            if (resizing !== 'bottom') setCustomW(Math.max(320, Math.min(drag.current.w + dx * 2, 1800)));
            if (resizing !== 'right')  setCustomH(Math.max(240, Math.min(drag.current.h + dy,     1400)));
        };
        const up = () => setResizing(null);
        window.addEventListener('mousemove', mv);
        window.addEventListener('mouseup', up);
        return () => { window.removeEventListener('mousemove', mv); window.removeEventListener('mouseup', up); };
    }, [resizing]);

    /* ── apply device preset ── */
    useEffect(() => {
        const d = DEVICES.find(x => x.id === device);
        if (d && d.w) { setCustomW(d.w); setCustomH(d.h); }
        else if (d && !d.w && stageRef.current) {
            // responsive: use stage width
            setCustomH(d.h);
        }
    }, [device]);

    /* ── Escape ── */
    useEffect(() => {
        const h = (e) => e.key === 'Escape' && (full ? setFull(false) : onClose());
        window.addEventListener('keydown', h);
        return () => window.removeEventListener('keydown', h);
    }, [onClose, full]);

    /* ── lock body scroll while open ── */
    useEffect(() => {
        const prev = document.body.style.overflow;
        document.body.style.overflow = 'hidden';
        return () => { document.body.style.overflow = prev; };
    }, []);

    const modal = (
        <div
            className={`spp-modal-bg${full ? ' spp-modal-bg--full' : ''}`}
            onClick={e => e.target === e.currentTarget && onClose()}
        >
            <div
                className={`spp-win${full ? ' spp-win--full' : ''}`}
                onClick={e => e.stopPropagation()}
            >
                {/* ── Chrome bar ── */}
                <div className="spp-chrome">
                    <div className="spp-chrome-l">
                        <div className="spp-tl">
                            <button className="spp-tl-dot red"    onClick={onClose} title="Закрыть"/>
                            <button className="spp-tl-dot yellow" onClick={() => setZoom(z => Math.max(50, z - 10))} title="Zoom −"/>
                            <button className="spp-tl-dot green"  onClick={() => setFull(f => !f)} title="Полный экран"/>
                        </div>
                        <div className="spp-addr">
                            <svg viewBox="0 0 16 16" fill="currentColor" width="11" height="11" style={{opacity:.45, flexShrink:0}}>
                                <path d="M11 7V5a3 3 0 0 0-6 0v2H4v7h8V7h-1zM7 5a1 1 0 0 1 2 0v2H7V5z"/>
                            </svg>
                            <span>{filename}</span>
                        </div>
                    </div>
                    <div className="spp-chrome-r">
                        <div className="spp-zoom">
                            <button onClick={() => setZoom(z => Math.max(50,  z - 10))}>−</button>
                            <span>{zoom}%</span>
                            <button onClick={() => setZoom(z => Math.min(200, z + 10))}>+</button>
                        </div>
                        <button className="spp-cbtn" onClick={() => setRKey(k => k + 1)} title="Обновить">
                            <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M4 10a6 6 0 1 1 1.5 4L4 15v-4H8" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                        </button>
                        <button
                            className={`spp-cbtn spp-cbtn--full${full ? ' spp-cbtn--active' : ''}`}
                            onClick={() => setFull(f => !f)}
                            title={full ? 'Свернуть' : 'Полный экран'}
                        >
                            {full
                                ? <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2"><path d="M8 3H3v5M17 3h-5v5M3 12v5h5M12 17h5v-5" strokeLinecap="round"/></svg>
                                : <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 8V3h5M17 3h-5v5M3 12v5h5M12 12h5v5" strokeLinecap="round"/></svg>
                            }
                        </button>
                        <button className="spp-cbtn spp-cbtn--close" onClick={onClose}>
                            <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2.5">
                                <path d="M5 5l10 10M15 5L5 15" strokeLinecap="round"/>
                            </svg>
                        </button>
                    </div>
                </div>

                {/* ── Device bar ── */}
                <div className="spp-devbar">
                    <div className="spp-devtabs">
                        {DEVICES.map(d => (
                            <button
                                key={d.id}
                                className={`spp-devtab${device === d.id ? ' spp-devtab--on' : ''}`}
                                onClick={() => setDevice(d.id)}
                            >
                                <span>{d.icon}</span><span>{d.label}</span>
                            </button>
                        ))}
                    </div>
                    {!isAuto ? (
                        <div className="spp-sizeinputs">
                            <input type="number" value={customW} min={320} max={1800}
                                onChange={e => setCustomW(Math.max(320, +e.target.value))}/>
                            <span className="spp-size-sep">×</span>
                            <input type="number" value={customH} min={240} max={1400}
                                onChange={e => setCustomH(Math.max(240, +e.target.value))}/>
                            <span className="spp-px">px</span>
                        </div>
                    ) : (
                        <span className="spp-autohint">↔ Авто-ширина · тяните углы</span>
                    )}
                </div>

                {/* ── Stage ── */}
                <div className="spp-stage" ref={stageRef}>
                    <div
                        className="spp-framewrap"
                        style={{ width: isAuto ? '100%' : `${customW}px`, maxWidth: '100%' }}
                    >
                        {!isAuto && (
                            <div className="spp-vpill">
                                {customW} × {customH}
                                {resizing && <i className="spp-resdot"/>}
                            </div>
                        )}

                        <div className="spp-iframebox" style={{ height: `${customH}px` }}>
                            <div className="spp-scaler" style={{
                                transform:       `scale(${zoom / 100})`,
                                transformOrigin: 'top left',
                                width:  zoom !== 100 ? `${100 / zoom * 100}%` : '100%',
                                height: zoom !== 100 ? `${100 / zoom * 100}%` : '100%',
                            }}>
                                <iframe
                                    key={rKey}
                                    className="spp-iframe"
                                    srcDoc={code}
                                    sandbox="allow-scripts allow-same-origin"
                                    title={`preview-${filename}`}
                                />
                            </div>
                        </div>

                        {!isAuto && !full && (<>
                            <div className="spp-rh spp-rh--r" onMouseDown={e => startResize(e, 'right')}/>
                            <div className="spp-rh spp-rh--b" onMouseDown={e => startResize(e, 'bottom')}/>
                            <div className="spp-rh spp-rh--c" onMouseDown={e => startResize(e, 'corner')}>
                                <svg width="10" height="10" viewBox="0 0 10 10">
                                    <path d="M9 1L1 9M9 5L5 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                                </svg>
                            </div>
                        </>)}
                    </div>
                </div>

                {resizing && <div className="spp-shield"/>}
            </div>
        </div>
    );

    /* Portal → document.body so it never affects parent layout */
    return ReactDOM.createPortal(modal, document.body);
};

/* ═══════════════════════════════════════════════════════════
   PreviewCard  ─  inline card on lesson page
═══════════════════════════════════════════════════════════ */
const PreviewCard = ({ file }) => {
    /* FIX 1: NO auto-open on mount — user opens manually */
    const [open, setOpen] = useState(false);
    const filename = getFileName(file) || 'preview.html';
    const code     = getCode(file);

    return (
        <>
            <div className="spp-card">
                {/* browser-chrome topbar */}
                <div className="spp-card-topbar">
                    <div className="spp-card-tl-dots">
                        <span/><span/><span/>
                    </div>
                    <div className="spp-card-addr">
                        <svg viewBox="0 0 16 16" fill="currentColor" width="11" height="11" style={{opacity:.45, flexShrink:0}}>
                            <path d="M11 7V5a3 3 0 0 0-6 0v2H4v7h8V7h-1zM7 5a1 1 0 0 1 2 0v2H7V5z"/>
                        </svg>
                        <span>{filename}</span>
                    </div>
                    <button className="spp-card-fullbtn" onClick={() => setOpen(true)}>
                        <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M3 8V3h5M17 3h-5v5M3 12v5h5M12 12h5v5" strokeLinecap="round"/>
                        </svg>
                        На весь экран
                    </button>
                </div>

                {/* live preview */}
                <div className="spp-card-preview" onClick={() => setOpen(true)}>
                    <iframe
                        className="spp-card-iframe"
                        srcDoc={code}
                        sandbox="allow-scripts allow-same-origin"
                        title={`card-${filename}`}
                    />
                    <div className="spp-card-overlay">
                        <div className="spp-card-playbtn">
                            <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                                <path d="M3 8V3h5M21 3h-5v5M3 16v5h5M16 19h5v-5" strokeLinecap="round"/>
                            </svg>
                            <span>Открыть на весь экран</span>
                        </div>
                    </div>
                </div>

                {/* footer */}
                <div className="spp-card-footer">
                    <div className="spp-card-footer-l">
                        <span className="spp-card-badge">HTML</span>
                        <span className="spp-card-fname">{filename}</span>
                    </div>
                    <button className="spp-card-openbtn" onClick={() => setOpen(true)}>
                        <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M3 8V3h5M17 3h-5v5M3 12v5h5M12 12h5v5" strokeLinecap="round"/>
                        </svg>
                        Полный экран
                    </button>
                </div>
            </div>

            {/* Portal modal — outside DOM tree */}
            {open && (
                <FullscreenPreview
                    code={code}
                    filename={filename}
                    onClose={() => setOpen(false)}
                />
            )}
        </>
    );
};

/* ═══════════════════════════════════════════════════════════
   StudentProjectFiles  ─  main export
═══════════════════════════════════════════════════════════ */
const StudentProjectFiles = ({ lessonId }) => {
    const { request } = useHttp();
    const [files,   setFiles]   = useState([]);
    const [loading, setLoading] = useState(true);
    const [error,   setError]   = useState('');

    useEffect(() => {
        if (!lessonId) return;
        setLoading(true);
        setError('');
        request(`${API_URL}v1/${lessonId}/files`, 'GET', null, headers())
            .then(res => setFiles(Array.isArray(res) ? res : []))
            .catch(() => setError('Не удалось загрузить превью'))
            .finally(() => setLoading(false));
    }, [lessonId, request]);

    const htmlFiles = files.filter(f => isHtml(getFileName(f)));

    if (loading) return (
        <div className="spp-wrap">
            <div className="spp-skeleton">
                <div className="spp-sk-bar"/>
                <div className="spp-sk-body"/>
            </div>
        </div>
    );

    if (error) return (
        <div className="spp-wrap">
            <div className="spp-err">{error}</div>
        </div>
    );

    if (htmlFiles.length === 0) return null;

    return (
        <div className="spp-wrap">
            {/* header */}
            <div className="spp-hdr">
                <div className="spp-hdr-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="2" y="3" width="20" height="14" rx="2"/>
                        <path d="M8 21h8M12 17v4"/>
                    </svg>
                </div>
                <div className="spp-hdr-text">
                    <span className="spp-hdr-title">Превью проекта</span>
                    <span className="spp-hdr-sub">Воссоздайте этот сайт — нажмите для просмотра</span>
                </div>
                <div className="spp-hdr-count">
                    {htmlFiles.length} файл{htmlFiles.length === 1 ? '' : 'а'}
                </div>
            </div>

            {/* cards */}
            <div className={`spp-cards${htmlFiles.length === 1 ? ' spp-cards--one' : ''}`}>
                {htmlFiles.map((f, i) => (
                    <PreviewCard key={f.id || i} file={f}/>
                ))}
            </div>
        </div>
    );
};

export default StudentProjectFiles;