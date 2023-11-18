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
def new_user_playlists():
    # Generate spotify headers to use for Spotify Web API
    headers = get_spotify_headers()

    # Send GET request to retrieve up to 15 of user's playlists
    playlists = get_user_playlists(headers, 0, 15).get('items', [])
    if not playlists:
        return 'No playlists found for this year for the current user.'

    # Find the playlists created by the user this year
    filtered_playlists, total_followers, avg_popularity, artist_counter = filter_and_analyze_playlists(playlists, headers)
    if not filtered_playlists:
        return 'No playlists found for this year for the current user.'
    
    avg_popularity = avg_popularity // len(filtered_playlists)
    top_artists, top_genres = analyze_artists(artist_counter, headers)
    result_data = {
        'annual_user_playlists': filtered_playlists,
        'total_followers': total_followers,
        'avg_popularity': avg_popularity,
        'top_genres': top_genres,
        'top_artists': top_artists
    }

    return jsonify(result_data)


def filter_and_analyze_playlists(playlists, headers):
    # Send GET request to retrieve user's id
    user_id = get_user_info(headers)['id']

    # Initialize variables
    filtered_playlists = []
    total_followers = 0
    avg_popularity = 0
    artist_counter = Counter()

    # Iterate through each playlist
    for playlist in playlists:
        if playlist['owner']['id'] != user_id:
            continue

        # Call the playlist API individual
        playlist_info = get_playlist_info(playlist, headers)

        # Determine if the playlist was created this year
        sorted_tracks = sorted(playlist_info['tracks']['items'], key=lambda x: x['added_at'])
        first_track_added_year = int(sorted_tracks[0]['added_at'][:4])
        current_year = date.today().year
        
        # Skip the rest of the code if the playlist was not created this year
        if first_track_added_year != current_year:
            continue

        # Analyze the playlist
        filtered_playlists.append(playlist)
        total_followers += int(playlist_info['followers']['total'])
        total_popularity = 0

        playlist_tracks = playlist_info['tracks']['items']
        for track in playlist_tracks:
            total_popularity += int(track['track']['popularity'])
            artist = track['track']['artists'][0]
            artist_id = artist['id']
            artist_counter.update({artist_id: 1})
        
        avg_popularity += total_popularity // len(playlist_tracks)
    
    return filtered_playlists, total_followers, avg_popularity, artist_counter    


def analyze_artists(artist_counter, headers):
    top_five_artists = artist_counter.most_common(5)
    artist_ids = [artist[0] for artist in top_five_artists]
    artist_ids_param = ",".join(artist_ids)
    url = f"{API_BASE_URL}artists?ids={artist_ids_param}"
    response = requests.get(url, headers=headers)
    artist_info = response.json()

    top_artists = []
    genre_counter = Counter()
    
    for artist in artist_info['artists']:
        top_artists.append(artist['name'])
        genre_counter.update(artist['genres'])

    top_five_genres = genre_counter.most_common(5)
    top_genres = [genre[0] for genre in top_five_genres]

    return top_artists, top_genres


def get_playlist_info(playlist, headers):
    # Call the playlist API individual
    fields = 'followers.total%2Cname%2Ctracks.items%28added_at%2Ctrack%28artists%28id%2Cname%29%2Cid%2Cname%2Cpopularity%29%29'
    url = f"{playlist['href']}?fields={fields}"
    response = requests.get(url, headers=headers)
    playlist_info = response.json()
    return playlist_info


# def filter_cur_year_playlists_by_user(user_id, headers, playlists):
#     print('getting the annual user playlists...')

#     filtered_playlists = [playlist for playlist in playlists if
#                           user_id == playlist['owner']['id'] and
#                           is_playlist_created_this_year(headers, playlist['id'])]

#     print('found annual user playlists!')
#     return filtered_playlists


# def is_playlist_created_this_year(headers, playlist_id):
#     print('getting if playlist created this year...')

#     current_year = date.today().year
#     playlist_items = get_playlist_items(headers, playlist_id)

#     for track in playlist_items:
#         if track['added_at'] and int(track['added_at'][:4]) < current_year:
#             return False

#     return True


# def analyze_users_playlists(playlists, headers):
#     print('analyzing the playlist results...')

#     total_followers = 0
#     avg_popularity = 0
#     top_artists = []
#     top_genres = []
#     genre_hashmap = {}
#     artist_hashmap = {}

