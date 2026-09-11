import React from 'react';

// Module-scope so it isn't redeclared (and thus torn down/rebuilt by React)
// on every render of the parent component.
export const Loader = () => (
    <div style={{ textAlign: 'center', padding: '60px', color: 'rgba(26,26,46,0.4)' }}>Загрузка...</div>
);
