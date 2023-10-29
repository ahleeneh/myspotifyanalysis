import React from 'react';

function SidebarHomeComponent({ displayName }) {
    return (
        <>
            <h2>my Spotify analysis</h2>
            <p>🎧 {displayName}</p>
        </>
    )
}

export default SidebarHomeComponent;