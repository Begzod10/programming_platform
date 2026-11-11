import React from 'react';
import { Star } from 'lucide-react';

/** Three-star row for one activity's best score — filled up to `stars`. */
export default function StarRow({ stars, size = 16 }) {
    return (
        <span className="el-star-row">
            {[0, 1, 2].map((i) => (
                <Star key={i} size={size} fill={i < stars ? 'currentColor' : 'none'} className={i < stars ? 'el-star-filled' : 'el-star-empty'} />
            ))}
        </span>
    );
}
