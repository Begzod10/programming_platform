import { useEffect, useRef } from 'react';
import { useStore } from '../../context/StoreContext';
import './MatrixRain.css';

// Classic falling-character rain, canvas-drawn. Pointer-events: none + low
// paint opacity (via the trailing-fade fillRect's alpha, not CSS opacity —
// see the draw loop) so it reads as an ambient backdrop layered OVER the
// app rather than obscuring it, since most pages' own opaque card
// backgrounds would hide a true background-layer version almost entirely
// behind their content anyway.
const CHARS = 'アイウエオカキクケコサシスセソタチツテトナニヌネノ0123456789'.split('');
const FONT_SIZE = 16;

export default function MatrixRain() {
    const { equipped } = useStore();
    const active = !!equipped.theme?.matrixRain;
    const canvasRef = useRef(null);

    useEffect(() => {
        if (!active) return;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        let width, height, drops;

        const resize = () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
            const columns = Math.floor(width / FONT_SIZE);
            drops = new Array(columns).fill(0).map(() => Math.random() * -50);
        };
        resize();
        window.addEventListener('resize', resize);

        const draw = () => {
            // Low-alpha black wash each frame — this (not CSS opacity) is
            // what produces the fading-trail look while keeping new
            // glyphs bright.
            ctx.fillStyle = 'rgba(0, 0, 0, 0.06)';
            ctx.fillRect(0, 0, width, height);
            ctx.font = `${FONT_SIZE}px monospace`;
            ctx.fillStyle = 'rgba(0, 255, 136, 0.4)';
            for (let i = 0; i < drops.length; i++) {
                const char = CHARS[Math.floor(Math.random() * CHARS.length)];
                ctx.fillText(char, i * FONT_SIZE, drops[i] * FONT_SIZE);
                if (drops[i] * FONT_SIZE > height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        };
        const intervalId = setInterval(draw, 45);

        return () => {
            clearInterval(intervalId);
            window.removeEventListener('resize', resize);
        };
    }, [active]);

    if (!active) return null;
    return <canvas ref={canvasRef} className="matrix-rain-canvas" aria-hidden="true" />;
}
