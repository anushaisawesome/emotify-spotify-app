from IPython.display import Audio
import pandas as pd
import numpy as np
import sqlite3
import spotipy
from spotipy import SpotifyException
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy import client
import time

spotify_access_token ='BQCxTajCoz-vn15WxHajByHaaZdRlA2etplVxQk6vU_QFjrmrA8sp9bPrp0GOZQKkz_b2qI9gTUUk9CwGzNH3ZFQyQsMF78WAT-01MCuggk4VpFQSycto-6mSFOC1ut1D0ehlIkJvRQwTay1BLxG_BpO0sRaBuNczbmccYvPACbqJ0c81ikw3Q9Nxl8mCZ5FE2mcYI2fsxA6nj766iUM-6RsnDOMhPqKdFfRAGmNLNIO9DmYPRBanpdB0OMzF7fsuMKZjpuxAy7CmWOOtt4asDMDpdHBPaySNFnN_5ZPt1SHsLNeKi1aVwTphrtZvKpoIX1Wq4Mh1R2zR3yUXQVJtMGvUnVWQk4woCDLdg_A-RCA-fV2ZMdfq_wHoE4AkA'
sp = spotipy.Spotify(auth=spotify_access_token)
sp.max_retries = 10
sp.backoff_factor = 0.4
sp.retries = 10


batch_size = 20
tracks = []


for i in range(0, 2000, batch_size):
    fetch_tracks = sp.current_user_top_tracks(limit=batch_size, offset=i, time_range='long_term' )

    for item in fetch_tracks['items']:
        track = item
        tracks.append({
            'spotify_uri' : track['uri'],
            'name' : track['name']
        })
    

tracks_df = pd.DataFrame(tracks)
tracks_df.to_csv('tracks.csv', index=False)

spotify_uris = tracks_df['spotify_uri'].to_list()
X_test_spotify = []

for i in range(0, 2000, 50):
    batch = spotify_uris[i:i + 50]
    
    try:
        audio_features = sp.audio_features(batch)
        
        for j, features in enumerate(audio_features):
            if features:
                X_test_spotify.append({
                    'spotify_uri': batch[j],
                    'time_signature': features['time_signature'],
                    'mode': features['mode'],
                    'key': features['key'],
                    'danceability': features['danceability'],
                    'energy': features['energy'],
                    'tempo': features['tempo'],
                    'loudness': features['loudness'],
                    'acousticness': features['acousticness'],
                    'instrumentalness': features['instrumentalness'],
                    'liveness': features['liveness'],
                    'speechiness': features['speechiness'],
                })
    
    except SpotifyException as e:
        print(f"Spotify API error at batch {i}: {e}")
        time.sleep(5)  

x_df = pd.DataFrame(X_test_spotify)
x_df.to_csv('X_test_spotify.csv', index=False)





