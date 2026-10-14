import { FileCode2, KeyRound, Play } from 'lucide-react';
import './TeamContractCard.css';

const shape = (v) => (v == null ? '—' : typeof v === 'string' ? v : JSON.stringify(v));

/** The team's fixed API contract: what the backend exposes and the frontend calls. Read-only. */
export default function TeamContractCard({ contract, ru }) {
    if (!contract || !Array.isArray(contract.endpoints)) return null;
    const bot = contract.kind === 'bot';
    const files = contract.files || {};
    const group = (k, uz, rus) => (files[k] || []).length > 0 && (
        <p className="tcc-files"><strong>{ru ? rus : uz}:</strong> {files[k].join(', ')}</p>
    );

    return (
        <details className="tcc" open>
            <summary>
                <FileCode2 size={16} aria-hidden="true" />
                {bot
                    ? (ru ? 'Контракт команды (бот)' : 'Jamoa shartnomasi (bot)')
                    : (ru ? 'Контракт команды (API)' : 'Jamoa shartnomasi (API)')}
            </summary>
            <p className="tcc-lead">
                {bot
                    ? (ru
                        ? 'Все части бота строятся по этим сценариям — команды, кнопки и ответы менять нельзя.'
                        : "Botning barcha qismlari shu oqimlarga ko'ra yoziladi: buyruqlar, tugmalar va javoblar o'zgarmaydi.")
                    : (ru
                        ? 'Все части проекта строятся по этому контракту — названия и формы ответов менять нельзя.'
                        : "Loyihaning barcha qismlari shu shartnomaga ko'ra yoziladi: nomlar va javob shakllari o'zgarmaydi.")}
            </p>
            <p className="tcc-meta">
                {!bot && <span><strong>base_url:</strong> <code>{contract.base_url}</code></span>}
                {!bot && contract.auth && (
                    <span><KeyRound size={13} aria-hidden="true" /> <strong>{ru ? 'Токен' : 'Token'}:</strong>{' '}
                        <code>{contract.auth.token_key}</code> · <code>{contract.auth.header}</code></span>
                )}
            </p>

            <div className="tcc-table-wrap">
                <table className="tcc-table" aria-label={bot ? (ru ? 'Сценарии' : 'Oqimlar') : (ru ? 'Эндпоинты' : 'Endpointlar')}>
                    <thead>
                        <tr>
                            <th>id</th><th>{bot ? 'Trigger' : (ru ? 'Запрос' : "So'rov")}</th>
                            <th>{bot ? (ru ? 'Ввод' : 'Kirish') : (ru ? 'Тело запроса' : "So'rov tanasi")}</th>
                            <th>{bot ? (ru ? 'Ответ бота' : 'Bot javobi') : (ru ? 'Ответ' : 'Javob')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {contract.endpoints.map(e => (
                            <tr key={e.id}>
                                <td><code>{e.id}</code></td>
                                <td>
                                    <span className={`tcc-method tcc-method--${e.method.toLowerCase()}`}>{e.method}</span>{' '}
                                    <code>{e.path}</code>{e.auth ? ' 🔒' : ''}
                                </td>
                                <td><code>{shape(e.request)}</code></td>
                                <td><code>{shape(e.response)}</code></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {group('skeleton', 'Skelet (integrator)', 'Каркас (интегратор)')}
            {bot ? group('backend', 'Bot fayllari', 'Файлы бота') : group('backend', 'Backend fayllari', 'Файлы backend')}
            {group('frontend', 'Frontend fayllari', 'Файлы frontend')}

            {contract.run && (
                <div className="tcc-run">
                    <p><Play size={13} aria-hidden="true" /> <strong>{ru ? 'Запуск' : 'Ishga tushirish'}</strong></p>
                    <pre>{contract.run.backend}</pre>
                    {contract.run.frontend && <pre>{contract.run.frontend}</pre>}
                </div>
            )}
        </details>
    );
}
