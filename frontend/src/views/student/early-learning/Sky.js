import React from 'react';

/** Decorative sky background — sun, drifting clouds, a paper plane — shared
 * by every full-bleed screen of the kids' games (the feature has no sidebar,
 * see StudentLayout.js). Purely decorative (aria-hidden). Styles live in
 * EarlyLearning.css under .el-sky. */
export default function Sky() {
    return (
        <div className="el-sky" aria-hidden="true">
            <span className="el-sun" />
            <span className="el-cloud el-cloud-1">☁️</span>
            <span className="el-cloud el-cloud-2">☁️</span>
            <span className="el-cloud el-cloud-3">☁️</span>
            <span className="el-plane">🛩️</span>
            <span className="el-kite">🪁</span>
        </div>
    );
}
