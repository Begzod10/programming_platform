/* ─── Shared constants and factory functions for LessonEditor ─── */

export const FONT_SIZES = ['12px', '14px', '16px', '18px', '20px', '24px', '28px', '32px'];
export const FONT_FAMILIES = ['Georgia', 'Courier New', 'Arial', 'Trebuchet MS', 'Verdana'];
export const HEADINGS = ['Paragraph', 'H1', 'H2', 'H3'];
export const CODE_LANGS = ['javascript', 'typescript', 'python', 'html', 'css', 'jsx', 'tsx', 'java', 'c', 'cpp', 'rust', 'go', 'sql', 'bash'];
export const EX_TYPES = ['text_input', 'multiple_choice', 'drag_and_drop', 'fill_in_blank'];
export const DIFF_LEVELS = ['Easy', 'Medium', 'Hard'];
export const DIFF_POINTS = { Easy: 2, Medium: 4, Hard: 5 };

export const makeSection = (type) => ({
    id: Date.now() + Math.random(),
    type,
    label: '',
    html: '',
    code: '',
    lang: 'javascript',
    videoUrl: '',
    imgUrl: '',
    imgUrlDirect: '',
    imgName: '',
    fileName: '',
    fileSize: '',
    description: '',
    requirements: '',
    techStack: '',
    deadline: '',
    exercises: [],
    projectFiles: [],   // ← code files inside Loyiha (project) block
    mashqType: 'textarea',
    question: '',
    answer: '',
    words: [],
});

export const makeExercise = () => ({
    _localId: Date.now() + Math.random(),
    id: null,
    title: '',
    description: '',
    exercise_type: 'text_input',
    options: '',
    correct_answers: '',
    drag_items: '',
    correct_order: '',
    is_multiple_select: false,
    expected_answer: '',
    hint: '',
    difficulty_level: 'Easy',
    points: 10,
    order: 0,
});
