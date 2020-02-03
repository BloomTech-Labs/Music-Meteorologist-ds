#import os
#import pandas as pd
#import json
#import pickle
#import numpy as np
from flask import (Flask, render_template,
                   request, make_response,
                   jsonify)
#from pandas.io.json import json_normalize
# from SOUNDDRIP.models.predict import predictfunc
from models.predict import predictfunc



application = Flask(__name__)
# Main Default page
@application.route("/request", methods=['GET', 'POST'])
def sim20():
  content = request.get_json(silent=True)
  return jsonify(predictfunc(content)), print('yay')

@application.route("/")
def root():
    return """Hello, I am working right now. send your request to {/request}"""



if __name__ == "__main__":
    application.run()


