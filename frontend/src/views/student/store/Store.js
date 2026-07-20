import { useEffect, useMemo, useState } from 'react';
import { API_URL, headers, useHttp } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import { useStore } from '../../../context/StoreContext';
import { Coins, Palette, Music4, Type, Check, Lock, Play } from 'lucide-react';
import { playSoundAsset } from '../../../utils/soundSynth';
import './Store.css';


const KIND_META = {
    theme:      { key: 'theme',      Icon: Palette, uz: 'Ranglar',  ru: 'Темы'   },
    font:       { key: 'font',       Icon: Type,    uz: 'Shriftlar', ru: 'Шрифты' },
    sound_pack: { key: 'sound_pack', Icon: Music4,  uz: 'Ovozlar',   ru: 'Звуки'  },
};

const TAB_ORDER = ['theme', 'font', 'sound_pack'];


function localise(row, field, lang) {
    if (lang === 'ru') {
        return row[`${field}_ru`] || row[field] || '';
    }
    return row[field] || row[`${field}_ru`] || '';
}


// ─── theme preview: mini swatch strip using the theme's tokens ────────────


function ThemeSwatch({ tokens }) {
    if (!tokens) return null;
    const keys = ['--color-primary', '--color-primary-mid', '--color-primary-light', '--color-ink', '--bg-page'];
    return (
        <div className="store-swatch">
            {keys.filter(k => tokens[k]).map(k => (
                <span key={k} className="store-swatch__dot" style={{ background: tokens[k] }} />
            ))}
        </div>
    );
}


// ─── font preview: renders the item name in its own font ──────────────────


function FontPreview({ stack, family }) {
    if (!stack) return null;
    return (
        <div className="store-font-preview" style={{ fontFamily: stack }}>
            {family || 'Aa Bb Cc 123'}
        </div>
    );
}


// ─── sound preview: play a short probe of the OK sound ────────────────────


function SoundProbe({ assetRef }) {
    if (!assetRef) return null;
    const play = () => playSoundAsset(assetRef);
    return (
        <button type="button" className="store-sound-probe" onClick={play} aria-label="Preview sound">
            <Play size={14} />
        </button>
    );
}


// ─── item card ────────────────────────────────────────────────────────────


function ItemCard({ item, lang, onBuy, buying, inventoryRow, onEquip, onUnequip, isRu }) {
    const title = localise(item, 'title', lang);
    const description = localise(item, 'description', lang);
    const Icon = KIND_META[item.kind]?.Icon || Coins;

    const owned = !!inventoryRow;
    const equipped = !!inventoryRow?.is_equipped;
    const priceLabel = `${item.price_coins} ${isRu ? 'монет' : 'tanga'}`;
    const previewNode = (
        item.kind === 'theme' ? <ThemeSwatch tokens={item.asset_ref?.tokens} /> :
        item.kind === 'font'  ? <FontPreview stack={item.asset_ref?.stack} family={item.asset_ref?.family} /> :
        item.kind === 'sound_pack' ? <SoundProbe assetRef={item.asset_ref} /> :
        null
    );

    let cta;
    if (equipped) {
        cta = (
            <button type="button" className="store-cta store-cta--equipped" onClick={() => onUnequip(inventoryRow)}>
                <Check size={14} /> {isRu ? 'Экипировано' : 'Yoqilgan'}
            </button>
        );
    } else if (owned) {
        cta = (
            <button type="button" className="store-cta store-cta--equip" onClick={() => onEquip(inventoryRow)}>
                {isRu ? 'Использовать' : 'Yoqish'}
            </button>
        );
    } else if (!item.can_afford) {
        cta = (
            <button type="button" className="store-cta store-cta--locked" disabled title={priceLabel}>
                <Lock size={14} /> {priceLabel}
            </button>
        );
    } else {
        cta = (
            <button
                type="button"
                className="store-cta store-cta--buy"
                onClick={() => onBuy(item)}
                disabled={buying}
            >
                {buying ? '…' : priceLabel}
            </button>
        );
    }

    return (
        <div className={`store-card ${equipped ? 'is-equipped' : ''} ${owned ? 'is-owned' : ''}`}>
            <div className="store-card__head">
                <span className="store-card__icon"><Icon size={18} /></span>
                <span className="store-card__kind">{isRu ? KIND_META[item.kind]?.ru : KIND_META[item.kind]?.uz}</span>
            </div>
            <h3 className="store-card__title">{title}</h3>
            {description && <p className="store-card__desc">{description}</p>}
            {previewNode && <div className="store-card__preview">{previewNode}</div>}
            <div className="store-card__foot">{cta}</div>
        </div>
    );
}


// ─── main page ────────────────────────────────────────────────────────────


