import './LoginPage.css';
import React from 'react';
import axios from 'axios';
import spotifyLogo from '../../assets/spotify/Spotify_Icon_RGB_White.png';
import flower from '../../images/flower.png';
import cliff from '../../images/cliff.png';
import dawn from '../../images/dawn.png';
import sea from '../../images/sea.png';

function LoginPage() {
    const handleSpotifyLogin = async () => {
        try {
            const response = await axios.get('http://localhost:6393/authorize', {
                withCredentials: true
            });

            const authorizationUrl = response.data;
            console.log(authorizationUrl);

            window.location.href = authorizationUrl;
        } catch (error) {
            console.error("Error: ", error)
        }
    }


    return (
        <div className="login-page">
            <div className="login-page-container">
                <h1>my Spotify analysis</h1>

                <p>Log in with your Spotify account to see your custom music analysis.</p>

                <button id="button-spotify-login" onClick={handleSpotifyLogin}>
                    <img src={spotifyLogo} alt="Spotify Logo" id="spotify-icon" />
                    <p>Log in with Spotify</p>
                </button>

                <div className="features-container">
                    <div className="feature-card">
                        <img src={flower} className="card-image" />
                        <h2>playlists '23</h2>
                        <p>explore your annual playlists</p>
                    </div>

                    <div className="feature-card">
                        <img src={dawn} className="card-image" />
                        <h2>top tracks</h2>
                        <p>long-term, 6 months, 4 weeks</p>
                    </div>

                    <div className="feature-card">
                        <img src={sea} className="card-image" />
                        <h2>top artists</h2>
                        <p>long-term, 6 months, 4 weeks</p>
                    </div>
                </div>
            </div>

        </div>
    );
    
}

export default LoginPage;