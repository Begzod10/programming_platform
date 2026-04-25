export const SECTION_TYPES = [
    { type: 'text',     icon: '📝', label: 'Текст'    },
    { type: 'code',     icon: '💻', label: 'Код'      },
    { type: 'video',    icon: '🎥', label: 'Видео'    },
    { type: 'image',    icon: '🖼️', label: 'Фото'     },
    { type: 'file',     icon: '📁', label: 'Файл'     },
    { type: 'exercise', icon: '🎯', label: 'Exercise' },
    { type: 'project',  icon: '🚀', label: 'Loyiha'   },
];

export const getYTId = (url) => {
    if (!url) return null;
    const match = url.match(
        /(?:youtube\.com\/(?:[^/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?/\s]{11})/
    );
    return match ? match[1] : null;
};