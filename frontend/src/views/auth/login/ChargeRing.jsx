import { useEffect, useState } from 'react';

const TICKS = 52;

function tickState(i, litCount, error, success) {
  if (error)   return 'error';
  if (success) return 'success';
  return i < litCount ? 'lit' : 'dim';
}

export default function ChargeRing({ progress, error, success, cardRef }) {
  const [r, setR] = useState(230);

  useEffect(() => {
    if (!cardRef?.current) return;
    const ro = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect;
      setR(Math.hypot(width / 2, height / 2) + 22);
    });
    ro.observe(cardRef.current);
    return () => ro.disconnect();
  }, [cardRef]);

  const clamped  = Math.min(1, Math.max(0, progress));
  const litCount = Math.round(clamped * TICKS);

  return (
    <div className="cr-ring" aria-hidden="true">
      {Array.from({ length: TICKS }, (_, i) => {
        const deg   = (i / TICKS) * 360;
        const state = tickState(i, litCount, error, success);
        return (
          <span
            key={i}
            className={`cr-tick cr-tick--${state}`}
            style={{
              transform: `translate(-50%,-50%) rotate(${deg}deg) translateY(${-r}px)`,
            }}
          />
        );
      })}
    </div>
  );
}
