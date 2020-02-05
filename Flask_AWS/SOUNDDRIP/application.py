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
import requests
#from pandas.io.json import json_normalize
# from SOUNDDRIP.models.predict import predictfunc
from models.predict import predictfunc, get_id, get_features


application = Flask(__name__)
# Main Default page
@application.route("/request", methods=['GET', 'POST'])
def sim20():
    content = request.get_json(silent=True)
    return jsonify(predictfunc(content)), print('yay')


# not sure why the below function isn't saying that there's no get_json attribute

# def request():
#     content = request.get_json(silent=True)
#     print(content)
#     id = get_id(content)
#     features = get_features(id)
#     return jsonify(predictfunc(features), print('yay'))

@application.route("/")

def root():
    return """Hello, I am working right now. send your request to {/request}"""

if __name__ == "__main__":
    application.run(debug=True)
