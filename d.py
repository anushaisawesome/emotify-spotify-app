from flask import Flask, request, redirect, flash, render_template, jsonify 
import spotipy
import pandas as pd
import numpy as np
import requests
from scipy.spatial import KDTree

app = Flask(__name__)

spotify_access_token = None


@app.route('/fetch_token', methods=['POST'])
def fetch_token():
     global spotify_access_token
     spotify_access_token = request.form['access_token']
     return render_template('plane.html')


@app.route('/')
def home():
    return render_template('home.html')

def get_spotify_client():
    return spotipy.Spotify(auth=spotify_access_token)

def col_range(col):
 return col.max()-col.min()

@app.route('/generate_playlist', methods=['POST'])
def generate_playlist():
    
    sp = get_spotify_client()
    sp.max_retries = 10
    sp.backoff_factor = 0.4
    sp.retries = 10

    data = request.get_json()
    df= pd.read_csv('predicted_valence_arousal.csv')
    valence = data.get('valence')*(col_range(df['predicted_valence'])) + df['predicted_valence'].min()
    arousal = data.get('arousal')*(col_range(df['predicted_arousal'])) + df['predicted_arousal'].min()

    
    tree = KDTree(df[['predicted_valence', 'predicted_arousal']])
    
    def find_nearest_songs(valence, arousal, k=10):
            distances, indices = tree.query([valence, arousal], k=k)
            return df.iloc[indices]['spotify_uri'].tolist()

    nearest_songs = find_nearest_songs(valence, arousal)
    user = sp.current_user()
    user_id = user['id']
    playlist = sp.user_playlist_create(user_id, name='Emotify Playlist', public=True, collaborative=False, description='' )
    playlist_id = playlist['id']
    playlist = sp.playlist_add_items(playlist_id, nearest_songs, position=0)
    
    get_playlist = sp.playlist(playlist_id)
    ext_url = get_playlist['external_urls']
    global playlist_url
    playlist_url = ext_url['spotify']

    return jsonify(success=True)


@app.route('/redirect')
def redirect_page():
    return render_template('redirect.html', playlist_url=playlist_url)


if __name__ == '__main__':
    app.run(debug=True)