import axios from 'axios';
import React, { useState, useEffect } from 'react';

function TopTracksComponent() {
    const [topTracks, setTopTracks] = useState(null);
    const [next, setNext] = useState(null);
    const [selectedTimeRange, setSelectedTimeRange] = useState('long_term');

    const getTopTracks = async (timeRange) => {
        try {
            let itemType = 'tracks';
            let limit = 20;
            const response = await axios.get(`http://localhost:6393/top-items?itemType=${itemType}&timeRange=${timeRange}&limit=${limit}`, {
                withCredentials: true
            });

            console.log(response.data.items);
            setTopTracks(response.data.items);
            setNext(response.data.next);
        } catch (error) {
            console.error('Error:', error)
        }
    }

    const handleTimeRangeClick = (timeRange) => {
        setSelectedTimeRange(timeRange);
    };

    useEffect(() => {
        getTopTracks(selectedTimeRange);
    }, [selectedTimeRange]);

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

            {topTracks ? (
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
                            {topTracks.map((song, index) => (
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
                <p>loading...</p>
            )}
        </div>
    )
}

export default TopTracksComponent;