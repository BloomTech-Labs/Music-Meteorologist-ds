from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from flask import request
import pandas as pd
from pandas.io.json import json_normalize
from flask import jsonify
from joblib import load
import pickle

def predictfunc(content):
    similar_songs = []
    print('Loading dataframe...')
    dataframe = pd.DataFrame.from_dict(
        json_normalize(content['audio_features']),
                                orient='columns')
    print('Dataframe Object Created')
    print('Loading pickled scaler...')
    scaler = load('SOUNDDRIP/models/scalar2.joblib')
    print('Pickled scaler loaded')
    print('Scaling dataframe object...')
    dataframe_scaled = scaler.transform(dataframe)
    print('Dataframe scaled')
    print('Loading pickled model...')
    model = load('SOUNDDRIP/models/model2.joblib')
    print('Model loaded')
    results = model.kneighbors([dataframe_scaled][0])[1]
    print('Prediction executed')
    print('song_id_list loading...')
    #song_id_list = load('SOUNDDRIP/data/song_id_list2.joblib') 
    # (added 3.4 sec to run time)
    song_id_list = pickle.load(open('SOUNDDRIP/data/song_id_list2.pkl', 'rb'))
    print('song_id_list loaded')

    print('beginning for loop...')
    for song_row in results[0][1:]:
        song_id = song_id_list[song_row]
        similar_songs.append({'similarity': [.99], 'values': song_id})
    json_dict = {"songs": similar_songs}
    return json_dict
