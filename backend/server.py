import os
import time
import logging
from datetime import timedelta

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect, make_response, abort
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize variables
client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
secret_key = os.environ.get('SECRET_KEY')
scope = 'user-library-read playlist-read-private user-top-read'

# Create Flask application
app = Flask(__name__)

# Allow CORS configuration
CORS(app, supports_credentials=True, origins=['http://localhost:1890'])

# Set the name of the session cookie
app.config['SESSION_COOKIE_NAME'] = 'My Spotify Analysis Cookie'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

# Set a random secret key to sign the cookie
app.secret_key = secret_key

# Set the key for the token info in the session dictionary
TOKEN_INFO = 'token_info'

# -----------------------------
# Home Route
# -----------------------------


@app.route('/')
def home():
    # Return a simple welcome phrase to the backend root
    return 'Welcome to the My Spotify Analysis Backend! Whatcha doing here?'


# -----------------------------
# Home Route
# -----------------------------
@app.route('/authorize')
def authorize():
    # Create a SpotifyOAuth instance and get the authorization URL
    auth_url = create_spotify_oauth().get_authorize_url()

    # Return the authorization url
    return auth_url


# -----------------------------
# Redirect URI Route
# -----------------------------
@app.route('/redirect-page')
def redirect_page():
    # Clear the session
    session.clear()

    # Get the authorization code from the request parameters
    code = request.args.get('code')

    # Exchange the authorization code for an access/refresh token
    token_info = create_spotify_oauth().get_access_token(code)

    # Save the token info in the session
    session[TOKEN_INFO] = token_info

    print('About to redirect the user to the React frontend user home page...')
    frontend_redirect_url = 'http://localhost:1890/user'

    return redirect(frontend_redirect_url)


# -----------------------------
# Get All User's Playlists Route
# -----------------------------
@app.route('/user-playlists')
def user_playlists():
    try:
        # Get the token info from the session
        token_info = get_token()

        # Create a Spotipy instance with the access token
        sp = spotipy.Spotify(auth=token_info['access_token'])

        # Get the user's playlists
        playlists = sp.current_user_playlists()['items']

        return playlists
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        abort(401, description=error_message)


# -----------------------------
# Logout Route
# -----------------------------
@app.route('/logout')
def logout():
    try:
        # Clear the token info from the session
        session.pop(TOKEN_INFO, None)

        # Clear the session data
        session.clear()

        # Clear client-side cookies
        response = make_response('Logged out successfully')
        print('response is: ', response)
        response.delete_cookie('My Spotify Analysis Cookie')  # Replace with the actual cookie name

        print('deleted cookie...')

        return response
    except Exception as e:
        logging.error(f"Error during logout: {str(e)}")

        return 'An error occurred during log out', 500


# -----------------------------
# Additional Functions
# -----------------------------
def get_token():
    # Get the token info from the session
    token_info = session.get(TOKEN_INFO, None)
    print(token_info)
    print('^^^^ token info above')

    # If no token is found, return an error!!!
    if not token_info:
        raise Exception('Authentication error: Please log in.')

    # Check if the token is expired and refresh if necessary
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info



def create_spotify_oauth():
    # Create and return a SpotifyOAuth object
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=url_for('redirect_page', _external=True),
        scope=scope
        )


if __name__ == '__main__':
    app.run(port=6393, debug=True)
