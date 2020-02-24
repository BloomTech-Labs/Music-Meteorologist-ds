# import spotipy
# import spotipy.util as util
from flask import (Flask, render_template, request,
                   make_response,
                   jsonify)
from flask_cors import CORS



from models.predict import instantiate_sp, get_acoustical_features, get_popularity, get_artist_id, get_genres, create_feature_object, get_results, filter_model, song_id_prediction_output, get_user_song_id  



# Create Flask app. Should use "application" as variable name for AWS
application = Flask(__name__)
CORS(application)



# Main Default page
@application.route("/request", methods=['GET', 'POST'])
def prediction():
  ''''request flask route takes token passed in from FE POST and outputs the 20 most similar songs'''
  content = request.get_json(silent=True)
  token = content["token"]
  sp = instantiate_sp(token)
  song_id = get_user_song_id(sp)
  acoustical_features = get_acoustical_features(song_id, sp)
  popularity = get_popularity(song_id, sp)
  song_features_df = create_feature_object(popularity, acoustical_features)
  results = get_results(song_features_df)
  source_genre = get_genres(get_artist_id(song_id, sp),sp)
  filtered_list = filter_model(results,source_genre)
  return jsonify(song_id_prediction_output(filtered_list)),print('JSON Object Returned')


# # Slider endpoint
# @application.route("/slider", methods=['GET', 'POST'])
# def prediction():
#   ''''request flask route takes acoustical features object and outputs the 20 most similar songs'''
#   content = request.get_json(silent=True)
#   token = content["token"]
#   sp = instantiate_sp(token)
#   id = get_id(sp)
#   features = get_features(id, sp)
#   return jsonify(predictfunc(features), print('yay'))


@application.route("/")
def root():
    return """Hello, I am working right now. send your request to {/request}"""


if __name__ == "__main__":
    application.run(debug=True)
