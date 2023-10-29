import './UserPages.css';
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';



function userHomePage() {
    const navigate = useNavigate();
    const [playlists, setPlaylists] = useState([]);

    const getUserPlaylists = async () => {
        try {
            const response = await axios.get('http://localhost:6393/user-playlists', {
                withCredentials: true
            })

            const receivedPlaylists = response.data;
            console.log(receivedPlaylists);

            setPlaylists(receivedPlaylists);
        } catch (error) {
            if (error.response && error.response.status === 401) {
                navigate('/');
            } else {
                console.error('Error: ', error);
                navigate('/');
            }
        }
    }

    const deleteCookie = (name) => {
        document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    }

    const handleLogout = async () => {
        try {
            const response = await axios.get('http://localhost:6393/logout', {
                withCredentials: true
            })

            console.log('return from response!!!')
            console.log(response.data);

            setPlaylists([]);

            deleteCookie('My Spotify Analysis Cookie')
            console.log('deleted cookie?');

            navigate('/');
        } catch (error) {
            console.error('Error: ', error)
        }
    }

    useEffect(() => {
        getUserPlaylists();
    }, []);

    return (
        <>
            <h1>Logged in!!!</h1>

            {playlists.length > 0 ? (
                <ul>
                    {playlists.map((playlist) => (
                        <li key={playlist.id}>{playlist.name}</li>
                    ))}
                </ul>
            ) : (
                <p>Loading playlists...</p>
            )}

            <button onClick={handleLogout}>Logout</button>
        </>
    );
}

export default userHomePage;