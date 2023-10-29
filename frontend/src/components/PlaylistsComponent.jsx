import React, { useState, useEffect } from 'react';
import axios from 'axios';
import empty from '../images/empty.png';

import PlaylistTracksComponent from './PlaylistTracksComponent';

function PlaylistsComponent({ playlists, isLoading }) {
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

            console.log(playlistTracks)

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

            <p>loading...</p>
        </div>
    )

    if (playlists && playlists.length > 0) {
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
                        {playlists.map((playlist) => (
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
                                <h2>{truncateText(playlist.name, 19)}</h2>
                                <p>{truncateText(playlist.description, 35)}</p>
                            </div>
                        ))}
                    </div>
                </div>
            );
        }
    }

    return (
        <div className="main-content-container">
            <h1>playlists '23</h1>

            <div className="cards-container">
                <div className="card">
                    <img src={empty} className="card-image" />
                    <h2>empty</h2>
                    <p>you haven't created any this year!</p>
                </div>
            </div>
        </div>
    );

}

export default PlaylistsComponent;
