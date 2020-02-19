        """Ihis file contains def for spotify api"""
"""Data engnering, cosine_similarity, and all_similarities"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np

"""This def Grants access to spotify API"""
def cred_init(cli_id, cli_secret):
    client_credentials_manager = SpotifyClientCredentials(
        client_id=cli_id, 
        client_secret=cli_secret)
    client_credentials_manager = client_credentials_manager
    sp = spotipy.Spotify(client_credentials_manager=
                         client_credentials_manager)
return sp

"""This def organizes pandas dataframe from a csv"""
def original_data_engnering(csv1, csv2):
    df = pd.read_csv(csv1)
    df_other = pd.read_csv(csv2)
    df = df.drop('popularity', 1)
    df = df.drop('duration_ms', 1)
    df = df.dropna()
    df_other = df_other.drop('popularity', 1)
    df_other = df_other.drop('duration_ms', 1)
    df_other = df_other.dropna()
    df = pd.concat([df,df_other]).
                    drop_duplicates().
                    reset_index(drop=True)
    dfy = df[['artist_name','track_id', 'track_name']]
    df2 = df.drop('artist_name', 1)
    df2 = df2.drop('track_id', 1)
    df2 = df2.drop('track_name', 1)
    array = df2.values
return dfy, array