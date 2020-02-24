import spotipy
import spotipy.util as util
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler, Normalizer
import pandas as pd
from pandas.io.json import json_normalize
from flask import jsonify
from joblib import load, dump
import pickle
import numpy as np


    


def instantiate_sp(token):
    sp = spotipy.Spotify(auth=token)
    return sp

def get_acoustical_features(song_id,sp):
    acoustical_features = sp.audio_features(song_id)[0]
    return acoustical_features

def get_popularity(song_id,sp):
    popularity =  sp.track(song_id)['popularity']
    return popularity

def get_artist_id(song_id,sp):
    artist = sp.track(song_id)['artists'][0]['id']
    return artist

def get_genres(artist,sp):
    genre = sp.artist(artist)['genres']
    return genre

def create_feature_object(popularity, acoustical_features):
    popularity_dict = {'popularity': popularity}
    song_features = acoustical_features
    song_features.update(popularity_dict)
    song_features = {
"audio_features": {
    key: song_features[key] for key in song_features.keys() & {
        'popularity',
        'acousticness',
        'danceability',
        'energy',
        'instrumentalness',
        'key',
        'liveness',
        'loudness',
        'mode',
        'speechiness',
        'tempo',
        'time_signature',
        'valence'}}}

    df = pd.DataFrame.from_dict(json_normalize(song_features["audio_features"]),orient='columns')   
    df = df.reindex(sorted(df.columns), axis=1)
    return df
    
def get_results(song_features_df):
    scaler = load("./models/scalar3.joblib")
    print('Scaling data...')
    data_scaled = scaler.transform(song_features_df)
    normalizer = Normalizer()
    data_normalized = normalizer.fit_transform(data_scaled)
    print('Loading pickled model...')
    model = load('./models/model5.joblib')
    results = model.kneighbors([data_normalized][0])[1:]
    print('Model Raw Results Returned')
    return results[0]
    
def filter_model(model_results,source_genre_list): 
    #loop takes KNN results and filters by source track genres
    print("filter for genres initiated")
    genre_array = pickle.load(open("./data/genres_array_2.pkl","rb"))
    filtered_list = []
    song_list_length = 20
    for output_song_index in model_results[0][1:]:
        output_genre_list = genre_array[output_song_index]
        for output_genre in output_genre_list:
            output_genre = output_genre.strip(" ")
            for source_genre in source_genre_list:
                source_genre = "'" + source_genre + "'"
                if source_genre == output_genre:
                    filtered_list.append(output_song_index)
                else:
                    continue
    if len(set(filtered_list)) > song_list_length:
        print("filter found at least 20 genre matches")
        filtered_list = set(filtered_list)
        filtered_list = list(filtered_list)[0:20]
    else:
        counter = song_list_length - len(set(filtered_list))
        print(len(set(filtered_list)))
        print(counter)
        print(f'need to add {counter} items to final song output')
        for output_song_index in model_results[1:]:
            if output_song_index not in filtered_list:
                if counter > 0:
                    filtered_list.append(output_song_index)
                    counter -= 1
                else:
                    break
    print("Filtered Results with 20 unique song indices returned")
    return filtered_list
    
def song_id_prediction_output(filtered_list): 
    similar_songs = []
    print('song_id_list loading...')
    song_id_array = pickle.load(open('./data/song_id_array3.pkl', 'rb'))
    print('song_id_list loaded')
    for song_row in filtered_list:
        song_id = song_id_array[song_row]
        similar_songs.append({'similarity': [.99], 'values': song_id})
    json_dict = {"songs": similar_songs}
    print("Song IDs Returned")
    return json_dict


def get_user_song_id(sp):
    results = sp.current_user_saved_tracks()
    genre = []
    counter = 0 
    for song_number in range(0,19):
        counter += 1 
        song_id = results['items'][song_number]['track']['id']
        artist_id = get_artist_id(song_id, sp)
        genre = get_genres(artist_id, sp)
        if genre != []:
            break
    return song_id


# def instantiate_sp(token):
#     sp = spotipy.Spotify(auth=token)
#     return sp


# def get_id(sp):
#     results = sp.current_user_saved_tracks()
#     song_id = results['items'][0]['track']['id']
#     return song_id


# def get_features(song_id,sp):
#     results_dict = sp.audio_features(song_id)[0]
#     audio_features = {
#         "audio_features": {
#             key: results_dict[key] for key in results_dict.keys() & {
#                 'danceability',
#                 'energy',
#                 'key',
#                 'loudness',
#                 'mode',
#                 'speechiness',
#                 'acousticness',
#                 'instrumentalness',
#                 'liveness',
#                 'valence',
#                 'tempo',
#                 'time_signature'}}}

#     return audio_features


# def predictfunc(content):
#     similar_songs = []
#     print('Loading dataframe...')
#     dataframe = pd.DataFrame.from_dict(
#         json_normalize(content['audio_features']),
#         orient='columns')
#     print('Dataframe Object Created')
#     print('Loading pickled scaler...')
#     scaler = load('./models/scalar2.joblib')
#     print('Pickled scaler loaded')
#     print('Scaling dataframe object...')
#     dataframe_scaled = scaler.transform(dataframe)
#     print('Dataframe scaled')
#     print('Loading pickled model...')
#     model = load('./models/model2.joblib')
#     print('Model loaded')
#     results = model.kneighbors([dataframe_scaled][0])[1]
#     print('Prediction executed')
#     print('song_id_list loading...')
#     #song_id_list = load('./data/song_id_list2.joblib')
#     # (added 3.4 sec to run time)
#     song_id_list = pickle.load(open('./data/song_id_list2.pkl', 'rb'))
#     print('song_id_list loaded')

#     print('beginning for loop...')
#     for song_row in results[0][1:]:
#         song_id = song_id_list[song_row]
#         similar_songs.append({'similarity': [.99], 'values': song_id})
#     json_dict = {"songs": similar_songs}
#     return json_dict
