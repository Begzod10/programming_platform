import { useEffect, useState } from 'react';
import { API_URL, useHttp, headers } from '../../api/search/base';
import './StreakBadge.css';
import { Flame } from 'lucide-react';

/**
 * Sidebar flame widget showing the student's daily-activity streak.
 *
 * - Bright orange flame + count when today_active=true
 * - Dim ember + "Act today!" hint when current_streak > 0 but today_active=false
 * - Hidden entirely when current_streak === 0 (avoid demotivating new students)
 *
 * Reads from /v1/rankings/my-streak — see streak_service.bump_streak() for
 * how the counter advances.
 */
export default function StreakBadge({ collapsed = false }) {
    const { request } = useHttp();
    const [streak, setStreak] = useState(null);

    useEffect(() => {
        request(`${API_URL}v1/rankings/my-streak`, 'GET', null, headers())
            .then(setStreak)
            .catch(() => {});
    }, []);  // eslint-disable-line

    if (!streak) return null;
    const days = streak.current_streak || 0;
    if (days === 0) return null;

    const isLive = streak.today_active === true;
    const stateClass = isLive ? 'is-live' : 'is-dormant';

    if (collapsed) {
        return (
            <div
                className={`streak-badge streak-badge--mini ${stateClass}`}
                title={isLive
                    ? `${days} kunlik streak — bugun bajarildi`
                    : `${days} kunlik streak — bugun yo'qotmang!`}
            >
                <span className="streak-badge__flame" aria-hidden="true"><Flame size={18} /></span>
                <span className="streak-badge__count">{days}</span>
            </div>
        );
    }

    return (
        <div className={`streak-badge ${stateClass}`}>
            <div className="streak-badge__flame-wrap" aria-hidden="true">
                <span className="streak-badge__flame"><Flame size={18} /></span>
                {!isLive && <span className="streak-badge__alert">!</span>}
            </div>
            <div className="streak-badge__body">
                <div className="streak-badge__count-row">
                    <span className="streak-badge__count">{days}</span>
                    <span className="streak-badge__unit">
                        {days === 1 ? 'kun' : 'kun'} streak
                    </span>
                </div>
                <div className="streak-badge__sub">
                    {isLive
                        ? 'Bugungi mashqlar bajarildi'
                        : 'Bugun yo\'qotmang!'}
                </div>
            </div>
        </div>
    );
}
