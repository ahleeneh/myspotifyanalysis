import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function useUserData() {
    const navigate = useNavigate();
    const [playlistAnalysisData, setPlaylistAnalysisData] = useState({
        annualUserPlaylists: [],
        totalFollowers: 0,
        avgPopularity: 0,
        topGenres: [],
        topArtists: [],
    });
    const [isLoading, setIsLoading] = useState(true);
    const [displayName, setDisplayName] = useState(null);
    // const [topTracks, setTopTracks] = useState([]);
    // const [topArtists, setTopArtists] = useState([]);

    const getUserPlaylists = async () => {
        try {
            const response = await axios.get('http://localhost:6393/user-playlists', {
                withCredentials: true
            })

            const receivedPlaylists = response.data;

            if (receivedPlaylists !== 'No playlists found for this year for current user.') {
                const playlistAnalysisData = {
                    annualUserPlaylists: receivedPlaylists.annual_user_playlists,
                    totalFollowers: receivedPlaylists.total_followers,
                    avgPopularity: receivedPlaylists.avg_popularity,
                    topGenres: receivedPlaylists.top_genres,
                    topArtists: receivedPlaylists.top_artists
                };

                setPlaylistAnalysisData(playlistAnalysisData);
            }

        } catch (error) {
            console.log('Error getting user playlists: ', error)
            navigate('/');
        } finally {
            setIsLoading(false);
        }
    }

    const getDisplayName = async () => {
        try {
            const response = await axios.get('http://localhost:6393/user-display-name', {
                withCredentials: true
            })

            const receivedDisplayName = response.data;

            setDisplayName(receivedDisplayName);
        } catch (error) {
            console.log('Error getting user display name: ', error)
        }
    }

    useEffect(() => {
        getUserPlaylists();
        getDisplayName();
    }, []);

    return { playlistAnalysisData, displayName, isLoading };
}

export default useUserData;