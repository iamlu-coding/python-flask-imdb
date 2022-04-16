from flask import Flask
from source.imdb import imdb_mod

app = Flask(__name__)

app.register_blueprint(imdb_mod, url_prefix='/imdb')