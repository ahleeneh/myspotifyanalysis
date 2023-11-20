import React, { useState, useEffect } from 'react';
import axios from 'axios';
import empty from '../images/empty.png';
import topartists from '../images/topartists.png';
import topgenres from '../images/topgenres.png';
import totalfollowers from '../images/totalfollowers.png';
import averagepopularity from '../images/averagepopularity.png';

import PlaylistTracksComponent from './PlaylistTracksComponent';

function PlaylistsComponent({ playlistAnalysisData, isLoading }) {
    const { annualUserPlaylists, totalFollowers, avgPopularity, topGenres, topArtists } = playlistAnalysisData;
    const [selectedPlaylist, setSelectedPlaylist] = useState(null);
    const [playlistTracks, setPlaylistTracks] = useState([]);
    const [playlistImage, setPlaylistImage] = useState(null);
    const [playlistName, setPlaylistName] = useState(null);
    const [playlistDescription, setPlaylistDescription] = useState(null);

    const getPlaylistDetails = async (playlistId, playlistImages, playlistName, playlistDescription) => {
        try {
            const response = await axios.get(`http://localhost:6393/playlist-tracks?playlistId=${playlistId}`, {
                withCredentials: true
            });

            const playlistTracks = response.data;

            setSelectedPlaylist(playlistId);
            setPlaylistTracks(playlistTracks);
            setPlaylistName(playlistName);
            setPlaylistDescription(playlistDescription);
            if (playlistImages && playlistImages.length > 0) {
                setPlaylistImage(playlistImages[0].url);
            }

        } catch (error) {
            console.error('Error: ', error)
        }
    }

    const reset = () => {
        setSelectedPlaylist(null);
        setPlaylistTracks([]);
        setPlaylistImage(null);
        setPlaylistName(null);
        setPlaylistDescription(null);
    }

    const truncateText = (description, limit) => {
        if (description.length > limit) {
            return description.substring(0, limit) + '...';
        }
        return description;
    }

    if (isLoading) return (
        <div className="main-content-container">
            <h1>playlists '23</h1>

            <p>finding and analyzing all your playlists created this year...</p>
        </div>
    )

    if (annualUserPlaylists && annualUserPlaylists.length > 0) {
        if (selectedPlaylist) {
            return (
                <div className="main-content-container">
                    <PlaylistTracksComponent
                        tracks={playlistTracks}
                        image={playlistImage}
                        name={playlistName}
                        description={playlistDescription}
                        onReset={reset}
                    />
                </div>
            )
        } else {
            return (
                <div className="main-content-container">
                    <h1>playlists '23</h1>
                    <div className="cards-container">
                        {annualUserPlaylists.map((playlist) => (
                            <div
                                className="card"
                                key={playlist.id}
                                onClick={() => getPlaylistDetails(playlist.id, playlist.images || null, playlist.name, playlist.description)}
                            >
                                {playlist.images && playlist.images.length > 0 && playlist.images[0].url ? (
                                    <img src={playlist.images[0].url} className="card-image" />
                                ) : (
                                    <img src={empty} className="card-image" />
                                )}
                                <h3>{truncateText(playlist.name, 19)}</h3>
                                <p>{truncateText(playlist.description, 35)}</p>
                            </div>
                        ))}
                    </div>

                    <div className="playlists-analysis-container">
                        <h2>playlist '23 analysis</h2>

                        <div className="cards-container">
                            <div className="card analysis-card">
                                <img src={topartists} className="card-image" />
                                <div className="analysis-card-right">
                                    <h3>top playlist artists</h3>
                                    {topArtists.map((artist, index) => (
                                        <p key={index}>{index + 1}: {artist}</p>
                                    ))}
                                </div>
                            </div>

                            <div className="card analysis-card">
                                <img src={topgenres} className="card-image" />
                                <div className="analysis-card-right">
                                    <h3>top playlist genres</h3>
                                    {topGenres.map((genre, index) => (
                                        <p key={index}>{index + 1}: {genre}</p>
                                    ))}
                                </div>
                            </div>

                            <div className="card analysis-card">
                                <img src={averagepopularity} className="card-image" />
                                <div className="analysis-card-right">
                                    <h3>average popularity</h3>
                                    <p className="larger-font">{avgPopularity}%</p>
                                </div>
                            </div>

                            <div className="card analysis-card">
                                <img src={totalfollowers} className="card-image" />
                                <div className="analysis-card-right">
                                    <h3>total followers</h3>
                                    <p className="larger-font">{totalFollowers}</p>
                                </div>
                            </div>
                        </div>
                    </div>


                </div >
            );
        }
    }

    return (
        <div className="main-content-container">
            <h1>playlists '23</h1>

            <div className="cards-container">
                <div className="card">
                    <img src={empty} className="card-image" />
                    <h3>empty</h3>
                    <p>you haven't created any this year!</p>
                </div>
            </div>
        </div>
    );

}

export default PlaylistsComponent;
