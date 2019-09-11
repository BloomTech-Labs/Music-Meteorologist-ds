import requests

r = requests.post(url = "https://music-meteorologist-ds.herokuapp.com", json = {"audio_features" : {"danceability": 0.186,
        "energy": 0.107,
        "key": 5,
        "loudness": -14.802,
        "mode": 1,
        "speechiness": 0.0347,
        "acousticness": 0.934,
        "instrumentalness": 0,
        "liveness": 0.297,
        "valence": 0.149,
        "tempo": 107.095,
        "time_signature": 4}})
print(r.content)
