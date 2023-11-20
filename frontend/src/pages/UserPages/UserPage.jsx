import './UserPages.css';
import React, { useState } from 'react';

import SidebarHomeComponent from '../../components/SidebarHomeComponent';
import SidebarLinksComponent from '../../components/SidebarLinksComponent';
import PlaylistsComponent from '../../components/PlaylistsComponent';
import TopArtistsComponent from '../../components/TopArtistsComponent';
import TopTracksComponent from '../../components/TopTracksComponent';
import useUserData from '../../hooks/useUserData';

function userPage() {
    const [selectedLink, setSelectedLink] = useState('user-playlists');
    const { playlistAnalysisData, displayName, isLoading, topTracksData, topArtistsData } = useUserData();

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
                {renderMainComponent(selectedLink, playlistAnalysisData, isLoading, topTracksData, topArtistsData)}
            </div>

        </div>
    );
}

function renderMainComponent(selectedLink, playlistAnalysisData, isLoading, topTracksData, topArtistsData) {
    switch (selectedLink) {
        case 'user-playlists':
            return <PlaylistsComponent playlistAnalysisData={playlistAnalysisData} isLoading={isLoading} />;
        case 'top-tracks':
            return <TopTracksComponent topTracksData={topTracksData}/>;
        case 'top-artists':
            return <TopArtistsComponent topArtists={topArtistsData}/>;
        default:
            return <PlaylistsComponent playlistAnalysisData={playlistAnalysisData} isLoading={isLoading} />;
    }
}


export default userPage;