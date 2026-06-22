import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import './CelebrationOverlay.css';
import { Trophy } from 'lucide-react';

// 40 confetti pieces with randomised colour / position / delay / duration
const COLORS = ['#7c3aed','#10b981','#f59e0b','#ef4444','#3b82f6','#ec4899','#14b8a6'];
const PIECES = Array.from({ length: 40 }, (_, i) => ({
    id: i,
    color:    COLORS[i % COLORS.length],
    left:     Math.random() * 100,
    delay:    Math.random() * 0.8,
    duration: 2.4 + Math.random() * 1.4,
    size:     7 + Math.random() * 8,
    rotate:   Math.random() * 720,
    shape:    i % 3 === 0 ? 'circle' : i % 3 === 1 ? 'square' : 'rect',
}));

const CelebrationOverlay = ({ score, onDone }) => {
    const [visible, setVisible] = useState(true);

    useEffect(() => {
        const t = setTimeout(() => {
            setVisible(false);
            setTimeout(onDone, 400); // wait for fade-out
        }, 3800);
        return () => clearTimeout(t);
    }, [onDone]);

    const messages = score >= 90
        ? ['Mukammal!', '🌟 Ajoyib natija!']
        : score >= 75
        ? ['Barakalla!', '🎉 Loyiha qabul qilindi!']
        : ['Zo\'r!', '✅ Qabul qilindi!'];

    return ReactDOM.createPortal(
        <div className={`cel-overlay ${visible ? 'cel-visible' : 'cel-hidden'}`}
             onClick={() => { setVisible(false); setTimeout(onDone, 400); }}>

            {/* Confetti */}
            {PIECES.map(p => (
                <span
                    key={p.id}
                    className={`cel-piece cel-${p.shape}`}
                    style={{
                        left:            `${p.left}%`,
                        background:      p.color,
                        width:           `${p.size}px`,
                        height:          p.shape === 'rect' ? `${p.size * 2.2}px` : `${p.size}px`,
                        animationDelay:  `${p.delay}s`,
                        animationDuration:`${p.duration}s`,
                        '--rotate':      `${p.rotate}deg`,
                    }}
                />
            ))}

            {/* Card */}
            <div className="cel-card" onClick={e => e.stopPropagation()}>
                <div className="cel-trophy" aria-hidden="true"><Trophy size={48} /></div>
                <div className="cel-score">{score}<span>/100</span></div>
                <div className="cel-headline">{messages[0]}</div>
                <div className="cel-sub">{messages[1]}</div>
                <button className="cel-btn" onClick={() => { setVisible(false); setTimeout(onDone, 400); }}>
                    Davom etish →
                </button>
            </div>
        </div>,
        document.body
    );
};

export default CelebrationOverlay;
