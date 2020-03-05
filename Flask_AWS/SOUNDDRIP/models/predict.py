import spotipy
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler, Normalizer
import pandas as pd
from pandas.io.json import json_normalize
from joblib import load, dump
import pickle
import numpy as np
import psycopg2 as ps
from misc.env_vars import *
import sys
from more_itertools import unique_everseen


class Sound_Drip:
    '''
    The Sound_Drip object contains all of the code necessary to output automated results via
    the flask endpoint specified in applications.py

    Rather than calling each method individually, object instantiation sequentially produces all necessary steps
    for the final prediction output for the endpoint.

    A separate child class called Slider can be found below addressing the slider functionality allowing users to receive
    song predictions by sending the endpoint acoustical features. As of March 2020, this feature has yet to be implemented.

    init Attributes
    ----------
    token : string, passed in from POST request as JSON object. See appliction.py for more details for initiating object instance.
        The is the session user token passed to Node upon user sign in.
    sp : object
        Spotipy module object used throughout the Class to communicate directly with Spotify's API.
    user_id : string
        Spotify user id of user
    display_name : string
        Spotify display name of user
    stale_seed_list : list
        List containing tracks that the Sound Drip application already used to make a prediction.
    stale_results_list : list
        List containing tracks that the Sound Drip application already provided as song recommendations.
    song_id : string
        Spotify song ID of the seed used to output the prediction
    source_genre: list
        Spotify list containing genre/s from the seed used to output the prediction
    acoustical_features: dictionary
        Contains list of all relevant acoustical features from the Spotify API for the seed track
    popularity: integer
        Integer indicating popularity attribute of seed track from Spotify API
    song_features_df : pandas dataframe
        1 dimension dataframe containing all relevant features of the seed track for making the prediction
    results: list of integers
        List of results from the ML model inference. Results are in the form of indexes corresponding to the master song list dataframe.
    filtered_list : list of integers
        List of results filtered by genre matching against the source_genre attribute. Results are in the form of indexes corresponding to the master song list dataframe.
    song_id_predictions : list of strings
        List of 20 song ids corresponding to the index list passed in from the filtered_list attribute.
    inser_user_predictions() : class method
        see class method definition for details
    '''

    def __init__(self, token):
        self.token = token
        self.sp = spotipy.Spotify(auth=self.token)
        self.user_id, self.display_name = self.get_user_ids()
        self.stale_seed_list = self.get_stale_seed()
        self.stale_results_list = self.get_stale_results()
        self.song_id, self.source_genre = self.get_user_song_id_source_genre()
        self.acoustical_features = self.get_acoustical_features(self.song_id)
        self.popularity = self.get_popularity(self.song_id)
        self.song_features_df = self.create_feature_object(
            self.popularity, self.acoustical_features)
        self.results = self.get_results(self.song_features_df)
        self.filtered_list = self.filter_model(self.results, self.source_genre)
        self.song_id_predictions = self.song_id_prediction_output(
            self.filtered_list)
        self.insert_user_predictions(), print("predicts inserted into db")

    def get_user_ids(self):
        '''
        Retrieves user id from Spotfiy API
        Returns user_id, and display_name (display_name is for the database)
        '''
        current_user_dict = self.sp.current_user()
        display_name = current_user_dict['display_name']
        user_id = current_user_dict['id']
        print("retrieving user id and display name for current token")
        return user_id, display_name

    def get_user_song_id_source_genre(self):
        '''
        Retrieves current user's last 50 liked tracks from Spotify and loops through all tracks to find track not previously used for prediction.
        Tracks that do not contain a genre in the API (= []) are also skipped. If all retrieved liked tracks have already been used for the prediction,
        the most recently liked track is used as the seed for the application. Returns seed track song_id and genre to be used in prediction.
        '''
        stale_songs = self.stale_seed_list
        results = self.sp.current_user_saved_tracks(limit=50)
        for song_number in range(0, len(results['items'])):
            print(song_number)
            song_id = results['items'][song_number]['track']['id']
            print(song_id)
            if song_id not in stale_songs:
                artist_id = self.get_artist_id(song_id)
                genre = self.get_genres(artist_id)
                print(genre)
                if genre != []:
                    break
                else:
                    continue
            else:
                if song_number == len(results['items']) - 1:
                    print("application out of fresh seeds")
                    for song_id in stale_songs:
                        artist_id = self.get_artist_id(song_id)
                        genre = self.get_genres(artist_id)
                        if genre != []:
                            break
                        else:
                            continue

        return song_id, genre

    def get_acoustical_features(self, song_id):
        '''
        Retrieves the acousitcal features of the song_id passed in.
        Song_id is technically defined outside of the method. Song_id is pulled from the spotify API
        Returns a dictionary object of with key, val for each feature
        '''
        acoustical_features = self.sp.audio_features(song_id)[0]
        return acoustical_features

    def get_popularity(self, song_id):
        '''
        Retrieves popularity score from Spotfiy API
        '''
        popularity = self.sp.track(song_id)['popularity']
        return popularity

    def get_artist_id(self, song_id):
        '''
        Retrieves artist id from Spotify API.
        '''
        artist = self.sp.track(song_id)['artists'][0]['id']
        return artist

    def get_genres(self, artist):
        '''
        Retrieves genre of artist from spotify API.
        '''
        genre = self.sp.artist(artist)['genres']
        return genre

    def create_feature_object(self, popularity, acoustical_features):
        '''
        Combines previously retrieved features into the dictionary format needed for the get_results method.
        Features are sorted in alphabetical order before being returned to match the order of the features that the model was trained on.
        '''
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

        df = pd.DataFrame.from_dict(
            json_normalize(
                song_features["audio_features"]),
            orient='columns')
        df = df.reindex(sorted(df.columns), axis=1)
        return df

    def get_results(self, song_features_df):
        '''
        1) Loads in previously fitted scaler (MinMax).
            1a) MinMax scalar import is the scaler in question
        2) Song_features_df is scaled.
        3) Scaled data is normalized
        4) Previously trained KNN model is loaded
        5) Predictions are made on the normalized array from the song features
        6) Returns results object (5000 nearest neighbors from KNN model are returned)
        '''
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

    def filter_model(self, model_results, source_genre_list):
        '''
        1) Load in genres array
            1a) The genres array is a numpy array object which contains a list of genres in corresponding order to the song_list df
        2) Raw model_results are loaded
        3) Raw model_results are filtered through stale_results
            3a) This is to ensure that the filter does not produce redundant predictions
        4) Loops through output_song_index
            4a) Output_song_index is member of model_results
        5) Loops through output_genre_list
            5a) Output_genre_list is returned from genre_array with output_song_index
        6) Loops through source_genre_list
            6a) Source_genre_list is a necessary **arg for this method
        7) Condition for matching output_genre to source_genre
            7a) if the condition is met, then the output_song_index is appended to the filtered list
        8) Duplicates removed from filtered_list
        9) 'if' statement is initiated
            9a) Song_list_length specifies ultimate amount of predictions from application
        10) If filtered list greater than or equal to pre-defined song_list length, the method returns the filtered_list
        11) If filtered list is less than pre-defined song_list length, tracks from model_results that do not match the source_genre are appended to filtered_list
            11a) This is done by looping through songs within the output_song_index and appending to the filtered_list
            11b) Song_list length is being used here to ensure that the final list is returned appropriately
        12) Returns filtered_list
        '''
        # loop takes KNN results and filters by source track genres
        print(source_genre_list)
        print("filter for genres initiated")
        genre_array = pickle.load(open("./data/genres_array_2.pkl", "rb"))
        filtered_list = []
        song_list_length = 20
        stale_results = self.stale_results_list
        model_results_before = len(model_results[0][1:])
        model_results = [index for index in model_results[0]
                         [1:] if index not in stale_results]
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
        filtered_list = list(unique_everseen(filtered_list))
        if len(filtered_list) >= song_list_length:
            print("filter found at least 20 genre matches")
            filtered_list = filtered_list[0:20]
        else:
            counter = song_list_length - len(filtered_list)
            print("length of filtered list:", len(filtered_list))
            print(f'need to add {counter} items to final song output')
            for output_song_index in model_results:
                if output_song_index not in filtered_list:
                    if counter > 0:
                        filtered_list.append(output_song_index)
                        counter -= 1
                    else:
                        break
        print(
            f"filtered list with {len(filtered_list)} unique song indices returned")
        return filtered_list

    def song_id_prediction_output(self, filtered_list):
        '''
        Retrieving the corresponding spotify song id's and outputting correct format for endpoint
        Returns song_result_output_dict for global endpoint, and song_id_and_index_dict for database method
        '''
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
        song_id_and_index_dict = {
            song_id: song_index for song_id,
            song_index in zip(
                song_id_list,
                filtered_list)}
        print("Results returned")
        return song_result_output_dict, song_id_and_index_dict

    def db_connect(self):
        '''
        Method for opening a connection to db and creating cursor object
        '''
        conn = ps.connect(host=POSTGRES_ADDRESS,
                          database=POSTGRES_DBNAME,
                          user=POSTGRES_USERNAME,
                          password=POSTGRES_PASSWORD,
                          port=POSTGRES_PORT)
        cur = conn.cursor()
        return conn, cur

    # def get_user_ids(self):
    #     '''
    #     Retrieves user id from Spotfiy API
    #     Returns user_id, and display_name (display_name is for the database)
    #     '''
    #     current_user_dict = self.sp.current_user()
    #     display_name = current_user_dict['display_name']
    #     user_id = current_user_dict['id']
    #     print("retrieving user id and display name for current token")
    #     return user_id, display_name

    def insert_user_predictions(self):
        '''
        Loops through song_id_predictions, inserting song_id, user information and song_index into db
        '''
        try:
            conn, cur = self.db_connect()
            for song_id, song_index in self.song_id_predictions[1].items():
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
        '''
        Retrieves indices corresponding to the master song list of tracks that have already been recommended to the specific user previously
        '''
        try:
            conn, cur = self.db_connect()
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


class Slider(Sound_Drip):
    '''
    A child class of the Sound_Drip parent class.
    Slider allows users to receive ong predictions by sending the endpoint acoustical features.
    As of March 2020, this feature has yet to be implemented.

    init Attributes
    ----------
    slider_features = dictionary object
        features received from external POST request to the endpoint
    slider_features_df = pandas dataframe object
        converted to correct format for get_slider_results() method
    slider_results_list = list
        list with indices corresponding to dataframe song_ids as results
    slider_predictions = dictionary
        slider endpoint return object with Spotify API track ids
    ----------
    '''

    def __init__(self, slider_features):
        self.slider_features = slider_features
        self.slider_features_df = self.create_slider_feature_df(
            slider_features)
        self.slider_results_list = self.get_slider_results(
            self.slider_features_df)[0][0:20]
        self.slider_predictions = self.song_id_prediction_output(
            self.slider_results_list)

    def create_slider_feature_df(self, slider_features):
        df = pd.DataFrame.from_dict(
            json_normalize(
                self.slider_features["audio_features"]),
            orient='columns')
        df = df.reindex(sorted(df.columns), axis=1)
        return df

    def get_slider_results(self, song_features_df):
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
