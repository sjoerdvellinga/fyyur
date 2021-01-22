import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# TODO: to run on other localmachine, replace username 'vellinga'
# TODO: in terminal run '$ createdb fyyur' to create db

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgres://vellinga@localhost:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False
