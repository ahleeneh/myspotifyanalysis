import axios from 'axios';
import React, { useState, useEffect } from 'react';

function TopTracksComponent() {
    const [topTracks, setTopTracks] = useState({
        long_term: null,
        medium_term: null,
        short_term: null
    });
    const [selectedTimeRange, setSelectedTimeRange] = useState('long_term');

    const getTopTracks = async (timeRange) => {
        try {
            let itemType = 'tracks';
            let limit = 20;
            const response = await axios.get(`http://localhost:6393/top-items?itemType=${itemType}&timeRange=${timeRange}&limit=${limit}`, {
                withCredentials: true
            });

            setTopTracks(prevState => ({
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
        getTopTracks('long_term');
        getTopTracks('medium_term');
        getTopTracks('short_term');
    }, []);

    return (
        <div className="main-content-container">
            <h1>top tracks</h1>

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

            {topTracks[selectedTimeRange] ? (
                <div className="playlist-table">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>title</th>
                                <th>album</th>
                                <th>time</th>
                                <th>popularity</th>
                            </tr>
                        </thead>

                        <tbody>
                            {topTracks[selectedTimeRange].map((song, index) => (
                                <tr key={index} className="border-radius">
                                    <td>{index + 1}</td>
                                    <td>
                                        <div className="title-container">
                                            <img src={song.album.images[0].url} alt="album cover" className="playlist-album-cover" />
                                            <div className="title-right">
                                                <p>{song.name}</p>
                                                <p className="grey-text">{song.artists[0].name}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td>{song.album.name}</td>
                                    <td>
                                        {`${Math.floor(song.duration_ms / 60000)}:${(song.duration_ms % 60000 / 1000 < 10 ? '0' : '')}${(song.duration_ms % 60000 / 1000).toFixed(0)}`}
                                    </td>
                                    <td>{song.popularity}%</td>
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

export default TopTracksComponent;