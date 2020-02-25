from flask import (Flask, request, jsonify)
from flask_cors import CORS
from models.predict import Sound_Drip,Slider


# Create Flask app. Should use "application" as variable name for AWS EBS
application = Flask(__name__)
CORS(application)



# Main Default page
@application.route("/request", methods=['GET', 'POST'])
def prediction():
  ''''request flask route takes token passed in from FE POST and outputs the 20 most similar songs'''
  content = request.get_json(silent=True)
  token = content["token"]
  SdObj = Sound_Drip(token)
  song_id,source_genre = SdObj.get_user_song_id_source_genre()
  acoustical_features = SdObj.get_acoustical_features(song_id)
  popularity = SdObj.get_popularity(song_id)
  song_features_df = SdObj.create_feature_object(popularity, acoustical_features)
  results = SdObj.get_results(song_features_df)
  filtered_list = SdObj.filter_model(results,source_genre)
  return jsonify(SdObj.song_id_prediction_output(filtered_list)),print('JSON Object Returned')


# Slider endpoint
@application.route("/slider", methods=['GET', 'POST'])
def slider_prediction():
  ''''request flask route takes acoustical features object and outputs the 20 most similar songs'''
  content = request.get_json(silent=True)
  slider = Slider(content)
  slider_predictions = slider.slider_predictions
  return jsonify(slider_predictions, print('Slider JSON Object Returned'))


@application.route("/")
def root():
    return """Hello, I am working right now. send your request to {/request}"""


if __name__ == "__main__":
    application.run(debug=True)
