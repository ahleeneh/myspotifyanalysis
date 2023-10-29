import os
import time
import secrets
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
app.config['SESSION_TYPE'] = 'filesystem'
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
    # Generate a random state value
    state = secrets.token_urlsafe(16)
    print('newly generated state: ', state)

    print('session before stated added: ', session)
    session['oauth_state'] = state
    print('session after state added: ', session)

    # Create a SpotifyOAuth instance and get the authorization URL
    auth_url = create_spotify_oauth().get_authorize_url(state=state)

    print('new authorization url: ', auth_url)
    print('session after getting auth url: ', session)

    # Return the authorization url
    return auth_url


# -----------------------------
# Redirect URI Route
# -----------------------------
@app.route('/redirect-page')
def redirect_page():
    print('')
    print('redirect page function entered:')
    print(request.args)
    print('')
    print('session: ', session)

    # Clear the session
    session.clear()

    # Get the authorization code from the request parameters
    code = request.args.get('code')
    print('authorization code: ', code)

    # Exchange the authorization code for an access/refresh token
    token_info = create_spotify_oauth().get_access_token(code)
    print('here is the token info from the redirect page....', token_info)

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
    token_info = session.get(TOKEN_INFO)
    print(f"Here is the token info: {token_info}")

    if token_info:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        playlists = sp.current_user_playlists()['items']
        return playlists

    else:
        print("USER IS NOT LOGGED IN!!!!")
        abort(401, description="An error occurred")

    # try:
    #     # Get the token info from the session
    #     token_info = get_token()

    #     # Create a Spotipy instance with the access token
    #     sp = spotipy.Spotify(auth=token_info['access_token'])

    #     # Get the user's playlists
    #     playlists = sp.current_user_playlists()['items']

    #     return playlists
    # except Exception as e:
    #     error_message = f"An error occurred: {str(e)}"
    #     abort(401, description=error_message)


# -----------------------------
# Logout Route
# -----------------------------
@app.route('/logout')
def logout():
    # Clear the token info from the session
    session.pop(TOKEN_INFO, None)

    # Clear the session data
    session.clear()

    # Clear client-side cookies
    response = make_response('Logged out successfully')
    print('response is: ', response)
    # Replace with the actual cookie name
    response.delete_cookie('My Spotify Analysis Cookie')

    print('deleted cookie...')
    token_info = session.get(TOKEN_INFO)
    print(f"Here is the token info: {token_info}")

    return response


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
        token_info = spotify_oauth.refresh_access_token(
            token_info['refresh_token'])

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
