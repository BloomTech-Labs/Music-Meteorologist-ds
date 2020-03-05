import psycopg2 as ps
from env_vars import *
import spotipy
import spotipy.util as util
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler, Normalizer
import pandas as pd
from pandas.io.json import json_normalize
from flask import jsonify
from joblib import load
import pickle
import numpy as np
from flask import request
from joblib import dump
from joblib import load
import pandas as pd
from importlib import reload
import sys
from env_vars import * 


class Sound_Drip:
    
    def __init__(self, token):
        self.token = token
        self.sp = spotipy.Spotify(auth=self.token)
        self.user_id,self.display_name = self.get_user_ids()
        self.stale_seed_list = self.get_stale_seed()
        self.stale_results_list = self.get_stale_results()
        self.song_id,self.source_genre = self.get_user_song_id_source_genre()
        self.acoustical_features = self.get_acoustical_features(self.song_id)
        self.popularity = self.get_popularity(self.song_id)
        self.song_features_df =  self.create_feature_object(self.popularity,self.acoustical_features)
        self.results = self.get_results(self.song_features_df)
        self.filtered_list = self.filter_model(self.results,self.source_genre)
        self.song_id_predictions = self.song_id_prediction_output(self.filtered_list)
        self.insert_user_predictions(),print("predicts inserted into db")
             

    def get_user_song_id_source_genre(self):
        stale_songs = self.stale_seed_list
        print(stale_songs)
        results = self.sp.current_user_saved_tracks(limit=50)
        print(len(results['items']))
        for song_number in range(0,len(results['items'])):
            print("song number:",song_number)
            song_id = results['items'][song_number]['track']['id']
            print(song_id)
            if song_id not in stale_songs:
                artist_id = self.get_artist_id(song_id)
                print("artist_id:",artist_id)
                genre = self.get_genres(artist_id)
                print("genre:",genre)
                if genre != []:
                    print("the genre is:",genre)
                    break
                else:
                    continue
            else:
                print("not enough songs found")
                if song_number == len(results['items']) - 1:
                    for song_id in stale_songs:
                        print(song_id)
                        artist_id = self.get_artist_id(song_id)
                        genre = self.get_genres(artist_id)
                        if genre != []:
                            print("the genre is:",genre)
                            break
                        else: 
                            continue
                   
        return song_id,genre

    def get_acoustical_features(self,song_id):
        acoustical_features = self.sp.audio_features(song_id)[0]
        return acoustical_features

    def get_popularity(self, song_id):
        popularity =  self.sp.track(song_id)['popularity']
        return popularity

    def get_artist_id(self, song_id):
        artist = self.sp.track(song_id)['artists'][0]['id']
        return artist

    def get_genres(self, artist):
        genre = self.sp.artist(artist)['genres']
        return genre
    
    def create_feature_object(self,popularity, acoustical_features):
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
    
    def get_results(self,song_features_df):
        scaler = load("./models/scalar3.joblib")
        print('Scaling data...')
        data_scaled = scaler.transform(song_features_df)
        normalizer = Normalizer()
        data_normalized = normalizer.fit_transform(data_scaled)
        print('Loading pickled model...')
        model = load('./models/model5.joblib')
        results = model.kneighbors([data_normalized][0])[1:]
        print('results returned')
        return results[0]
    
    def filter_model(self,model_results,source_genre_list): 
        #loop takes KNN results and filters by source track genres
        print(source_genre_list)
        print("filter for genres initiated")
        genre_array = pickle.load(open("./data/genres_array_2.pkl","rb"))
        filtered_list = []
        song_list_length = 20
        stale_results = self.stale_results_list
        model_results_before = len(model_results[0][1:])
        model_results = [index for index in model_results[0][1:] if index not in stale_results]
        model_results_final = model_results_before - len(model_results)
        print(f'{model_results_final} stale tracks were removed for the user')
        for output_song_index in model_results:
            output_genre_list = genre_array[output_song_index]
            for output_genre in output_genre_list:
                output_genre = output_genre.strip(" ")
                for source_genre in source_genre_list:
                    source_genre = "'" + source_genre + "'"
                    if source_genre == output_genre:
                        filtered_list.append(output_song_index)
                    else:
                        continue
        filtered_list = set(filtered_list)
        filtered_list = list(filtered_list)
        if len(filtered_list) > song_list_length:
            print("filter found at least 20 genre matches")
            filtered_list = filtered_list[0:20]
        else:
            counter = song_list_length - len(filtered_list)
            print("length of filtered list:",len(filtered_list))
