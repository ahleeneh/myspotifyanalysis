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

# Spotify Web API URLs
REDIRECT_URI = 'http://localhost:6393/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

# Redirect Front-End URLS
FRONTEND_LOGIN_URL = 'http://localhost:1890'
FRONTEND_REDIRECT_URL = 'http://localhost:1890/user'

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
    return 'Welcome to the My Spotify Analysis Backend! Whatcha doing here?'


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

        # Send POST request to exchange the authorization code for an access/refresh token
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        # Save the token information in the session
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + \
            token_info['expires_in']

        # Redirect the user to the frontend user page
        return redirect(FRONTEND_REDIRECT_URL)


# -----------------------------
# Get User's Playlist Route
# -----------------------------
@app.route('/user-playlists')
def user_playlists():
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

    # Send GET request to retrieve user's id
    user_id = get_user_id(headers)['id']

    print('getting the user id....')

    # Send GET request to retrieve up to 15 of user's playlists
    url = f"{API_BASE_URL}me/playlists?offset=0&limit=15"
    response = requests.get(url, headers=headers)
    playlists = response.json()

    # Find the playlists created by the current user this year
    annual_user_playlists = get_annual_user_playlists(
        user_id, headers, playlists['items'])
    
    print('found annual user playlists!')

    if annual_user_playlists:
        # Analyze the annual_user_playlists to get playlist analysis
        print('analyzing the playlist results...')
        analysis_results = analyze_users_playlists(annual_user_playlists, headers)

        total_followers, avg_popularity, top_genres, top_artists = analysis_results

        result_data = {
            'annual_user_playlists': annual_user_playlists,
            'total_followers': total_followers,
            'avg_popularity': avg_popularity,
            'top_genres': top_genres,
            'top_artists': top_artists
        }

        return jsonify(result_data)
    else:
        return 'No playlists found for this year for current user.'


def get_annual_user_playlists(user_id, headers, playlists):
    print('getting the annual user playlists...')

    annual_user_playlists = []
    current_year = date.today().year

    for playlist in playlists:
        # Determine if the current user created the playlist
        if playlist['owner']['id'] != user_id:
            continue

        # Determine when the playlist was created
        created_year = get_year_playlist_created(headers, playlist)
        if created_year == current_year:
            annual_user_playlists.append(playlist)

    return annual_user_playlists


def get_year_playlist_created(headers, playlist):
    print('getting year created...')
    current_year = date.today().year

    url = f"{playlist['href']}"
    response = requests.get(url, headers=headers)
    playlist_info = response.json()
    playlist_tracks = playlist_info['tracks']['items']

    for track in playlist_tracks:
        if track['added_at'] and int(track['added_at'][:4]) < current_year:
            return int(track['added_at'][:4])

    return current_year


def analyze_users_playlists(playlists, headers):
    total_followers = 0
    avg_popularity = 0
    top_artists = []
    top_genres = []
    genre_hashmap = {}
    artist_hashmap = {}

    for playlist in playlists:
        url = f"{playlist['href']}"
        response = requests.get(url, headers=headers)
        playlist_info = response.json()

        # Increment the number of followers
        total_followers += int(playlist_info['followers']['total'])

        # Iterate through each track in the playlist
        playlist_tracks = playlist_info['tracks']['items']
        total_popularity = 0

        # Iterate through each track to determine popularity and top artists
        for track in playlist_tracks:
            total_popularity += int(track['track']['popularity'])
            artist = track['track']['artists'][0]
            artist_id, artist_name = artist['id'], artist['name']
            if (artist_id, artist_name) not in artist_hashmap:
                artist_hashmap[(artist_id, artist_name)] = 0
            artist_hashmap[(artist_id, artist_name)] += 1

        # Calculate the average popularity of tracks in playlist
        avg_popularity += total_popularity // len(playlist_tracks)

    print('playlists analyzed, artist hashmap created!')

    artist_counter = Counter(artist_hashmap)
    top_five_artists = artist_counter.most_common(5)
    for (artist_id, artist_name), _ in top_five_artists:
        top_artists.append(artist_name)

        artist_url = f"{API_BASE_URL}artists/{artist_id}"
        artist_response = requests.get(artist_url, headers=headers)
        artist_info = artist_response.json()
        artist_genres = artist_info['genres']

        for genre in artist_genres:
            if genre not in genre_hashmap:
                genre_hashmap[genre] = 0
            genre_hashmap[genre] += 1

    genre_counter = Counter(genre_hashmap)
    print(genre_counter)
    top_five_genres = genre_counter.most_common(5)

    for genre, _ in top_five_genres:
        top_genres.append(genre)

    print('top genres and artists found!')

    # Calculate the average popularity of all playlists
    avg_popularity = avg_popularity // len(playlists)

    return total_followers, avg_popularity, top_genres, top_artists


# -----------------------------
# Get Playlist Details Route
# -----------------------------
@app.route('/playlist-tracks')
def playlist_tracks():
    if 'access_token' not in session:
        print('Session expired!')
        return redirect(FRONTEND_LOGIN_URL)

    # Retrieve new refresh token if access token expired
    if datetime.now().timestamp() > session['expires_at']:
        refresh_access_token()

    # Retrieve the playlist Id from the query parameters
    playlist_id = request.args.get('playlistId')

    # Create header to use Spotify Web API
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    # Send GET request to retrieve a playlist's tracks
    url = f"{API_BASE_URL}playlists/{playlist_id}/tracks"
    response = requests.get(url, headers=headers)
    playlist_tracks = response.json()

    return playlist_tracks['items']


# -----------------------------
# Get User Display Name Route
# -----------------------------
@app.route('/user-display-name')
def user_display_name():
    if 'access_token' not in session:
        print('Session expired!')
        return redirect(FRONTEND_LOGIN_URL)

    # Retrieve new refresh token if access token expired
    if datetime.now().timestamp() > session['expires_at']:
        refresh_access_token()

    # Create header to use Spotify Web API
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    # Send GET request to retrieve a playlist's tracks
    url = f"{API_BASE_URL}me"
    response = requests.get(url, headers=headers)
    user_info = response.json()

    return user_info['display_name']

# -----------------------------
# Logout Route
# -----------------------------


@app.route('/logout')
def logout():
    clear_session()
    response = make_response('Logged out!')
    response.delete_cookie('MY SPOTIFY ANALYSIS COOKIE COOKIE!')
    return response


# -----------------------------
# Additional Functions
# -----------------------------
def get_user_id(headers):
    '''
    Retrieve a user's id.
    '''
    url = f"{API_BASE_URL}me"
    response = requests.get(url, headers=headers)
    return response.json()


def refresh_access_token():
    '''
    Exchange a refresh token, if valid, for a new access token.
    '''
    print('Refreshing token!')
    if 'refresh_token' in session and datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        # Send POST request to exchange refresh token for access token
        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        # Store the new access token and expiration information into the user's session
        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + \
            new_token_info['expires_in']
    else:
        return redirect(FRONTEND_LOGIN_URL)


def clear_session():
    '''
    Clear a user's session.
    '''
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
