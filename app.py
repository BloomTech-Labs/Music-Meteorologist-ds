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

# TODO Fix robots.txt
app = Flask(__name__)
client_credentials_manager = SpotifyClientCredentials(client_id='200f9f0be54b4daab1c2561098b3891a', client_secret='936688039db4402084f44eda09f17ffe')
client_credentials_manager = client_credentials_manager
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
#@app.route("/api/", methods=['GET', 'POST'])
df = pd.read_csv('songmetadata_1.csv')
array = df.values
dfy = pd.read_csv('songtitles_1.csv')

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
    similar_songs.append({'similarity': similarity, 'values': metadata['id']})
  return similar_songs


@app.route("/")
def default():
    body_unicode = request.data.decode('utf-8')
    print(request.get_data())
    # body = json.loads(body_unicode)
    content = request.get_data()
    #song = array[1549]
    song = content['audio_features']
    similarities = all_similarities(song, dfy)
    sorted_list = sorted(similarities, key=lambda i: i['similarity'], reverse=True)[1:3]
    json_dict = {"songs": sorted_list}
    data = json.dumps(json_dict)
    return jsonify(data)


if __name__ == "__main__":
    app.run()