export default function Store() {
    const { request } = useHttp();
    const { t, lang } = useTranslation();
    const isRu = lang === 'ru';
    const { balance, lifetimePoints, inventory, refreshAll } = useStore();

    const [tab, setTab] = useState('theme');
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [buyingId, setBuyingId] = useState(null);
    const [flash, setFlash] = useState(null);  // {kind: 'ok'|'err', text: '...'}

    useEffect(() => {
        let alive = true;
        setLoading(true);
        request(`${API_URL}v1/store/items`, 'GET', null, headers())
            .then(rows => { if (alive) setItems(Array.isArray(rows) ? rows : []); })
            .catch(() => { if (alive) setItems([]); })
            .finally(() => { if (alive) setLoading(false); });
        return () => { alive = false; };
    }, [request, balance]);  // re-fetch after a purchase updates balance

    const inventoryByItemId = useMemo(() => {
        const m = new Map();
        (inventory || []).forEach(r => m.set(r.store_item_id, r));
        return m;
    }, [inventory]);

    const filteredItems = useMemo(
        () => items.filter(i => i.kind === tab),
        [items, tab]
    );

    const showFlash = (kind, text) => {
        setFlash({ kind, text });
        setTimeout(() => setFlash(null), 2600);
    };

    const handleBuy = async (item) => {
        setBuyingId(item.id);
        try {
            const idem = `buy-${item.id}-${Date.now()}`;
            await request(
                `${API_URL}v1/store/purchase`,
                'POST',
                JSON.stringify({ store_item_id: item.id, idempotency_key: idem }),
                headers(),
            );
            await refreshAll();
            showFlash('ok', isRu ? 'Куплено ✓' : 'Sotib olindi ✓');
        } catch (e) {
            const msg = e?.message || '';
            let human;
            if (msg.includes('402')) human = isRu ? 'Недостаточно монет' : 'Tanga yetarli emas';
            else if (msg.includes('409')) human = isRu ? 'Уже куплено' : 'Allaqachon sizniki';
            else human = isRu ? 'Ошибка покупки' : 'Xatolik yuz berdi';
            showFlash('err', human);
        } finally {
            setBuyingId(null);
        }
    };

    const handleEquip = async (inv) => {
        try {
            await request(
                `${API_URL}v1/store/inventory/${inv.inventory_id}/equip`,
                'POST',
                JSON.stringify({}),
                headers(),
            );
            await refreshAll();
            showFlash('ok', isRu ? 'Экипировано' : 'Yoqildi');
        } catch {
            showFlash('err', isRu ? 'Не удалось экипировать' : 'Yoqib bo\'lmadi');
        }
    };

    const handleUnequip = async (inv) => {
        try {
            await request(
                `${API_URL}v1/store/inventory/${inv.inventory_id}/unequip`,
                'POST',
                JSON.stringify({}),
                headers(),
            );
            await refreshAll();
        } catch {
            showFlash('err', isRu ? 'Не удалось снять' : 'Bekor qilib bo\'lmadi');
        }
    };

    return (
        <div className="store-page">
            <header className="store-header">
                <div className="store-header__title">
                    <h1>{t('store_title') || (isRu ? 'Магазин' : "Do'kon")}</h1>
                    <p className="store-header__sub">
                        {isRu
                            ? 'Заработанные монеты — теперь на темы, шрифты и звуки.'
                            : "O'zingiz yiqqan tangalarni ranglar, shriftlar va ovozlarga sarflang."}
                    </p>
                </div>
                <div className="store-wallet">
                    <div className="store-wallet__pill">
                        <Coins size={16} />
                        <span className="store-wallet__count">{balance ?? '–'}</span>
                        <span className="store-wallet__unit">{isRu ? 'монет' : 'tanga'}</span>
                    </div>
                    {lifetimePoints !== null && (
                        <div className="store-wallet__lifetime" title={isRu ? 'Заработано за всё время' : "Umumiy topilgan"}>
                            {isRu ? 'Всего заработано' : "Jami yiqqan"}: <b>{lifetimePoints}</b>
                        </div>
                    )}
                </div>
            </header>

            {flash && (
                <div className={`store-flash store-flash--${flash.kind}`}>{flash.text}</div>
            )}

            <nav className="store-tabs" aria-label="Store categories">
                {TAB_ORDER.map(kind => {
                    const meta = KIND_META[kind];
                    const Icon = meta.Icon;
                    const active = tab === kind;
                    return (
                        <button
                            key={kind}
                            type="button"
                            className={`store-tab ${active ? 'is-active' : ''}`}
                            onClick={() => setTab(kind)}
                        >
                            <Icon size={16} />
                            <span>{isRu ? meta.ru : meta.uz}</span>
                        </button>
                    );
                })}
            </nav>

            {loading ? (
                <div className="store-grid">
                    {[0, 1, 2, 3].map(k => (
                        <div key={k} className="store-card store-card--skeleton" />
                    ))}
                </div>
            ) : filteredItems.length === 0 ? (
                <div className="store-empty">
                    {isRu ? 'Здесь пока пусто.' : 'Hozircha bu bo\'limda hech nima yo\'q.'}
                </div>
            ) : (
                <div className="store-grid">
                    {filteredItems.map(item => (
                        <ItemCard
                            key={item.id}
                            item={item}
                            lang={lang}
                            isRu={isRu}
                            onBuy={handleBuy}
                            onEquip={handleEquip}
                            onUnequip={handleUnequip}
                            buying={buyingId === item.id}
                            inventoryRow={inventoryByItemId.get(item.id)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
