import { useState, useEffect } from 'react';
import { listMyGroups } from './pcApi';

// The teacher's own groups; degrades to [] when the call fails.
export default function useMyGroups(request) {
    const [groups, setGroups] = useState([]);
    useEffect(() => {
        let alive = true;
        listMyGroups(request)
            .then(g => { if (alive) setGroups(Array.isArray(g) ? g : []); })
            .catch(() => { /* picker degrades to empty */ });
        return () => { alive = false; };
    }, [request]);
    return groups;
}
