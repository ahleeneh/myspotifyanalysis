import React from 'react';
import { format } from 'date-fns';

function PlaylistTracksComponent({ tracks, image, name, description, onReset }) {
    return (
        <>
            <button onClick={onReset} className="back-button">back to playlists</button>

            <div className="playlist-info-container">
                <>
                    {image && (
                        <img src={image} className="playlist-image" />
                    )}
                </>
                <div className="right-column">
                    <h1>{name}</h1>
                    <p className="grey-text">{description}</p>
                </div>
            </div>

            <div className="playlist-table">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>title</th>
                            <th>album</th>
                            <th>time</th>
                            <th>date added</th>
                            <th>popularity</th>
                        </tr>
                    </thead>

                    <tbody>
                        {tracks.map((song, index) => (
                            <tr key={index} className="border-radius">
                                <td>{index + 1}</td>
                                <td>
                                    <div className="title-container">
                                        <img src={song.track.album.images[0].url} alt="album cover" className="playlist-album-cover" />
                                        <div className="title-right">
                                            <p>{song.track.name}</p>
                                            <p className="grey-text">{song.track.artists[0].name}</p>
                                        </div>
                                    </div>
                                </td>
                                <td>{song.track.album.name}</td>
                                <td>   
                                    {`${Math.floor(song.track.duration_ms / 60000)}:${(song.track.duration_ms % 60000 / 1000 < 10 ? '0' : '')}${(song.track.duration_ms % 60000 / 1000).toFixed(0)}`}
                                </td>
                                <td>{format(new Date(song.added_at), 'MMM d, y')}</td>
                                <td>{song.track.popularity}%</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

        </>
    )
}

export default PlaylistTracksComponent;