#     # Iterate through each playlist to find the artists, followers, popularity
#     for playlist in playlists:
#         playlist_info = get_playlist(headers, playlist['id'])
#         popularity, followers, artist_hashmap = analyze_playlist(playlist_info, artist_hashmap)
#         total_followers += followers
#         avg_popularity += popularity

#     print('playlists analyzed, artist hashmap created!')

#     # Find the top 5 artists
#     artist_counter = Counter(artist_hashmap)
#     top_five_artists = artist_counter.most_common(5)

#     for (artist_id, artist_name), _ in top_five_artists:
#         top_artists.append(artist_name)
#         artist_genres = get_artist_genres(headers, artist_id)

#         for genre in artist_genres:
#             if genre not in genre_hashmap:
#                 genre_hashmap[genre] = 0
#             genre_hashmap[genre] += 1

#     # Create genre hashmap
#     genre_counter = Counter(genre_hashmap)
#     print(genre_counter)
#     top_five_genres = genre_counter.most_common(5)

#     for genre, _ in top_five_genres:
#         top_genres.append(genre)

#     print('top genres and artists found!')

#     # Calculate the average popularity of all playlists
#     avg_popularity = avg_popularity // len(playlists)

#     result_data = {
#         'annual_user_playlists': playlists,
#         'total_followers': total_followers,
#         'avg_popularity': avg_popularity,
#         'top_genres': top_genres,
#         'top_artists': top_artists
#     }

#     return result_data



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

    return playlist_items


# -----------------------------
# Get User Display Name Route
# -----------------------------
@app.route('/user-display-name')
def user_display_name():
    # Generate spotify headers to use for Spotify Web API
    headers = get_spotify_headers()

    # Send GET request to retrieve user's display name
    user_display_name = get_user_info(headers)['display_name']

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
def get_user_info(headers):
    '''Retrieve a user's id.'''
    url = f"{API_BASE_URL}me"
    response = requests.get(url, headers=headers)
    return response.json()


def get_user_playlists(headers, offset=0, limit=20):
    '''Retrieve a user's playlists'''
    url = f"{API_BASE_URL}me/playlists?offset={offset}&limit={limit}"
    response = requests.get(url, headers=headers)
    return response.json()

    # try:
    #     response = requests.get(url, headers=headers)

    #     # Check for rate limiting
    #     if response.status_code == 429:
    #         print('Rate limited! [429]')

    #     response.raise_for_status()

    #     if response.headers.get("content-type") == "application/json":
    #         return response.json()
    #     else:
    #         print('The response does not contain JSON content')
    #         print(response.text)
    # except Exception as e:
    #     print(f"An error occurred: {e}")

    # return None



# def get_playlist(headers, playlist_id):
#     '''Retrieve a playlist's full details'''
#     url = f"{API_BASE_URL}playlists/{playlist_id}"
#     response = requests.get(url, headers=headers)
#     return response.json()

# def analyze_playlist(playlist, artist_hashmap=None):
#     '''Playlist contains full playlist information and ['items']'''
#     artist_hashmap = {} if artist_hashmap is None else artist_hashmap
#     total_popularity = 0
#     playlist_tracks = playlist['tracks']['items']

#     # Iterate through each track to determine popularity and top artists
#     for track in playlist_tracks:
#         total_popularity += int(track['track']['popularity'])
#         artist = track['track']['artists'][0]
#         artist_id, artist_name = artist['id'], artist['name']
#         if (artist_id, artist_name) not in artist_hashmap:
#             artist_hashmap[(artist_id, artist_name)] = 0
#         artist_hashmap[(artist_id, artist_name)] += 1
    
#     # Find the average popularity and total number of followers
#     avg_popularity = total_popularity // len(playlist_tracks)
#     total_followers = int(playlist['followers']['total'])

#     return avg_popularity, total_followers, artist_hashmap


def get_playlist_items(headers, playlist_id):
    '''Retrieve a playlist's items'''
    url = f"{API_BASE_URL}playlists/{playlist_id}/tracks"
    response = requests.get(url, headers=headers)
    return response.json()['items']


# def get_artist_genres(headers, artist_id):
#     '''Retrieve an artist's associated genres'''
#     url = f"{API_BASE_URL}artists/{artist_id}"
#     response = requests.get(url, headers=headers)
#     return response.json()['genres']


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
