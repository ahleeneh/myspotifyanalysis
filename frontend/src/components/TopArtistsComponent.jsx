import axios from 'axios';
import React, { useState, useEffect } from 'react';

function TopArtistsComponent() {
    const [topArtists, setTopArtists] = useState({
        long_term: null,
        medium_term: null,
        short_term: null
    });
    const [selectedTimeRange, setSelectedTimeRange] = useState('long_term');

    const getTopArtists = async (timeRange) => {
        try {
            let itemType = 'artists';
            let limit = 20;
            const response = await axios.get(`http://localhost:6393/top-items?itemType=${itemType}&timeRange=${timeRange}&limit=${limit}`, {
                withCredentials: true
            });

            setTopArtists(prevState => ({
                ...prevState,
                [timeRange]: response.data.items,
            }));
        } catch (error) {
            console.error('Error:', error)
        }
    }

    const handleTimeRangeClick = (timeRange) => {
        setSelectedTimeRange(timeRange);
    };

    useEffect(() => {
        getTopArtists('long_term');
        getTopArtists('medium_term');
        getTopArtists('short_term');
    }, []);

    return (
        <div className="main-content-container">
            <h1>top artists</h1>

            <div className="time-range-slider">
                <button
                    className={selectedTimeRange === 'long_term' ? 'selected' : ''}
                    onClick={() => handleTimeRangeClick('long_term')}
                >
                    Long-Term
                </button>
                <button
                    className={selectedTimeRange === 'medium_term' ? 'selected' : ''}
                    onClick={() => handleTimeRangeClick('medium_term')}
                >
                    6 Months
                </button>
                <button
                    className={selectedTimeRange === 'short_term' ? 'selected' : ''}
                    onClick={() => handleTimeRangeClick('short_term')}
                >
                    4 Weeks
                </button>
            </div>

            {topArtists[selectedTimeRange] ? (
                <div className="playlist-table">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>name</th>
                                <th>genres</th>
                                <th>popularity</th>
                            </tr>
                        </thead>

                        <tbody>
                            {topArtists[selectedTimeRange].map((artist, index) => (
                                <tr key={index} className="border-radius">
                                    <td>{index + 1}</td>
                                    <td>
                                        <div className="title-container">
                                            <img src={artist.images[0].url} alt="album cover" className="playlist-album-cover" />
                                            <div className="title-right">
                                                <p>{artist.name}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td>{artist.genres.join(', ')}</td>
                                    <td>{artist.popularity}%</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ) : (
                <div className="playlist-table">
                </div>
            )}
        </div>
    )
}


export default TopArtistsComponent;