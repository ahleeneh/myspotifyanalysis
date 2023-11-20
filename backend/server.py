# Implement's Spotify's Web API: https://developer.spotify.com/documentation/web-api
# Create Flask application: https://code.visualstudio.com/docs/python/tutorial-flask


import os
import requests
import secrets
import urllib.parse
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
from flask import Flask, redirect, request, jsonify, session, make_response
from flask_cors import CORS
from collections import Counter

# Load environment variables from the .env file
load_dotenv()

# Initialize variables
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
SECRET_KEY = os.environ.get('SECRET_KEY')
REDIRECT_URI = os.environ.get('REDIRECT_URI')
AUTH_URL = os.environ.get('AUTH_URL')
TOKEN_URL = os.environ.get('TOKEN_URL')
API_BASE_URL = os.environ.get('API_BASE_URL')

# Redirect Front-End URLS
FRONTEND_LOGIN_URL = 'http://localhost:1890'
FRONTEND_REDIRECT_URL = 'http://localhost:1890/user'

# Other constants
NO_PLAYLISTS_FOUND_MSG = 'No playlists found for this year for the current user.'
PLAYLIST_OFFSET = 0
PLAYLIST_LIMIT = 15

# Create Flask application
app = Flask(__name__)

# Allow CORS configuration
CORS(app, supports_credentials=True)

# Configure session key
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_NAME'] = 'MY SPOTIFY ANALYSIS COOKIE COOKIE!'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)


# -----------------------------
# Home Route
# -----------------------------
@app.route('/')
def home():
    # Return a simple welcome phrase to the backend root
    return 'Welcome to the My Spotify Analysis Backend! What are you doing here?'


# -----------------------------
# Authorize Route
# -----------------------------
@app.route('/authorize')
def authorize():
    # Clear the user's session
    clear_session()

    # Generate state for session and OAuth
    state = secrets.token_hex(16)
    session['state'] = state

    # Create query parameters to request user authorization
    scope = 'user-library-read playlist-read-private user-top-read'
    query_params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'state': state,
        'scope': scope,
        'show_dialog': True
    }

    # Create authorization url from query parameters
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(query_params)}"

    # Return the authorization url to the frontend
    return auth_url


