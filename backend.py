from flask import Flask, request, redirect, flash, render_template, jsonify 
import pandas as pd
import numpy as np
import spotipy
from spotipy import SpotifyException
import time
import tensorflow as tf
from keras import layers, Model
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
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


    
    ############################################### c.py starts here #######################################################


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



    ############################################### c.py ends here #######################################################


    ############################################### b.py starts here #######################################################
    

    m_df = pd.read_csv('muse_with_audio_features.csv')
    feature_columns = [col for col in m_df.columns if col not in ['valence', 'arousal', 'spotify_id']]

    X = m_df[feature_columns].apply(pd.to_numeric, errors='coerce').fillna(0) 
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    Y = m_df[['valence', 'arousal']].apply(pd.to_numeric, errors='coerce').fillna(0)


    X_train, X_val, Y_train, Y_val = train_test_split(X, Y, test_size=0.2, random_state=42)
    def create_model(input_dim):
        model = tf.keras.Sequential([
            layers.Input(shape=(input_dim,)),
            #layers.Dense(256, activation='relu' ),
            #layers.Dense(128, activation='relu'),
            #layers.Dense(64, activation='relu'),
            #layers.Dense(32, activation='relu'),
            layers.Dense(16, activation='relu',),
            layers.Dense(8, activation='relu'),
            #layers.Dropout(0.3),
            layers.Dense(2, activation='relu'),
            layers.Dense(2, activation='linear') 
        ])
        return model

    input_dim = X_train.shape[1]
    model = create_model(input_dim)

    model.compile(optimizer= tf.keras.optimizers.Adam(learning_rate=0.0025), loss='mse')

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=3,
        restore_best_weights=True
    )

    history = model.fit(
        X_train, Y_train,
        epochs=600, batch_size=64,
     validation_data=(X_val, Y_val),
    )
    #val_loss, val_mae = model.evaluate(X_val, Y_val)
    #print(f"Validation Loss: {val_loss:.4f}, Validation MAE: {val_mae:.4f}")

    val_loss = model.evaluate(X_val, Y_val)
    print(f"Validation Results: {val_loss:.4f}")

    model.save("valence_arousal_model.keras")

    loaded_model = tf.keras.models.load_model("valence_arousal_model.keras")


    X_test_spotify = pd.read_csv('X_test_spotify.csv') 
    spotify_uris = X_test_spotify['spotify_uri'] 
    ft_columns = [col for col in X_test_spotify.columns if col not in ['spotify_uri']]
    X_test_spotify = X_test_spotify[ft_columns].apply(pd.to_numeric, errors='coerce').fillna(0) 
    X_test_spotify = scaler.transform(X_test_spotify)

    predictions = loaded_model.predict(X_test_spotify)

    results_df = pd.DataFrame({
        'spotify_uri': spotify_uris,
        'predicted_valence': predictions[:, 0], 
        'predicted_arousal': predictions[:, 1]   
    })

    results_df.to_csv('predicted_valence_arousal.csv', index=False)
    
    
    ############################################### b.py ends here #######################################################
    
    
    
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










