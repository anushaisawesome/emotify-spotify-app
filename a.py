from IPython.display import Audio
import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import SpotifyException
import time



#spotify_cid = '9ab9dcbc306a43af8029c32ca95de9e9'
#spotify_secret = '18962569c33c4039855a05a6a3c8b7ff'

spotify_access_token ='BQDW71t88XYfwa5Lh3vLKlB8SsSk11t2XnHmxnTj8JRvdJTxFeM9lzvDVL7Yjgii9j7_A4Og0a0cRjUgfkMkaJwCFZk4pO8vaTc3ToQkKA9g2zSPyTPl3-hnOSE1kxCpMmhG2roQobaTZqDykuNzUU8N6g5EAm7NVyWlUhQapt0wIwxRwkb9FJHAX-0XgeZEtpCAsW6wuFjLdjjKYbJoFb_bDWzU4Y-sEk1aFsQKv1rI2_AtXCailOLBdMNOBVHq_npVP9ltsfXnxI7Jvv84m2fxlpKx3OpV2QOWxlbJEOG-YPHtFtqAO64nhJX2kQkra-Lxo1wo9gVE6oJ98Jq7pmDwg0LxYHTfRFYk6ooQdNSvkEZ6olJ_dH6R5I9-GQ'
spotify = spotipy.Spotify(auth=spotify_access_token)
spotify.max_retries = 10
spotify.backoff_factor = 0.4
spotify.retries = 10

df = pd.read_csv('muse_v3.csv')
df = df[['spotify_id', 'valence_tags', 'arousal_tags']].dropna(subset=['spotify_id'])

processed_data = []

batch_size = 50  
spotify_ids = df['spotify_id'].tolist()

for i in range(0, len(spotify_ids), batch_size):
    batch = spotify_ids[i:i + batch_size]
    
    try:
        audio_features = spotify.audio_features(batch)
        
        for j, features in enumerate(audio_features):
            if features:
                processed_data.append({
                    'spotify_id': batch[j],
                    'valence': df.iloc[i + j]['valence_tags'],
                    'arousal': df.iloc[i + j]['arousal_tags'],
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


processed_df = pd.DataFrame(processed_data)
processed_df.to_csv('muse_with_audio_features.csv', index=False)

print("Processing complete! Saved as 'muse_with_audio_features.csv'")