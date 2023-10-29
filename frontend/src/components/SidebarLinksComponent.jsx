import React from 'react';
import { useNavigate } from 'react-router-dom';
import flower from '../images/flower.png';
import cliff from '../images/cliff.png';
import dawn from '../images/dawn.png';
import sea from '../images/sea.png';
import axios from 'axios';


function SidebarLinksComponent({ onSelectLink, selectedLink }) {
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            const response = await axios.get('http://localhost:6393/logout', {
                withCredentials: true
            })

            console.log('return from response!!!')
            console.log(response.data);

            navigate('/');
        } catch (error) {
            console.error('Error: ', error)
        }
    }

    return (
        <>
            <div className="link-top">
                <h2>your analysis</h2>
                <div className={`link-card ${selectedLink === 'user-playlists' ? 'active' : ''}`} onClick={() => onSelectLink('user-playlists')}>
                    <img src={flower} className="link-image" />
                    <div className="link-card-text">
                        <h3>playlists '23</h3>
                        <p>explore your annual playlists</p>
                    </div>
                </div>

                <div className={`link-card ${selectedLink === 'top-tracks' ? 'active' : ''}`} onClick={() => onSelectLink('top-tracks')}>
                    <img src={dawn} className="link-image" />
                    <div className="link-card-text">
                        <h3>top tracks</h3>
                        <p>top artists: 4 weeks, 6 months, all-time</p>
                    </div>
                </div>

                <div className={`link-card ${selectedLink === 'top-artists' ? 'active' : ''}`} onClick={() => onSelectLink('top-artists')}>
                    <img src={cliff} className="link-image" />
                    <div className="link-card-text">
                        <h3>top artists</h3>
                        <p>top songs: 4 weeks, 6 months, all-time</p>
                    </div>
                </div>

                <div className={`link-card ${selectedLink === 'recommended' ? 'active' : ''}`} onClick={() => onSelectLink('recommended')}>
                    <img src={sea} className="link-image" />
                    <div className="link-card-text">
                        <h3>recommended</h3>
                        <p>view artists, songs, and genres for you</p>
                    </div>
                </div>

            </div>
            
            <div className="link-bottom">
                <button onClick={handleLogout} id="button-logout">Logout</button>
            </div>

        </>
    )
}

export default SidebarLinksComponent;