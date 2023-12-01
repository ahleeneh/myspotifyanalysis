import React, { useState, useEffect } from 'react';
import axios from 'axios';

function SidebarHomeComponent({ displayName }) {
    const [musicEmoji, setMusicEmoji] = useState(null);

    const getRandomEmoji = async () => {
        try {
            const emojisList = [
                'studio microphone', 'headphone', 'mirror ball', 'speaker high volume'
            ]

            const randomEmoji = emojisList[Math.floor(Math.random() * emojisList.length)];

            const response = await axios.get(`https://emoji-microservice-c2d2e08d1329.herokuapp.com/fetch-emoji?name=${randomEmoji}`)

            setMusicEmoji(response.data.emoji);

        } catch (error) {
            console.error('Error getting emoji:', error)
        }
    }

    useEffect(() => {
        getRandomEmoji()
    }, []);

    return (
        <>
            <h2>my Spotify analysis</h2>
            <p>{musicEmoji} {displayName}</p>
        </>
    )
}

export default SidebarHomeComponent;