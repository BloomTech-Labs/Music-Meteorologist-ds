import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler, Normalizer
import pandas as pd
from pandas.io.json import json_normalize
from joblib import load, dump
import pickle
import numpy as np

class Sound_Drip:
    
    def __init__(self, token):
        self.token = token
        self.sp = spotipy.Spotify(auth=self.token)
        self.song_id,self.source_genre = self.get_user_song_id_source_genre()
        self.acoustical_features = self.get_acoustical_features(self.song_id)
        self.popularity = self.get_popularity(self.song_id)
        self.song_features_df =  self.create_feature_object(self.popularity,self.acoustical_features)
        self.results = self.get_results(self.song_features_df)
        self.filtered_list = self.filter_model(self.results,self.source_genre)
        self.song_id_predictions = self.song_id_prediction_output(self.filtered_list) 

    def get_user_song_id_source_genre(self):
        results = self.sp.current_user_saved_tracks()
        genre = []
        for song_number in range(0,19): 
            song_id = results['items'][song_number]['track']['id']
            artist_id = self.get_artist_id(song_id)
            genre = self.get_genres(artist_id)
            if genre != []:
                break
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
            print('need to add ' + counter + ' items to final song output')
            for output_song_index in model_results[1:]:
                if output_song_index not in filtered_list:
                    if counter > 0:
                        filtered_list.append(output_song_index)
                        counter -= 1
                    else:
                        break
        print("filtered list with 20 unique song indices returned")
        return filtered_list
    
    def song_id_prediction_output(self,filtered_list): 
        similar_songs = []
        print('song_id_list loading...')
        song_id_array = pickle.load(open('./data/song_id_array3.pkl', 'rb'))
        print('song_id_list loaded')
        for song_row in filtered_list:
            song_id = song_id_array[song_row]
            similar_songs.append({'similarity': [.99], 'values': song_id})
        json_dict = {"songs": similar_songs}
        print("Results returned")
        return json_dict


class Slider(Sound_Drip):

    def __init__(self,slider_features):
        self.slider_features = slider_features
        self.slider_features_df = self.create_slider_feature_df(slider_features)
        self.slider_results_list = self.get_slider_results(self.slider_features_df)[0][0:20]
        self.slider_predictions = self.song_id_prediction_output(self.slider_results_list)

    def create_slider_feature_df(self,slider_features):
            df = pd.DataFrame.from_dict(json_normalize(self.slider_features["audio_features"]),orient='columns')   
            df = df.reindex(sorted(df.columns), axis=1)
            return df
        
    def get_slider_results(self,song_features_df):
        scaler = load("./models/scalar3.joblib")
        print('Scaling data...')
        data_scaled = scaler.transform(song_features_df)
        normalizer = Normalizer()
        data_normalized = normalizer.fit_transform(data_scaled)
        print('Loading pickled model...')
        model = load('./models/slider_model6.joblib')
        results = model.kneighbors([data_normalized][0])[1:]
        print('results returned')
        return results[0]


