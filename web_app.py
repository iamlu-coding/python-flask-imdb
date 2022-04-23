from flask import Flask
from source.imdb import imdb_mod
from source.home import home_mod

app = Flask(__name__)

app.register_blueprint(home_mod, url_prefix='/')
app.register_blueprint(imdb_mod, url_prefix='/imdb')
