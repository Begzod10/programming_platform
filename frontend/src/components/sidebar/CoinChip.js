import { useNavigate } from 'react-router-dom';
import { Coins } from 'lucide-react';
import { useTranslation } from '../../i18n/useTranslation';
import { useStore } from '../../context/StoreContext';
import './CoinChip.css';

/**
 * Sidebar wallet chip.
 *
 * Sits directly under the StreakBadge, mirrors its collapsed/expanded
 * behaviour, and taps navigate to the store. When the balance is null
 * (unauth or pre-fetch) the chip renders nothing so it never flashes
 * a "0" for a student who actually has coins.
 */
export default function CoinChip({ collapsed = false, storePath = '/student/store' }) {
    const navigate = useNavigate();
    const { lang } = useTranslation();
    const { balance } = useStore();
    const isRu = lang === 'ru';

    if (balance === null || balance === undefined) return null;

    const label = isRu ? 'монет' : 'tanga';
    const openStore = () => navigate(storePath);

    if (collapsed) {
        return (
            <button
                type="button"
                className="coin-chip coin-chip--mini"
                onClick={openStore}
                title={isRu ? `${balance} монет — открыть магазин` : `${balance} tanga — do'konni ochish`}
            >
                <span className="coin-chip__icon" aria-hidden="true"><Coins size={18} /></span>
                <span className="coin-chip__count">{balance}</span>
            </button>
        );
    }

    return (
        <button type="button" className="coin-chip" onClick={openStore}>
            <span className="coin-chip__icon" aria-hidden="true"><Coins size={18} /></span>
            <div className="coin-chip__body">
                <div className="coin-chip__count-row">
                    <span className="coin-chip__count">{balance}</span>
                    <span className="coin-chip__unit">{label}</span>
                </div>
                <div className="coin-chip__sub">
                    {isRu ? 'Открыть магазин →' : "Do'kon →"}
                </div>
            </div>
        </button>
    );
}
