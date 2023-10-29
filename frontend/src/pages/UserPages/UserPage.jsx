import './UserPages.css';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import SidebarHomeComponent from '../../components/SidebarHomeComponent';
import SidebarLinksComponent from '../../components/SidebarLinksComponent';
import PlaylistsComponent from '../../components/PlaylistsComponent';
import TopArtistsComponent from '../../components/TopArtistsComponent';
import TopTracksComponent from '../../components/TopTracksComponent';
import RecommendedComponent from '../../components/RecommendedComponent';

import useUserData from '../../hooks/useUserData';

function userPage() {
    const navigate = useNavigate();
    const [selectedLink, setSelectedLink] = useState('user-playlists');
    const { playlists, topTracks, topArtists, displayName, isLoading } = useUserData();

    return (
        <div className="user-page">
            <div className="sidebar-column">
                <div className="sidebar-home">
                    <SidebarHomeComponent displayName={displayName}/>
                </div>
                <div className="sidebar-links">
                    <SidebarLinksComponent onSelectLink={setSelectedLink} selectedLink={selectedLink} />
                </div>

            </div>

            <div className="main-column">
                {renderMainComponent(selectedLink, playlists, isLoading)}
            </div>

        </div>
    );
}

function renderMainComponent(selectedLink, playlists, isLoading) {
    switch (selectedLink) {
        case 'user-playlists':
            return <PlaylistsComponent playlists={playlists} isLoading={isLoading} />;
        case 'top-tracks':
            return <TopTracksComponent />;
        case 'top-artists':
            return <TopArtistsComponent />;
        case 'recommended':
            return <RecommendedComponent />;
        default:
            return <PlaylistsComponent playlists={playlists} isLoading={isLoading} />;
    }
}


export default userPage;