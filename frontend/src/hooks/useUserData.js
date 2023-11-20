import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function useUserData() {
    const navigate = useNavigate();
    const [displayName, setDisplayName] = useState(null);
    const [playlistAnalysisData, setPlaylistAnalysisData] = useState({
        annualUserPlaylists: [],
        totalFollowers: 0,
        avgPopularity: 0,
        topGenres: [],
        topArtists: [],
    });
    const [topTracksData, setTopTracksData] = useState({
        long_term: { tracks: null, stats: null },
        medium_term: { tracks: null, stats: null },
        short_term: { tracks: null, stats: null}
    })
    const [topArtistsData, setTopArtistsData] = useState({
        long_term: null,
        medium_term: null,
        short_term: null
    });
    const [isLoading, setIsLoading] = useState(true);


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

    const getTopArtists = async (timeRange) => {
        try {
            let itemType = 'artists';
            let limit = 20;
            const response = await axios.get(`http://localhost:6393/top-items?itemType=${itemType}&timeRange=${timeRange}&limit=${limit}`, {
                withCredentials: true
            });

            setTopArtistsData(prevState => ({
                ...prevState,
                [timeRange]: response.data.items,
            }));
        } catch (error) {
            console.error('Error:', error)
        }
    }

    const getTopTracks = async (timeRange) => {
        try {
            let itemType = 'tracks';
            let limit = 20;
            const response = await axios.get(`http://localhost:6393/top-items?itemType=${itemType}&timeRange=${timeRange}&limit=${limit}`, {
                withCredentials: true
            });

            setTopTracksData(prevState => ({
                ...prevState,
                [timeRange]: {
                    tracks: response.data.items,
                    stats: response.data.stats,
                }
            }))
        } catch (error) {
            console.error('Error:', error)
        }
    }

    useEffect(() => {
        getUserPlaylists();
        getDisplayName();
    }, []);

    useEffect(() => {
        getTopTracks('long_term');
        getTopTracks('medium_term');
        getTopTracks('short_term');
        getTopArtists('long_term');
        getTopArtists('medium_term');
        getTopArtists('short_term');
    }, []);


    return { playlistAnalysisData, displayName, isLoading, topTracksData, topArtistsData };
}

export default useUserData;