import React, { useState } from 'react';
import TopTracksStatsComponent from './TopTracksStatsComponent';
import TopTracksTableComponent from './TopTracksTableComponent';

function TopTracksComponent({ topTracksData }) {
    const [selectedTimeRange, setSelectedTimeRange] = useState('long_term');

    const handleTimeRangeClick = (timeRange) => {
        setSelectedTimeRange(timeRange);
    };

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

            {topTracksData[selectedTimeRange]?.stats ? (
                <TopTracksStatsComponent stats={topTracksData[selectedTimeRange].stats} />
            ) : null}

            {topTracksData[selectedTimeRange]?.tracks ? (
                <TopTracksTableComponent tracks={topTracksData[selectedTimeRange].tracks} />
            ) : (
                <div className="playlist-table">
                </div>
            )}
        </div>
    )
}

export default TopTracksComponent;