# -----------------------------
# Callback Route
# -----------------------------
@app.route('/callback')
def callback():
    if 'error' in request.args:
        # Check if an error is in the request arguments
        return jsonify({'Error: ', request.args['error']})

    if 'code' in request.args:
        # Determine if the states are the same
        received_state = request.args.get('state')
        stored_session_state = session.get('state')

        if received_state != stored_session_state:
            return 'Invalid state parameters! Possible CSRF attack!'

        # Create request body parameters to request access token
        req_body = {
            'grant_type': 'authorization_code',
            'code': request.args['code'],
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        token_info = exchange_token(req_body)
        save_token_information(token_info)

        # Redirect the user to the frontend user page
        return redirect(FRONTEND_REDIRECT_URL)


# -----------------------------
# Get User's Playlist Route
# -----------------------------
@app.route('/user-playlists')
def user_playlists():
    '''
    Determine the playlists created by the user this year and an analysis
    including the total followers, average popularity, top genres and artists.
    '''
    headers = get_spotify_headers()
    playlists = get_current_user_playlists(
        headers, PLAYLIST_OFFSET, PLAYLIST_LIMIT).get('items', [])

    # Check if there are no playlists found
    if not playlists:
        return NO_PLAYLISTS_FOUND_MSG

    user_id = get_current_user_profile(headers)['id']
    result_data = analyze_users_playlists(playlists, headers, user_id)

    if result_data == NO_PLAYLISTS_FOUND_MSG:
        return result_data
    return jsonify(result_data)


def analyze_users_playlists(playlists, headers, user_id):
    '''
    Find the playlists created by the current user this year and the
    total followers, average popularity, top 5 genres, and top 5 artists.
    '''
    current_yr_playlists = []
    total_followers = 0
    avg_popularity = 0
    artist_counter = Counter()

    for playlist in playlists:
        if playlist['owner']['id'] != user_id:
            continue

        # Retrieve a playlist's details
        playlist_info = get_specific_playlist_details(headers, playlist)

        if not is_playlist_created_this_year(playlist_info):
            continue

        # Analyze the playlist
        playlist_popularity, playlist_followers, artist_counter = analyze_individual_playlist(
            playlist_info, artist_counter)
        avg_popularity += playlist_popularity
        total_followers += playlist_followers
        current_yr_playlists.append(playlist)

    if not current_yr_playlists:
        return NO_PLAYLISTS_FOUND_MSG

    avg_popularity = avg_popularity // len(current_yr_playlists)
    top_artists, top_genres = get_top_artists_genres_from_artists(
        headers, artist_counter)

    return {
        'annual_user_playlists': current_yr_playlists,
        'total_followers': total_followers,
        'avg_popularity': avg_popularity,
        'top_genres': top_genres,
        'top_artists': top_artists
    }


def analyze_individual_playlist(playlist, artist_counter):
    '''Determine a playlist's popularity, followers, and updates artist Counter.'''
    popularity = 0
    followers = int(playlist['followers']['total'])
    tracks = playlist['tracks']['items']

    for track in tracks:
        popularity += int(track['track']['popularity'])
        artist_id = track['track']['artists'][0]['id']
        artist_counter.update({artist_id: 1})

    popularity = popularity // len(tracks) if tracks else popularity

    return popularity, followers, artist_counter


def is_playlist_created_this_year(playlist):
    '''Return a boolean value determining if the playlist was created this year.'''
    sorted_tracks = sorted(
        playlist['tracks']['items'], key=lambda x: x['added_at'])
    first_track_added_year = int(sorted_tracks[0]['added_at'][:4])
    current_year = date.today().year
    return first_track_added_year == current_year


def get_top_artists_genres_from_artists(headers, artist_counter):
    '''Determine the top 5 artists and top 5 genres from an artist Counter.'''
    artist_ids = ",".join([artist[0]
                          for artist in artist_counter.most_common(5)])
    artist_info = get_several_artists(headers, artist_ids)
    top_artists = []
    genre_counter = Counter()

    for artist in artist_info['artists']:
        top_artists.append(artist['name'])
        genre_counter.update(artist['genres'])

    top_genres = [genre[0] for genre in genre_counter.most_common(5)]
    return top_artists, top_genres


# -----------------------------
# Get Playlist Details Route
# -----------------------------
@app.route('/playlist-tracks')
def playlist_tracks():
    # Generate spotify headers to use for Spotify Web API
    headers = get_spotify_headers()

    # Retrieve the playlist Id from the query parameters
    playlist_id = request.args.get('playlistId')

    # Send GET request to retrieve a playlist's items
    playlist_items = get_playlist_items(headers, playlist_id)

    return jsonify(playlist_items.get('items', []))


# -----------------------------
# Get User's Top Items
# -----------------------------
@app.route('/top-items')
def top_items():
    # Generate spotify headers to use for Spotify Web API
    headers = get_spotify_headers()

    # Retrieve the itemType, timeRange, and limit from the query parameters
    item_type = request.args.get('itemType')
    time_range = request.args.get('timeRange')
    limit = request.args.get('limit')

    # Send GET request to retrieve a user's top items
    top_items = get_users_top_items(headers, item_type, time_range, limit)

    # Add audio feature analysis for top tracks
    if top_items and item_type == 'tracks':
        ids = ",".join([item['id'] for item in top_items.get('items', [])])
        audio_features = get_several_tracks_audio_features(
            headers, ids).get('audio_features', [])
        stats = calculate_average_statistics(audio_features)
        top_items['stats'] = stats

    return jsonify(top_items)


def calculate_average_statistics(audio_features):
    num_tracks = len(audio_features)

    keys = ['acousticness', 'danceability', 'energy',
            'instrumentalness', 'speechiness', 'valence']
    sum_features = {key: 0 for key in keys}

    for audio in audio_features:
        for key in keys:
            sum_features[key] += float(audio[key])

    average_features = {
        key: int(round(sum_features[key] / num_tracks, 2) * 100) for key in keys}
    return average_features


# -----------------------------
# Get User Display Name Route
# -----------------------------
@app.route('/user-display-name')
def user_display_name():
    # Generate spotify headers to use for Spotify Web API
    headers = get_spotify_headers()

    # Send GET request to retrieve user's display name
    user_display_name = get_current_user_profile(headers)['display_name']

    return user_display_name


# -----------------------------
# Logout Route
# -----------------------------
@app.route('/logout')
def logout():
    # Clear a user's session
    clear_session()

    # Delete cookie
    response = make_response('Logged out!')
    response.delete_cookie('MY SPOTIFY ANALYSIS COOKIE COOKIE!')

    return response


# -----------------------------
# Spotify Web API Functions
# -----------------------------
def get_current_user_profile(headers):
    '''Retrieve the current user's profile.'''
    url = f"{API_BASE_URL}me"
    response = requests.get(url, headers=headers)
    return response.json()


def get_current_user_playlists(headers, offset=0, limit=20):
    '''Retrieve a user's playlists'''
    url = f"{API_BASE_URL}me/playlists?offset={offset}&limit={limit}"
    response = requests.get(url, headers=headers)
    return response.json()


def get_playlist(headers, playlist_id):
    '''Retrieve a playlist's full details'''
    url = f"{API_BASE_URL}playlists/{playlist_id}"
    response = requests.get(url, headers=headers)
    return response.json()


def get_specific_playlist_details(headers, playlist):
    '''
    Retrieve a playlist with the following fields: followers.total,
    name, tracks.items(added_at, track, name, popularity, artists(id, name))
    '''
    fields = 'followers.total%2Cname%2Ctracks.items%28added_at%2Ctrack%28artists%28id%2Cname%29%2Cid%2Cname%2Cpopularity%29%29'
    url = f"{playlist['href']}?fields={fields}"
    response = requests.get(url, headers=headers)
    playlist_info = response.json()
    return playlist_info


def get_playlist_items(headers, playlist_id):
    '''Retrieve a playlist's tracks'''
    url = f"{API_BASE_URL}playlists/{playlist_id}/tracks"
    response = requests.get(url, headers=headers)
    return response.json()


def get_several_artists(headers, artist_ids):
    '''Retrieve several artist's full details'''
    url = f"{API_BASE_URL}artists?ids={artist_ids}"
    response = requests.get(url, headers=headers)
    return response.json()


def get_users_top_items(headers, item_type, time_range, limit=20):
    '''Retrieve the current user's top artists or tracks based on calculated affinity.'''
    url = f"{API_BASE_URL}me/top/{item_type}?time_range={time_range}&limit={limit}"
    response = requests.get(url, headers=headers)
    return response.json()


def get_several_tracks_audio_features(headers, track_ids):
    '''Retrieve the audio features for multiple tracks based on their IDs.'''
    url = f"{API_BASE_URL}audio-features?ids={track_ids}"
    response = requests.get(url, headers=headers)
    return response.json()


# -----------------------------
# Helper OAuth2 Functions
# -----------------------------
def get_spotify_headers():
    if 'access_token' not in session:
        print('Session expired!')
        return redirect(FRONTEND_LOGIN_URL)

    # Retrieve new refresh token if access token expired
    if datetime.now().timestamp() > session['expires_at']:
        refresh_access_token()

    # Create header and query params to use Spotify Web API
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    return headers


def exchange_token(req_body):
    '''Exchange an authorization code or refresh token for a new access token.'''
    response = requests.post(TOKEN_URL, data=req_body)
    return response.json()


def save_token_information(token_info):
    '''Save the token information in the session.'''
    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    session['expires_at'] = datetime.now().timestamp() + \
        token_info['expires_in']


def refresh_access_token():
    '''Exchange a refresh token, if valid, for a new access token.'''
    print('Refreshing token!')

    if 'refresh_token' in session and datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        # Exchange refresh token for access token and store new information into user's session
        new_token_info = exchange_token(req_body)
        save_token_information(new_token_info)
    else:
        return redirect(FRONTEND_LOGIN_URL)


def clear_session():
    '''Clear a user's session.'''
    if 'access_token' in session:
        session.pop('access_token')
    if 'refresh_token' in session:
        session.pop('refresh_token')
    if 'expires_at' in session:
        session.pop('expires_at')
    if 'state' in session:
        session.pop('state')


# -----------------------------
# Start Flask Application
# -----------------------------
if __name__ == '__main__':
    app.run(port=6393, debug=True)
