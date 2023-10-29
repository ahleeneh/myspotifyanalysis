import './UserPages.css';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import SidebarHomeComponent from '../../components/SidebarHomeComponent';
import SidebarLinksComponent from '../../components/SidebarLinksComponent';
import PlaylistsComponent from '../../components/PlaylistsComponent';
import TopArtistsComponent from '../../components/TopArtistsComponent';
import TopTracksComponent from '../../components/TopTracksComponent';

function userPage() {
    const navigate = useNavigate();
    const [selectedLink, setSelectedLink] = useState('user-playlists');

    return (
        <div className="user-page">
            <div className="sidebar-column">
                <div className="sidebar-home">
                    <SidebarHomeComponent />
                </div>
                <div className="sidebar-links">
                    <SidebarLinksComponent onSelectLink={setSelectedLink} selectedLink={selectedLink} />
                </div>

            </div>

            <div className="main-column">
                {renderMainComponent(selectedLink)}
            </div>

        </div>
    );
}

function renderMainComponent(selectedLink) {
    switch (selectedLink) {
        case 'user-playlists':
            return <PlaylistsComponent />;
        case 'top-tracks':
            return <TopTracksComponent />;
        case 'top-artists':
            return <TopArtistsComponent />;
        default:
            return <PlaylistsComponent />;
    }
}


export default userPage;