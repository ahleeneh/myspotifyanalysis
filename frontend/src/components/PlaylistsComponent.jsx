import React, { useState, useEffect } from 'react';
import axios from 'axios';
import empty from '../images/empty.png';

function PlaylistsComponent({ playlists, isLoading }) {
    const [selectedPlaylist, setSelectedPlaylist] = useState(null);

    const getPlaylistDetails = async (playlistId) => {
        try {
            const response = await axios.get(`http://localhost:6393/playlist-tracks?playlistId=${playlistId}`, {
                withCredentials: true
            });

            const playlistTracks = response.data;

            console.log(playlistTracks)

        } catch (error) {
            console.error('Error: ', error)
        }
    }

    const truncateText = (description, limit) => {
        if (description.length > limit) {
            return description.substring(0, limit) + '...';
        }
        return description;
    }

    return (
        <>
            <h1>playlists '23</h1>
            <div className="main-content-container">

                {isLoading ? (
                    <p>Loading...</p>
                ) : (
                    playlists && playlists.length > 0) ? (
                    <div className="cards-container">
                        {playlists.map((playlist) => (
                            <div
                                className="card"
                                key={playlist.id}
                                onClick={() => getPlaylistDetails(playlist.id)}
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
                ) : (
                    <div className="cards-container">
                        <div className="card">
                            <img src={empty} className="card-image" />
                            <h2>empty</h2>
                            <p>you haven't created any this year!</p>
                        </div>
                    </div>
                )}

            </div>
        </>
    );
}

export default PlaylistsComponent;
