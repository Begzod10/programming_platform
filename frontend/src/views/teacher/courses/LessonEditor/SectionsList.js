import React, { useState, useRef } from 'react';
import { SectionBlock } from './SectionBlock';

/* ─────────────────────────────────────────────
   DRAG-AND-DROP SORTABLE SECTIONS LIST
───────────────────────────────────────────── */
export const SectionsList = ({ sections, onReorder, onUpdate, onDelete, onMoveUp, onMoveDown, lessonId, apiBaseUrl }) => {
    const dragIdx = useRef(null);
    const [dragOver, setDragOver] = useState(null);

    const handleDragStart = (i) => { dragIdx.current = i; };
    const handleDragOver = (e, i) => { e.preventDefault(); setDragOver(i); };
    const handleDrop = (e, i) => {
        e.preventDefault();
        if (dragIdx.current === null || dragIdx.current === i) { setDragOver(null); return; }
        const list = [...sections];
        const [moved] = list.splice(dragIdx.current, 1);
        list.splice(i, 0, moved);
        onReorder(list);
        dragIdx.current = null;
        setDragOver(null);
    };
    const handleDragEnd = () => { dragIdx.current = null; setDragOver(null); };

    return (
        <div className="lep-sections-list">
            {sections.map((s, i) => (
                <div key={s.id}
                     className={`lep-section-wrapper${dragOver === i ? ' lep-section-wrapper--over' : ''}`}
                     onDragOver={e => handleDragOver(e, i)}
                     onDrop={e => handleDrop(e, i)}>
                    <SectionBlock
                        section={s} index={i} total={sections.length}
                        onUpdate={data => onUpdate(s.id, data)}
                        onDelete={() => onDelete(s.id)}
                        onMoveUp={() => onMoveUp(i)}
                        onMoveDown={() => onMoveDown(i)}
                        lessonId={lessonId}
                        apiBaseUrl={apiBaseUrl}
                        dragHandleProps={{
                            draggable: true,
                            onDragStart: () => handleDragStart(i),
                            onDragEnd: handleDragEnd,
                        }}
                    />
                </div>
            ))}
        </div>
    );
};
