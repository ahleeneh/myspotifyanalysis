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
    const { playlistAnalysisData, displayName, isLoading, topTracks, topArtistsData } = useUserData();

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
                {renderMainComponent(selectedLink, playlistAnalysisData, isLoading, topTracks, topArtistsData)}
            </div>

        </div>
    );
}

function renderMainComponent(selectedLink, playlistAnalysisData, isLoading, topTracks, topArtistsData) {
    switch (selectedLink) {
        case 'user-playlists':
            return <PlaylistsComponent playlistAnalysisData={playlistAnalysisData} isLoading={isLoading} />;
        case 'top-tracks':
            return <TopTracksComponent topTracks={topTracks}/>;
        case 'top-artists':
            return <TopArtistsComponent topArtists={topArtistsData}/>;
        // case 'recommended':
        //     return <RecommendedComponent />;
        default:
            return <PlaylistsComponent playlistAnalysisData={playlistAnalysisData} isLoading={isLoading} />;
    }
}


export default userPage;