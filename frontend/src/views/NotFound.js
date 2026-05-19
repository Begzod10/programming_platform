import { useNavigate } from 'react-router-dom';

// [REFACTOR] 404 Not Found page
function NotFound() {
    const navigate = useNavigate();

    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            background: '#f5f6fa',
            fontFamily: 'inherit',
            padding: '20px',
            textAlign: 'center',
        }}>
            <div style={{ fontSize: '80px', marginBottom: '16px' }}>🔍</div>
            <h1 style={{
                fontSize: '48px',
                fontWeight: 800,
                color: '#1a1a2e',
                margin: '0 0 8px',
            }}>404</h1>
            <p style={{
                fontSize: '18px',
                color: 'rgba(26,26,46,0.5)',
                margin: '0 0 32px',
            }}>Страница не найдена</p>
            <button
                onClick={() => navigate('/')}
                style={{
                    padding: '12px 32px',
                    borderRadius: '12px',
                    border: 'none',
                    background: 'linear-gradient(135deg, #6c5ce7, #a29bfe)',
                    color: '#fff',
                    fontSize: '16px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'transform 0.2s',
                }}
                onMouseEnter={e => e.target.style.transform = 'scale(1.05)'}
                onMouseLeave={e => e.target.style.transform = 'scale(1)'}
            >
                ← На главную
            </button>
        </div>
    );
}

export default NotFound;
