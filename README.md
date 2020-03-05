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

More information can be found on our notion doc: https://www.notion.so/For-Current-DS-145f105cd7a1459bbc955a97624ecc60

***API INPUTS/OUTPUTS***


Root endpoints utilized on local flask deployments
- Root are the local APIs
- **SD DS Prod refers to the main one being consumed by the application**

Information regarding the API calls made between front-end and DS can be found here:
https://documenter.getpostman.com/view/10161796/SzRuYroD?version=latest#intro
