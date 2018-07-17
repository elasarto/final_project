#importing dependencies

import sys
import spotipy
import spotipy.util as util
from spotipy import oauth2
import json
import os
import re

import pandas as pd
import numpy as np

from matplotlib import pyplot as plt
import seaborn as sns

from sklearn.cluster import KMeans

import hypertools as hyp

from flask import Flask, jsonify, render_template, request, json, redirect, url_for

# Create App
app = Flask(__name__)

scope = 'user-library-read'

username = '7yp23sdg5ptloppevj62zjn6a'

token = util.prompt_for_user_token(username, scope,client_id = "944cef2fde194a8e8d4d5e8db666e020",
                                   client_secret = "52f43621583e4844a4728a5577617f24",
                                   redirect_uri = 'https://example.com/callback/')#, SPOTIPY_REDIRECT_URI)

if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_saved_tracks()
    for item in results['items']:
        track = item['track']
        print (track['name'] + ' - ' + track['artists'][0]['name'])
else:
    print ("Can't get token for", username)

# Returns the dashboard homepage
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/user_dashboard")
def user_dashboard():
    return render_template("user_dashboard.html")

def get_username():
    username = request.values.get('username')
    print(username)
    return username

# in the route name use a variable that will be use in the function, therefre get rid of the 
@app.route("/spotify_user_playlists/<username>") 
# /, methods=['POST']")
def get_playlists(username):

    print(username)

    # username = request.values.get('username', '')
    # print(username)

    # json = request.get_json() request.values.get('input', '')
    # username = json["username"]

    # if request.method == 'POST':
    #     username = request.form['username']
    #     print(username)

        #username = request.form['username']
        #username = input("What's the username?")

    sp = spotipy.Spotify(auth=token)
    playlists = sp.user_playlists(username) 

    playlist_name = []
    playlist_id = []
    playlist_total_songs = []

    for i in playlists['items']:
        playlist_name.append(i['name'])
        playlist_id.append(i['uri'].split("playlist:")[1])
        playlist_total_songs.append(str(i['tracks']['total']))
        
    print(len(playlist_name))
    print(playlist_name)
    print(len(playlist_id))
    print(playlist_id)
    print(len(playlist_total_songs))
    print(playlist_total_songs)

    user_playlists_info = {'Playlist Name' : playlist_name, 'Playlist ID' : playlist_id, 
                    'Playlist_Total_Songs' : playlist_total_songs}

    playlist_info = {}

    playlist_name = []
    playlist_owner = []
    owner_type = []
    playlist_followers = []
    artist_id = []
    artist_name = []
    album_name = []
    song_name = []
    song_id = []
    song_popularity = []

    for p_id in playlist_id:
        #print(p_id)
        try:
            results = sp.user_playlist(username, p_id)
        except Exception:
            print('Cannot find following playlist id: ' + p_id)
            continue
        
        #print(json.dumps(results,indent=4))

        for i in results['tracks']['items']:
            playlist_name.append(results['name'])
            playlist_owner.append(results['owner']['id'])
            owner_type.append(results['owner']['type'])
            playlist_followers.append(results['followers']['total'])
            artist_id.append(i['track']['artists'][0]['id'])
            artist_name.append(i['track']['artists'][0]['name'])
            album_name.append(i['track']['album']['name'])
            song_name.append(i['track']['name'])
            song_id.append(i['track']['id'])
            song_popularity.append(i['track']['popularity'])

    playlists_info = {'Playlist Name' : playlist_name, 'Playlist Owner' : playlist_owner, 'Owner Type' : owner_type, 
                'Playlist Followers' : playlist_followers, 'Artist ID' : artist_id, 'Artist Name' : artist_name,
                'Album Name' : album_name, 'Song Name' : song_name, 'Song ID' : song_id, 'Song Popularity' : song_popularity}

    song_id_2 = []
    danceability = []
    energy = []
    key = []
    loudness = []
    mode = []
    speechiness = []
    acousticness = []
    instrumentalness = []
    liveness = []
    valence = []
    tempo = []
    duration_ms = []

    for s_id in song_id:
        features = sp.audio_features(s_id)
        #print(features)
        #print(json.dumps(features, indent = 4))
        for feature in features:
            song_id_2.append(s_id)
            danceability.append(feature['danceability'])
            energy.append(feature['energy'])
            key.append(feature['key'])
            loudness.append(feature['loudness'])
            mode.append(feature['mode'])
            speechiness.append(feature['speechiness'])
            acousticness.append(feature['acousticness'])
            instrumentalness.append(feature['instrumentalness'])
            liveness.append(feature['liveness'])
            valence.append(feature['valence'])
            tempo.append(feature['tempo'])
            duration_ms.append(feature['duration_ms'])

    songs_info = {'Song ID' : song_id_2,'Danceability' : danceability, 'Energy' : energy, 'Key' : key, 'Loudness' : loudness,
            'Mode' : mode, 'Speechiness' : speechiness, 'Acousticness' : acousticness, 'Instrumentalness' : instrumentalness,
            'Liveness' : liveness, 'Valence' : valence, 'Tempo' : tempo, 'Duration ms' : duration_ms}
    
    return jsonify(user_playlists_info, playlists_info, songs_info)

if __name__ == "__main__":
    app.run(debug=True)