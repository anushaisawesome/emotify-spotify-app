import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import SpotifyException
import time
import tensorflow as tf
from keras import layers, Model
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


df = pd.read_csv('muse_with_audio_features.csv')
feature_columns = [col for col in df.columns if col not in ['valence', 'arousal', 'spotify_id']]

X = df[feature_columns].apply(pd.to_numeric, errors='coerce').fillna(0) 
scaler = StandardScaler()
X = scaler.fit_transform(X)

Y = df[['valence', 'arousal']].apply(pd.to_numeric, errors='coerce').fillna(0)


X_train, X_val, Y_train, Y_val = train_test_split(X, Y, test_size=0.2, random_state=42)
def create_model(input_dim):
    model = tf.keras.Sequential([
        layers.Input(shape=(input_dim,)),
        #layers.Dense(256, activation='relu' ),
        #layers.Dense(128, activation='relu'),
        #layers.Dense(64, activation='relu'),
        #layers.Dense(32, activation='relu'),
        layers.Dense(16, activation='relu',),
        #layers.Dense(8, activation='relu'),
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