import requests

r = requests.post(url = "https://music-meteorologist-ds.herokuapp.com", json = {"audio_features" : {"acousticness": 0.934,"danceability": 0.186,
        "energy": 0.107,
        "instrumentalness": 0,
        "key": 5,
        "liveness": 0.297,
        "loudness": -14.802,
        "mode": 1,
        "speechiness": 0.0347,
        "tempo": 107.095,
        "time_signature": 4,
        "valence": 0.149}})
print(r.content)
