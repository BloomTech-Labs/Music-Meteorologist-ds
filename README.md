Production site: https://www.sound-drip.com/

There's a lot going on here, so we'll let you know where things are.

***Top Level***
- `data_collection` is a directory where we aggregated all the spotify song data
- `model_notebooks` is a directory where all current and former knn models are found. There is also a notebook where we tried DBSCAN
- `model_validation` is a directory used to test out song outputs from our model for listening as part of the model validation step
- `Flask_Notebooks` is our directory for notebooks used for staging production code prior to deploying changes to flask
- `spotipy` is our directory where we explored the Spotify API extensively in preparation for API calls
- `RDS-postgres/SOUNDDRIP` is our sandbox for testing out new updates to our RDS-hosted postgrSQL tables
- `Flask_AWS/SOUNDDRIP` is our production flask app

More information can be found on our notion doc: https://www.notion.so/For-Current-DS-145f105cd7a1459bbc955a97624ecc60

***API INPUTS/OUTPUTS***


Root endpoints utilized on local flask deployments
- Root are the local APIs
- **SD DS Prod refers to the main one being consumed by the application**

Information regarding the API calls made between front-end and DS can be found here:
https://documenter.getpostman.com/view/10161796/SzRuYroD?version=latest#intro


***Local Deployment***

Environment manager documentation can be found here:
https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/


1. Install pip's preferred virtual environment manager 

```
python3 -m pip install --user virtualenv
```
2. Access `Flask_AWS/SOUNDDRIP`
3. Create environment, replacing `env` with your preferred environment name 

```
python3 -m venv env
```
4. Activate environment

```
source env/bin/activate
```

5. Install all dependencies from the `requirements.txt` file located in the current directory 
 

```
pip3 install -r requirements.txt
```

6. Download all compressed file object dependencies from `S3` in this directory

https://s3.console.aws.amazon.com/s3/buckets/sound-drip/Flask-Prod-Files/?region=us-east-1&tab=overview

7. Copy following files to `./models`: 
    - `genres_array_2.pkl`
    - `model5.joblib`
    - `scalar3.joblib`
    - `slider_model6.joblib`

8. Place `song_id_array3.pkl` in a new `data` folder after creating it under the `SOUNDDRIP` directory

9. Create `env_vars.py` with the necessary database credentials under `./misc/` 


9. Run the application

```
python3 application.py 
```

* NOTE: If you get an error that a particular package is missing even though you have confirmed it is installed, you will need to `pip install` those packages utilizing an optional `target` argument:

     - You can find your virtual enviroment's target directory by accessing python3 shell within your virtual environment and running `sys.path`  

```
pip install [package name] --target [target directory]
```






