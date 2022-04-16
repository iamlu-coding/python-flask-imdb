from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
from pandas.io import sql
import sqlalchemy
from environs import Env

env = Env()
env.read_env()

DATABASE_SERVER=env('DATABASE_SERVER')
DATABASE_PORT=env('DATABASE_PORT')
DATABASE_NAME=env('DATABASE_NAME')
DATABASE_USERNAME=env('DATABASE_USERNAME')
DATABASE_PASSWORD=env('DATABASE_PASSWORD')

# Downloading imdb top 250 movie's data
url = 'http://www.imdb.com/chart/top'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

movies = soup.select('td.titleColumn')
links = [a.attrs.get('href') for a in soup.select('td.titleColumn a')]
crew = [a.attrs.get('title') for a in soup.select('td.titleColumn a')]

ratings = [b.attrs.get('data-value')
           for b in soup.select('td.posterColumn span[name=ir]')]

votes = [b.attrs.get('data-value')
         for b in soup.select('td.ratingColumn strong')]

list = []

# create a empty list for storing
# movie information
list = []

# Iterating over movies to extract
# each movie's details
for index in range(0, len(movies)):
    # Separating  movie into: 'place',
    # 'title', 'year'
    movie_string = movies[index].get_text()
    movie = (' '.join(movie_string.split()).replace('.', ''))
    movie_title = movie[len(str(index)) + 1:-7]
    year = re.search('\((.*?)\)', movie_string).group(1)
    place = movie[:len(str(index)) - (len(movie))]
    data = {"movie_title": movie_title,
            "year": year,
            "place": place,
            "star_cast": crew[index],
            "rating": ratings[index],
            "vote": votes[index],
            "link": links[index]}
    list.append(data)



print(pd.DataFrame(list))
# pd.DataFrame(list).to_csv('Top_250_movies.csv')


db_setting = f'postgresql+psycopg2://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_SERVER}:{DATABASE_PORT}/{DATABASE_NAME}'

engine = sqlalchemy.create_engine(db_setting)
# drop table
sql.execute('drop table IMDB_TOP250_movies', engine)

pd.DataFrame(list).to_sql('IMDB_TOP250_movies', engine)
