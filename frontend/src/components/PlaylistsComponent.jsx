import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import empty from '../images/empty.png';

function PlaylistsComponent() {
    const navigate = useNavigate();
    const [playlists, setPlaylists] = useState([]);
    const [notFound, setNotFound] = useState(false);

    const getUserPlaylists = async () => {
        try {
            const response = await axios.get('http://localhost:6393/user-playlists', {
                withCredentials: true
            })

            const receivedPlaylists = response.data;

            if (receivedPlaylists == 'No playlists found for this year for current user.') {
                setNotFound(true);
            } else {
                setPlaylists(receivedPlaylists);
            }

            console.log('received Playlists: ', receivedPlaylists);

        } catch (error) {
            if (error.response && error.response.status === 401) {
                navigate('/');
            } else {
                console.error('Error: ', error);
                navigate('/');
            }
        }
    }

    useEffect(() => {
        getUserPlaylists()
    }, []);

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
                {notFound ? (
                    <p>You haven't created any playlists this year!</p>
                ) : (
                    playlists.length > 0 ? (
                        <div className="cards-container">

                            {playlists.map((playlist) => (
                                <div className="card" key={playlist.id}>
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
                        <div className="main-content-container">
                            <p>loading...</p>
                        </div>
                    )
                )}

            </div>
        </>
    )
}

export default PlaylistsComponent;