from flask import Blueprint, redirect

home_mod = Blueprint('home', __name__)

@home_mod.route('/', methods=['GET'])
def home_page():
    url = f'/imdb/top-250-movies'
    return redirect(url)