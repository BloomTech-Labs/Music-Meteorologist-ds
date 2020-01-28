"""Entry point fot the TWITTOFF flask app"""

from .app import create_app

# APP is a Global var
APP = create_app()

# run this in terminal with set FLASK_APP=SOUNDDRIP:APP (and) flask run