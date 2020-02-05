#import os
#import pandas as pd
#import json
#import pickle
#import numpy as np
import spotipy
import spotipy.util as util
from flask import (Flask, render_template, request,
                   make_response,
                   jsonify)
#from pandas.io.json import json_normalize
# from SOUNDDRIP.models.predict import predictfunc
from models.predict import predictfunc, get_id, get_features


application = Flask(__name__)
# Main Default page
@application.route("/request", methods=['GET', 'POST'])
def prediction():
    content = request.get_json(silent=True)
    token = content["token"]
    sp = spotipy.Spotify(auth=token)
    id = get_id(sp)
    features = get_features(id,sp)
    return jsonify(predictfunc(features), print('yay'))

@application.route("/")

def root():
    return """Hello, I am working right now. send your request to {/request}"""

if __name__ == "__main__":
    application.run(debug=True)
