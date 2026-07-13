import { API_URL } from '../../../../api/search/base';

// ФИКС: сравниваем id через String() — бэкенд может вернуть number, useParams всегда string
export const sameId = (a, b) => String(a) === String(b);

/* ─── helpers ─── */
export const parseToComma = (val) => {
    if (!val) return '';
    if (Array.isArray(val)) return val.join(',');
    if (typeof val === 'string') {
        const trimmed = val.trim();
        if (trimmed.startsWith('[')) {
            try { const p = JSON.parse(trimmed); if (Array.isArray(p)) return p.join(','); } catch (_) { }
        }
        return trimmed;
    }
    return '';
};

export const commaToJsonArray = (str) => {
    if (!str) return null;
    const arr = str.split(',').map(s => s.trim()).filter(Boolean);
    return arr.length === 0 ? null : JSON.stringify(arr);
};

export const apiToExercise = (e) => ({
    _localId: e.id, id: e.id, title: e.title || '', description: e.description || '',
    exercise_type: e.exercise_type || 'text_input', correct_answers: e.correct_answers || '',
    drag_items: parseToComma(e.drag_items), correct_order: parseToComma(e.correct_order),
    options: parseToComma(e.options), is_multiple_select: e.is_multiple_select || false,
    expected_answer: e.expected_answer || '', hint: e.hint || '', explanation: e.explanation || '',
    difficulty_level: e.difficulty_level || 'Easy', points: e.points || 10, order: e.order || 0,
});

export const exerciseToApi = (ex) => ({
    title: ex.title, description: ex.description, exercise_type: ex.exercise_type,
    correct_answers: ex.correct_answers || null, drag_items: commaToJsonArray(ex.drag_items),
    correct_order: commaToJsonArray(ex.correct_order), options: commaToJsonArray(ex.options),
    is_multiple_select: ex.is_multiple_select || false, expected_answer: ex.expected_answer || null,
    hint: ex.hint || null, explanation: ex.explanation || null,
    difficulty_level: ex.difficulty_level || 'Easy', points: ex.points || 10, order: ex.order || 0,
});

export const apiToLesson = (l) => {
    if (l.sections_json) {
        try {
            const sections = JSON.parse(l.sections_json);
            return { id: l.id, title: l.title, chapter: l.chapter || '', image: l.image_url || '', completed: false, order: l.order || 0, is_published: l.is_published || false, sections };
        } catch (_) { }
    }
    return {
        id: l.id, title: l.title, chapter: l.chapter || '', image: l.image_url || '',
        completed: false, order: l.order || 0, is_published: l.is_published || false,
        sections: [
            l.text_content ? { id: `t${l.id}`, type: 'text',    label: 'Текст',  html: l.text_content } : null,
            l.code_content ? { id: `c${l.id}`, type: 'code',    label: 'Код',    lang: l.code_language || 'javascript', code: l.code_content } : null,
            l.video_url    ? { id: `v${l.id}`, type: 'video',   label: 'Видео',  videoUrl: l.video_url } : null,
            l.image_url    ? { id: `i${l.id}`, type: 'image',   label: 'Фото',   imgUrl: l.image_url } : null,
            l.file_url     ? { id: `f${l.id}`, type: 'file',    label: 'Файл',   fileName: l.file_url, fileUrl: `/uploads/lesson_files/${encodeURIComponent(l.file_url)}` } : null,
            (l.task_title || l.task_description) ? { id: `p${l.id}`, type: 'project', label: l.task_title || 'Loyiha', description: l.task_description || '', requirements: l.task_requirements || '', techStack: l.task_technologies || '', deadline: l.task_deadline_days || '' } : null,
            Array.isArray(l.exercises) ? { id: `e${l.id}`, type: 'exercise', label: 'Упражнения', exercises: l.exercises.map(apiToExercise) } : null,
        ].filter(Boolean),
    };
};

export const lessonToApi = (form) => {
    const project = form.sections?.find(s => s.type === 'project');
    const mashq   = form.sections?.find(s => s.type === 'mashq');
    return {
        title: form.title, order: Number(form.order) || 0, chapter: form.chapter || '',
        image_url: form.image || '',
        sections_json: JSON.stringify(form.sections || []),
        text_content: form.sections?.find(s => s.type === 'text')?.html || '',
        code_content: form.sections?.find(s => s.type === 'code')?.code || '',
        code_language: form.sections?.find(s => s.type === 'code')?.lang || '',
        video_url: form.sections?.find(s => s.type === 'video')?.videoUrl || '',
        file_url: form.sections?.find(s => s.type === 'file')?.fileName || '',
        mashq_type: mashq?.mashqType || null, mashq_question: mashq?.question || null,
        mashq_answer: mashq?.answer || null, mashq_words: mashq?.words?.join(',') || null,
        task_title: project ? (project.label || 'Loyiha') : null,
        task_description: project?.description || null, task_requirements: project?.requirements || null,
        task_technologies: project?.techStack || null,
        task_deadline_days: project?.deadline ? Number(project.deadline) : null,
    };
};
