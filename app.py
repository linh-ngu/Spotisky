import re
from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import tekore as tk
from pprint import pprint
import sys

#defining consts
CLIENT_ID = "b3d8a81abd2c44da92c119308d490849"
CLIENT_SECRET = "d9544c2e106946f5b73b336ce5460b79"

app = Flask(__name__)

app.secret_key = 'aldkfjalkdjflakdfj'
app.config['SESSION_COOKIE_NAME'] = 'Spotisky Cookie'
TOKEN_INFO = 'token_info'


def create_spotify_auth():
    return SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = url_for('redirectPage', _external = True),
        scope = 'user-top-read'
    )

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    sp_auth = create_spotify_auth()
    auth_url = sp_auth.get_authorize_url()
    return redirect(auth_url)

@app.route("/redirect")
def redirectPage():
    sp_auth = create_spotify_auth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_auth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('getTracks', _external = True))

def getSongCode(sp):
    songArray = []
    for i in range(10):
        spot = sp.current_user_top_tracks(limit=10, offset=0, time_range='medium_term')['items'][i] #splits top ten dict by index
        song = spot.get('external_urls')
        s = song.get('spotify')[31:] #chops string to get code only
        songArray.append(s)
    return songArray

def getFeatures(sp):
    songs = getSongCode(sp)
    features = sp.audio_features(tracks = songs)
    return features

#song at index zero of songArray is sun
def categorizeData(sp):
    data = {
        'danceability':[],
        'energy':[],
        'tempo':[],
        'loudness':[]
    }
    features = getFeatures(sp)
    for i in range(1,10):
        f = features[i]
        data['danceability'].append(f["danceability"])
        data['energy'].append(f["energy"])
        data['tempo'].append(f["tempo"])
        data['loudness'].append(f["loudness"])
    return data

def risingSign(sp):
    songList = getSongCode(sp)
    d = categorizeData(sp)
    rising_list = []
    risingData = d["danceability"]

    danceMax = max(risingData)
    danceIndex = risingData.index(danceMax)

    song = "spotify:track:"+songList[danceIndex + 1]
    track = sp.track(song)
    rising_list.append(track.get('name'))
    rising_list.append(track['album']['artists'][0]['name'])
    imageData = track['album']['images'][0]
    rising_list.append(imageData.get('url'))

    return rising_list


def sunSign(sp):
    sun_list = []
    songList = getSongCode(sp)
    songData = sp.current_user_top_tracks(limit=10, offset=0, time_range='medium_term')['items'][0]
    sun_list.append(songData.get('name'))
    sun_list.append(songData['album']['artists'][0]['name'])
    imageData = songData['album']['images'][0]
    sun_list.append(imageData.get('url'))
    
    return sun_list

def moonSign(sp):
    songList = getSongCode(sp)
    d = categorizeData(sp)
    moon_list = []
    moonData = d["energy"]
    
    minimum = min(moonData)
    index = moonData.index(minimum)
    
    song = "spotify:track:"+songList[index + 1]
    track = sp.track(song)
    moon_list.append(track.get('name'))
    moon_list.append(track['album']['artists'][0]['name'])
    imageData = track['album']['images'][0]
    moon_list.append(imageData.get('url'))
    
    return moon_list



def venusSign(sp):
    songList = getSongCode(sp)
    d = categorizeData(sp)
    venus_list = []
    venusData = d["tempo"]

    tempoMin = min(venusData)
    tempoIndex = venusData.index(tempoMin)

    song = "spotify:track:"+songList[tempoIndex + 1]
    track = sp.track(song)
    venus_list.append(track.get('name'))
    venus_list.append(track['album']['artists'][0]['name'])
    imageData = track['album']['images'][0]
    venus_list.append(imageData.get('url'))

    return venus_list


def marsSign(sp):
    songList = getSongCode(sp)
    d = categorizeData(sp)
    mars_list = []
    marsData = d["loudness"]

    loudMax = min(marsData)
    loudIndex = marsData.index(loudMax)

    song = "spotify:track:"+songList[loudIndex + 1]
    track = sp.track(song)
    mars_list.append(track.get('name'))
    mars_list.append(track['album']['artists'][0]['name'])
    imageData = track['album']['images'][0]
    mars_list.append(imageData.get('url'))

    return mars_list


@app.route("/getTracks")
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect(url_for('login', _external = False))

    sp = spotipy.Spotify(auth = token_info['access_token'])
    getSongCode(sp)
    getFeatures(sp)
    categorizeData(sp)
    signDict = [
        risingSign(sp),
        sunSign(sp),
        moonSign(sp),
        venusSign(sp),
        marsSign(sp)
    ]
    return render_template('base.html', data = signDict)


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now <= 100
    if (is_expired):
        sp_auth = create_spotify_auth()
        token_info = sp_auth.refresh_access_token(token_info['refresh_token'])
    return token_info


app.run()