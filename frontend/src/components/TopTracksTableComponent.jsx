import React from 'react';

function TopTracksTable({ tracks }) {
    return (
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
                    {tracks.map((song, index) => (
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
    );
}

export default TopTracksTable;