#             print("counter:",counter)
            print(f'need to add {counter} items to final song output')
            for output_song_index in model_results:
#                 print(output_song_index)
                if output_song_index not in filtered_list:
                    if counter > 0:
                        filtered_list.append(output_song_index)
                        counter -= 1
                    else:
                        break
        print(f"filtered list with {len(filtered_list)} unique song indices returned")
        return filtered_list
    
    def song_id_prediction_output(self,filtered_list): 
        similar_songs = []
        song_id_list = []
        print('song_id_list loading...')
        song_id_array = pickle.load(open('./data/song_id_array3.pkl', 'rb'))
        print('song_id_list loaded')
        for song_row in filtered_list:
            song_id = song_id_array[song_row]
            similar_songs.append({'similarity': [.99], 'values': song_id})
            song_id_list.append(song_id)
        song_result_output_dict = {"songs": similar_songs}
        song_id_and_index_dict = {song_id:song_index for song_id,song_index in zip(song_id_list,filtered_list)}
        print("Results returned")
        return song_result_output_dict,song_id_and_index_dict

    def db_connect(self):
        conn = ps.connect(host=POSTGRES_ADDRESS,
              database=POSTGRES_DBNAME,
              user=POSTGRES_USERNAME,
              password=POSTGRES_PASSWORD,
              port=POSTGRES_PORT)
        cur = conn.cursor()
        return conn,cur
    
    def get_user_ids(self):
        current_user_dict = self.sp.current_user()
        display_name = current_user_dict['display_name']
        user_id = current_user_dict['id']
        print("retrieving user id and display name for current token")
        return user_id, display_name
    
    def insert_user_predictions(self):
        try:
            conn,cur = self.db_connect()
            for song_id,song_index in self.song_id_predictions[1].items():
                        cur.execute(
        'INSERT INTO recommendations'
        '(userid,songid,songlistindex,seedsongid,recdate)'
        f' VALUES (\'{self.user_id}\',\'{song_id}\',\'{song_index}\',\'{self.song_id}\',current_timestamp);')
            conn.commit()
            conn.close()
        except ps.DatabaseError as e:
            print(f'Error {e}')
            sys.exit(1)
        finally:
            if conn:
                conn.close()
        
        
    def get_stale_results(self):
        try:
            conn,cur = self.db_connect()
            query = f'SELECT DISTINCT (songlistindex) FROM recommendations WHERE userid = \'{self.user_id}\';'
            cur.execute(query)
            query_results = cur.fetchall()
            stale_results_list = [index[0] for index in query_results]
        except ps.DatabaseError as e:
            print(f'Error {e}')
            sys.exit(1)
        finally:
            if conn:
                conn.close()
        return stale_results_list
    
    def get_stale_seed(self):
        try:
            conn,cur = self.db_connect()
            query = f'SELECT DISTINCT (seedsongid) FROM recommendations WHERE userid = \'{self.user_id}\' AND seedsongid is not null;'
            cur.execute(query)
            query_results = cur.fetchall()
            stale_results_list = [index[0] for index in query_results]
        except ps.DatabaseError as e:
            print(f'Error {e}')
            sys.exit(1)
        finally:
            if conn:
                conn.close()
        return stale_results_list
            
        
          
            
            