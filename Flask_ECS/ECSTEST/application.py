# import spotipy
# import spotipy.util as util
from flask import (Flask, render_template, request,
                   make_response,
                   jsonify)

from models.predict import predictfunc, get_id, get_features, instantiate_sp


# Create Flask app. Should use "application" as variable name for AWS
application = Flask(__name__)



# Main Default page
@application.route("/request", methods=['GET', 'POST'])
def prediction():
  ''''request flask route takes token passed in from FE POST and outputs the 20 most similar songs'''
  content = request.get_json(silent=True)
  token = content["token"]
  sp = instantiate_sp(token)
  id = get_id(sp)
  features = get_features(id, sp)
  return jsonify(predictfunc(features), print('yay'))


@application.route("/")
def root():
    return """Hello, I am working right now. send your request to {/request}"""


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=80)
