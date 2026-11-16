import React from 'react';
import * as Icons from 'lucide-react';
import { HelpCircle } from 'lucide-react';

/** An item's picture for the active games: its emoji, or (rare) the lucide
 * icon named by `icon` — same rule as MatchingActivity's ItemIcon. */
export default function ItemPic({ item, size = 32 }) {
    if (item?.emoji) return <span className="ag-pic" style={{ fontSize: size }} aria-hidden="true">{item.emoji}</span>;
    const Icon = Icons[item?.icon] || HelpCircle;
    return <Icon size={size} aria-hidden="true" />;
}
