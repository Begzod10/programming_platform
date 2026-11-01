import React, { useState } from 'react';
import './PcControl.css';
import { Monitor } from 'lucide-react';
import { useTranslation } from '../../../i18n/useTranslation';
import { pcStrings } from './pcStrings';
import DevicesTab from './DevicesTab';
import AllowlistTab from './AllowlistTab';
import ReportTab from './ReportTab';

export default function PcControl() {
    const { lang } = useTranslation();
    const t = pcStrings(lang);
    const [tab, setTab] = useState('devices');
    const tabs = [
        ['devices', t.tabDevices],
        ['allowlist', t.tabAllowlist],
        ['report', t.tabReport],
    ];
    return (
        <div className="pc-page">
            <div className="pc-head">
                <div className="pc-head-ico"><Monitor size={24} /></div>
                <div>
                    <h1>{t.title}</h1>
                    <p>{t.subtitle}</p>
                </div>
            </div>
            <div className="pc-tabs" role="tablist">
                {tabs.map(([id, label]) => (
                    <button key={id} type="button" role="tab" aria-selected={tab === id}
                        className={`pc-tab${tab === id ? ' active' : ''}`} onClick={() => setTab(id)}>
                        {label}
                    </button>
                ))}
            </div>
            {tab === 'devices' && <DevicesTab />}
            {tab === 'allowlist' && <AllowlistTab />}
            {tab === 'report' && <ReportTab />}
        </div>
    );
}
