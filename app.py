import os

from flask import (
    Flask,
    render_template,
    request,
    make_response,
)
import requests
import pandas as pd
import json

#import pickle
#import io
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import jsonify
from pandas.io.json import json_normalize

# TODO Fix robots.txt
app = Flask(__name__)
client_credentials_manager = SpotifyClientCredentials(client_id='200f9f0be54b4daab1c2561098b3891a', client_secret='936688039db4402084f44eda09f17ffe')
client_credentials_manager = client_credentials_manager
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
#@app.route("/api/", methods=['GET', 'POST'])
#df = pd.read_csv('songmetadata_1.csv')
#array = df.values
#dfy = pd.read_csv('songtitles_1.csv')
df = pd.read_csv('SpotifyAudioFeaturesApril2019.csv')
df_other = pd.read_csv('SpotifyAudioFeaturesNov2018.csv')
df = df.drop('popularity', 1)
df = df.drop('duration_ms', 1)

df = df.dropna()

df_other = df_other.drop('popularity', 1)
df_other = df_other.drop('duration_ms', 1)

df_other = df_other.dropna()
df = pd.concat([df,df_other]).drop_duplicates().reset_index(drop=True)
dfy = df[['artist_name','track_id', 'track_name']]
df2 = df.drop('artist_name', 1)
df2 = df2.drop('track_id', 1)
df2 = df2.drop('track_name', 1)
array = df2.values

def cosine_similarity(a, b):
  dot_product = np.dot(a,b)
  norm_a = np.linalg.norm(a)
  norm_b = np.linalg.norm(b)
  return dot_product / (norm_a * norm_b)
  #return np.sqrt(np.sum((a - b) ** 2))
def all_similarities(a, dfy):
  similar_songs = []
  for spotify_song, metadata in zip(array, dfy.values):
    similarity = cosine_similarity(a, spotify_song)
    similar_songs.append({'similarity': similarity, 'values': metadata[1]})
  return similar_songs


@app.route("/", methods=['GET', 'POST'])
def default():

    content = request.get_json(silent=True)
    #print("song", content)
    dataframe = pd.DataFrame.from_dict(json_normalize(content['audio_features']), orient='columns')
    #print("dataframe", dataframe)

    song = dataframe.values
    #print("content", song)

    #song = array[1549]
    similarities = all_similarities(song, dfy)
    sorted_list = sorted(similarities, key=lambda i: i['similarity'], reverse=True)[1:3]
    json_dict = {"songs": sorted_list}
    #data = json.dumps(json_dict)
    return jsonify(json_dict)


if __name__ == "__main__":
    app.run()
