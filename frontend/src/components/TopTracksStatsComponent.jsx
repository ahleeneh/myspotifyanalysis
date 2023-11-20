import React from 'react';

function TopTrackStats({ stats }) {
    const { acousticness, danceability, energy, instrumentalness, speechiness, valence } = stats;

    const getMoodEmoji = (valence) => {
        if (valence < 20) {
            return "🙁"
        } else if (valence < 40) {
            return "😐"
        } else if (valence < 60) {
            return "🙂"
        } else if (valence < 80) {
            return "😊"
        } else {
            return "😄"
        }
    }

    const getAcousticnessEmoji = (acousticness) => {
        if (acousticness < 20) {
            return "🤫";
        } else if (acousticness < 40) {
            return "🎵";
        } else if (acousticness < 60) {
            return "🔉";
        } else if (acousticness < 80) {
            return "🔊";
        } else {
            return "🔔";
        }
    };

    const getDanceabilityEmoji = (danceability) => {
        if (danceability < 20) {
            return "🚶‍♂️";
        } else if (danceability < 40) {
            return "💃";
        } else if (danceability < 60) {
            return "🕺";
        } else if (danceability < 80) {
            return "👯‍♂️";
        } else {
            return "🕴️";
        }
    };

    const getEnergyEmoji = (energy) => {
        if (energy < 20) {
            return "😴";
        } else if (energy < 40) {
            return "⚡️";
        } else if (energy < 60) {
            return "🚀"; // Rocket
        } else if (energy < 80) {
            return "🔥";
        } else {
            return "💥";
        }
    };

    const getInstrumentalnessEmoji = (instrumentalness) => {
        if (instrumentalness < 20) {
            return "🎹";
        } else if (instrumentalness < 40) {
            return "🎸";
        } else if (instrumentalness < 60) {
            return "🎷";
        } else if (instrumentalness < 80) {
            return "🎺";
        } else {
            return "🥁";
        }
    };

    const getSpeechinessEmoji = (speechiness) => {
        if (speechiness < 33) {
            return "📻";
        } else if (speechiness < 66) {
            return "🎙️";
        } else {
            return "💬";
        }
    };

    return (
        <div className="stats-card-container">
            <div className="stats-card">
                <h3>{getAcousticnessEmoji(acousticness)} acoustic</h3>
                <p>{acousticness}%</p>
            </div>
            <div className="stats-card">
                <h3>{getDanceabilityEmoji(danceability)} dance</h3>
                <p>{danceability}%</p>
            </div>
            <div className="stats-card">
                <h3>{getEnergyEmoji(energy)} energy</h3>
                <p>{energy}%</p>
            </div>
            <div className="stats-card">
                <h3>{getInstrumentalnessEmoji(instrumentalness)} instruments</h3>
                <p>{instrumentalness}%</p>
            </div>
            <div className="stats-card">
                <h3>{getSpeechinessEmoji(speechiness)} wordy</h3>
                <p>{speechiness}%</p>
            </div>
            <div className="stats-card">
                <h3>{getMoodEmoji(valence)} mood</h3>
                <p>{valence}%</p>
            </div>
        </div>

    )
}

export default TopTrackStats;