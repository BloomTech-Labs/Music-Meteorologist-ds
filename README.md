Production site: https://www.sound-drip.com/

There's a lot going on here, so we'll let you know where things are.

***Top Level***
- data_collection is a directory where we aggregated all the spotify song data
- model_notebooks is a directory where all current and former knn models are found. There is also a notebook where we tried DBSCAN
- model_validation is a directory used to test out song outputs from our model for listening as part of the model validation step
- Flask_Notebooks is our directory for notebooks used for staging production code prior to deploying changes to flask
- spotipy is our directory where we explored the Spotify API extensively in preparation for API calls
- RDS-postgres/SOUNDDRIP is our sandbox for testing out new updates to our RDS-hosted postgreSQL tables
- Flask_AWS/SOUNDDRIP is our production flask app

***INPUT_ACTUAL***

```json

{"token":"BQCEhCfQoAEwvw7muBWJ4fQmCKmB37d0a0PRzFPGNHxXQjiW9YWECFFKXDYSrJ_Id_fKtA9rKnOUZJmrancJzmlxDPGBCzhQWNZ9sQK6FNfIlCyy81UVqUiWUT-2rOXkskvZXgjkqwamQMZ0Eu-3FbKxfOdxw"}

```

***OUTPUT***
```json
{
  "songs": [
    {
      "similarity": [
        0.9999733801267939
      ],
      "values": "6rMRZ9DtxJhH1Ycbk6VeDi"
    },
    {
      "similarity": [
        0.9999691841226913
      ],
      "values": "6cgoS3EosBd9MZOK8Z6KOV"
    }
  ]
}
```
