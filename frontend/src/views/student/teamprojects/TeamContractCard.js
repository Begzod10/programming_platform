import { FileCode2, KeyRound, Play } from 'lucide-react';
import './TeamContractCard.css';

const shape = (v) => (v == null ? '—' : typeof v === 'string' ? v : JSON.stringify(v));

/** The team's fixed API contract: what the backend exposes and the frontend calls. Read-only. */
export default function TeamContractCard({ contract, ru }) {
    if (!contract || !Array.isArray(contract.endpoints)) return null;
    const files = contract.files || {};
    const group = (k, uz, rus) => (files[k] || []).length > 0 && (
        <p className="tcc-files"><strong>{ru ? rus : uz}:</strong> {files[k].join(', ')}</p>
    );

    return (
        <details className="tcc" open>
            <summary>
                <FileCode2 size={16} aria-hidden="true" />
                {ru ? 'Контракт команды (API)' : 'Jamoa shartnomasi (API)'}
            </summary>
            <p className="tcc-lead">
                {ru
                    ? 'Все части проекта строятся по этому контракту — названия и формы ответов менять нельзя.'
                    : "Loyihaning barcha qismlari shu shartnomaga ko'ra yoziladi: nomlar va javob shakllari o'zgarmaydi."}
            </p>
            <p className="tcc-meta">
                <span><strong>base_url:</strong> <code>{contract.base_url}</code></span>
                {contract.auth && (
                    <span><KeyRound size={13} aria-hidden="true" /> <strong>{ru ? 'Токен' : 'Token'}:</strong>{' '}
                        <code>{contract.auth.token_key}</code> · <code>{contract.auth.header}</code></span>
                )}
            </p>

            <div className="tcc-table-wrap">
                <table className="tcc-table" aria-label={ru ? 'Эндпоинты' : 'Endpointlar'}>
                    <thead>
                        <tr>
                            <th>id</th><th>{ru ? 'Запрос' : "So'rov"}</th>
                            <th>{ru ? 'Тело запроса' : "So'rov tanasi"}</th><th>{ru ? 'Ответ' : 'Javob'}</th>
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
            {group('backend', 'Backend fayllari', 'Файлы backend')}
            {group('frontend', 'Frontend fayllari', 'Файлы frontend')}

            {contract.run && (
                <div className="tcc-run">
                    <p><Play size={13} aria-hidden="true" /> <strong>{ru ? 'Запуск' : 'Ishga tushirish'}</strong></p>
                    <pre>{contract.run.backend}</pre>
                    <pre>{contract.run.frontend}</pre>
                </div>
            )}
        </details>
    );
}
