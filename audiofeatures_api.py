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

import pickle
#import io
import numpy as np
import spotipy
# TODO Fix robots.txt
app = Flask(__name__)

client_credentials_manager = client_credentials_manager
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
#@app.route("/api/", methods=['GET', 'POST'])
df = pd.read_csv('SpotifyAudioFeaturesApril2019.csv')

array = df.values
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
    similar_songs.append({'similarity': similarity, 'values': metadata})
  return similar_songs


@app.route("/")
def default():
    body_unicode = request.data.decode('utf-8')
    print(request.get_data())
    #body = json.loads(body_unicode)
    content = request.get_data()
    similarities = all_similarities(song, dfy)
    sorted_list: sorted(similarities, key=lambda i: i['similarity'], reverse=True)[1:51]
    json_dict = {"songs": sorted_list}
    return sorted_list
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
