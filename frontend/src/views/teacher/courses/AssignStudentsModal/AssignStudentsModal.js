import React, { useCallback, useEffect, useMemo, useState } from 'react';
import ReactDOM from 'react-dom';
import { API_URL, useHttp, headers } from '../../../../api/search/base';
import './AssignStudentsModal.css';

/* Tiny debounce — local, avoids pulling in a util module. */
const useDebounced = (value, ms) => {
    const [v, setV] = useState(value);
    useEffect(() => {
        const t = setTimeout(() => setV(value), ms);
        return () => clearTimeout(t);
    }, [value, ms]);
    return v;
};

const AssignStudentsModal = ({ course, onClose, onChanged }) => {
    const { request } = useHttp();

    const [groups, setGroups]               = useState([]);
    const [groupId, setGroupId]             = useState('all');
    const [search, setSearch]               = useState('');
    const [onlyEnrolled, setOnlyEnrolled]   = useState(false);
    const [students, setStudents]           = useState([]);
    const [enrolledCount, setEnrolledCount] = useState(0);
    const [selected, setSelected]           = useState(() => new Set());
    const [loading, setLoading]             = useState(false);
    const [busy, setBusy]                   = useState(false);
    const [error, setError]                 = useState(null);

    const debouncedSearch = useDebounced(search, 250);

    /* ── load teacher's groups once ── */
    useEffect(() => {
        let cancelled = false;
        request(`${API_URL}v1/groups/`, 'GET', null, headers())
            .then((data) => {
                if (cancelled) return;
                setGroups(Array.isArray(data) ? data : []);
            })
            .catch(() => { /* groups are optional context */ });
        return () => { cancelled = true; };
    }, [request]);

    /* ── load student roster for this course ── */
    const reload = useCallback(async () => {
        if (!course?.id) return;
        setLoading(true);
        setError(null);
        try {
            const params = new URLSearchParams();
            if (groupId !== 'all') params.set('group_id', groupId);
            if (onlyEnrolled)      params.set('only_enrolled', 'true');
            if (debouncedSearch)   params.set('search', debouncedSearch);
            params.set('limit', '500');
            const url = `${API_URL}v1/teacher/courses/${course.id}/students?${params.toString()}`;
            const data = await request(url, 'GET', null, headers());
            setStudents(Array.isArray(data?.items) ? data.items : []);
            setEnrolledCount(data?.enrolled_count ?? 0);
            setSelected(new Set());
        } catch (e) {
            setError("Ro'yxatni yuklab bo'lmadi");
        } finally {
            setLoading(false);
        }
    }, [course?.id, groupId, onlyEnrolled, debouncedSearch, request]);

    useEffect(() => { reload(); }, [reload]);

    /* ── selection helpers ── */
    const visibleNotEnrolled = useMemo(
        () => students.filter(s => !s.is_enrolled).map(s => s.id),
        [students],
    );
    const visibleEnrolled = useMemo(
        () => students.filter(s => s.is_enrolled).map(s => s.id),
        [students],
    );

    const toggleOne = (id) => {
        setSelected(prev => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id); else next.add(id);
            return next;
        });
    };

    const selectAllUnenrolled = () => {
        setSelected(new Set(visibleNotEnrolled));
    };
    const clearSelection = () => setSelected(new Set());

    /* ── mutations ── */
    const assign = async ({ studentIds = [], wholeGroup = false } = {}) => {
        const body = {
            student_ids: studentIds,
            group_ids: wholeGroup && groupId !== 'all' ? [Number(groupId)] : [],
        };
        if (!body.student_ids.length && !body.group_ids.length) return;

        setBusy(true);
        try {
            await request(
                `${API_URL}v1/teacher/courses/${course.id}/students`,
                'POST', JSON.stringify(body), headers(),
            );
            await reload();
            onChanged?.();
        } catch (e) {
            setError("Qo'shib bo'lmadi");
        } finally {
            setBusy(false);
        }
    };

    const unassignOne = async (studentId) => {
        setBusy(true);
        try {
            await request(
                `${API_URL}v1/teacher/courses/${course.id}/students/${studentId}`,
                'DELETE', null, headers(),
            );
            await reload();
            onChanged?.();
        } catch (e) {
            setError("Bekor qilib bo'lmadi");
        } finally {
            setBusy(false);
        }
    };

    const selectedNotEnrolled = [...selected].filter(id => visibleNotEnrolled.includes(id));
    const canBulkAssign = selectedNotEnrolled.length > 0 && !busy;
    const canAssignGroup = groupId !== 'all' && !busy;

    return ReactDOM.createPortal(
        <div className="asm-overlay" onClick={onClose}>
            <div className="asm-modal" onClick={e => e.stopPropagation()}>
                <header className="asm-head">
                    <div>
                        <h3>👥 Talabalarni boshqarish</h3>
                        <p className="asm-sub">{course?.title}</p>
                    </div>
                    <button className="asm-close" onClick={onClose} aria-label="Yopish">✕</button>
                </header>

                <div className="asm-stats">
                    <span className="asm-badge asm-badge--green">
                        {enrolledCount} ta talaba kursga ulangan
                    </span>
                    {loading && <span className="asm-muted">yuklanmoqda…</span>}
                </div>

                <div className="asm-toolbar">
                    <select
                        className="asm-select"
                        value={groupId}
                        onChange={e => setGroupId(e.target.value)}
                    >
                        <option value="all">Barcha guruhlar</option>
                        {groups.map(g => (
                            <option key={g.id} value={g.id}>{g.name}</option>
                        ))}
                    </select>

                    <input
                        className="asm-search"
                        placeholder="Ism / username / email bo'yicha qidirish…"
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                    />

                    <label className="asm-check">
                        <input
                            type="checkbox"
                            checked={onlyEnrolled}
                            onChange={e => setOnlyEnrolled(e.target.checked)}
                        />
                        <span>Faqat ulanganlar</span>
                    </label>
                </div>

                <div className="asm-actions">
                    <button
                        className="asm-btn asm-btn--ghost"
                        onClick={selectAllUnenrolled}
                        disabled={!visibleNotEnrolled.length || busy}
                    >
                        Ulanmaganlarni belgilash ({visibleNotEnrolled.length})
                    </button>
                    <button
                        className="asm-btn asm-btn--ghost"
                        onClick={clearSelection}
                        disabled={!selected.size || busy}
                    >
                        Tozalash
                    </button>
                    <span className="asm-spacer" />
                    <button
                        className="asm-btn asm-btn--primary"
                        onClick={() => assign({ studentIds: selectedNotEnrolled })}
                        disabled={!canBulkAssign}
                    >
                        ➕ Belgilanganlarni ulash ({selectedNotEnrolled.length})
                    </button>
                    <button
                        className="asm-btn asm-btn--accent"
                        onClick={() => assign({ wholeGroup: true })}
                        disabled={!canAssignGroup}
                        title={groupId === 'all' ? 'Avval guruhni tanlang' : ''}
                    >
                        Butun guruhni ulash
                    </button>
                </div>

                {error && <div className="asm-error">{error}</div>}

                <div className="asm-list">
                    {!loading && students.length === 0 && (
                        <div className="asm-empty">Bu filtr bilan talabalar topilmadi.</div>
                    )}
                    {students.map(s => {
                        const checked = selected.has(s.id);
                        return (
                            <div
                                key={s.id}
                                className={`asm-row${s.is_enrolled ? ' asm-row--on' : ''}`}
                            >
                                <input
                                    type="checkbox"
                                    className="asm-row-check"
                                    checked={checked}
                                    onChange={() => toggleOne(s.id)}
                                    disabled={s.is_enrolled}
                                    title={s.is_enrolled ? 'Allaqachon ulangan' : 'Tanlash'}
                                />
                                <div className="asm-row-name">
                                    <strong>{s.full_name || s.username || `#${s.id}`}</strong>
                                    <span className="asm-row-meta">
                                        {s.email || s.username}
                                        {s.groups?.length > 0 && (
                                            <> · {s.groups.map(g => g.name).join(', ')}</>
                                        )}
                                    </span>
                                </div>
                                <div className="asm-row-tail">
                                    {s.is_enrolled ? (
                                        <button
                                            className="asm-btn asm-btn--danger asm-btn--sm"
                                            onClick={() => unassignOne(s.id)}
                                            disabled={busy}
                                        >
                                            Olib tashlash
                                        </button>
                                    ) : (
                                        <button
                                            className="asm-btn asm-btn--primary asm-btn--sm"
                                            onClick={() => assign({ studentIds: [s.id] })}
                                            disabled={busy}
                                        >
                                            Ulash
                                        </button>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>

                <footer className="asm-foot">
                    <button className="asm-btn asm-btn--ghost" onClick={onClose}>Yopish</button>
                </footer>
            </div>
        </div>,
        document.body,
    );
};

export default AssignStudentsModal;
