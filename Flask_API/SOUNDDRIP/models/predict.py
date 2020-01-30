from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from flask import request
import pandas as pd
from pandas.io.json import json_normalize
from flask import jsonify




def predict(content):
    similar_songs = []
    print('Loading dataframe...')
    dataframe = pd.DataFrame.from_dict(
        json_normalize(content['audio_features']),
                                orient='columns')
    print('Dataframe Object Created')
    print('Loading pickled scaler...')
    scaler = pickle.load(open('models/scaler.pkl', 'rb'))
    print('Pickled scaler loaded')
    print('Scaling dataframe object...')
    dataframe_scaled = scaler.transform(dataframe)
    print('Dataframe scaled')
    print('Loading pickled model...')
    model = pickle.load(open('./models/knn_model_v1.pkl', 'rb'))
    print('Model loaded')
    results = model.kneighbors([dataframe_scaled][0])[1]
    print('Prediction executed')
    print('song_id_list loading...')
    song_id_list = pickle.load(open('Flask_API/SOUNDDRIP/data/song_id_list.pkl', 'rb'))
    print('song_id_list loaded')

    print('beginning for loop...')
    for song_row in results[0][1:]:
        song_id = song_id_list[song_row]
        similar_songs.append({'similarity': [.99], 'values': song_id})
    json_dict = {"songs": similar_songs}
    return json_dict
