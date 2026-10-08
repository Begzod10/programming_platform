import { useTranslation } from '../i18n/useTranslation';

/** Thin strip shown to demo visitors: what they can and cannot do. */
export default function DemoBanner() {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    return (
        <div role="note" style={{
            background: '#fff7e0', color: '#6b4e00', borderBottom: '1px solid #f0d98a',
            padding: '8px 16px', fontSize: 14, lineHeight: 1.4, textAlign: 'center',
        }}>
            {ru
                ? '🎓 Демо-режим: доступны 2 урока. Отправка проектов недоступна. Чтобы учиться полностью, обратитесь к администратору.'
                : "🎓 Demo rejim: 2 ta dars ochiq. Loyiha topshirish yopiq. To'liq o'qish uchun administratorga murojaat qiling."}
        </div>
    );
}
