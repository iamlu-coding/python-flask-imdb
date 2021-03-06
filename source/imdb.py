from urllib import response
from flask import Blueprint, request, render_template, redirect, send_file
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import sqlalchemy
from environs import Env
import datetime
import psycopg2
import io
env = Env()
env.read_env()

DATABASE_SERVER=env('DATABASE_SERVER')
DATABASE_PORT=env('DATABASE_PORT')
DATABASE_NAME=env('DATABASE_NAME')
DATABASE_USERNAME=env('DATABASE_USERNAME')
DATABASE_PASSWORD=env('DATABASE_PASSWORD')

imdb_mod = Blueprint('imdb', __name__)

@imdb_mod.route('top-250-movies', methods=['GET'])
@imdb_mod.route('top-250-movies/<msg>', methods=['GET'])
def top_250_movies_page(msg=None):
    
    return render_template('imdb/top_250_movies.html', msg=msg)

@imdb_mod.route('get-top-250-movies', methods=['GET', 'POST'])
def get_top_250_movies():
    url_path = request.form['url']
    print(url_path)
    
    if url_path is None:
        msg = f"URL is missing"
        url = f'/imdb/top-250-movies/{msg}'
        return redirect(url)

    # Downloading imdb top 250 movie's data
    # url = 'http://www.imdb.com/chart/top'
    url = url_path
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
        # replace "'" with blanks
        movie_title = movie_title.replace("'", '')
        star_cast = crew[index].replace("'", '')
        data = {"movie_title": movie_title,
                "year": year,
                "place": place,
                "star_cast": star_cast,
                "rating": ratings[index],
                "vote": votes[index],
                "link": links[index]}
        list.append(data)

    db_setting = f'postgresql+psycopg2://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_SERVER}:{DATABASE_PORT}/{DATABASE_NAME}'

    engine = sqlalchemy.create_engine(db_setting)
    # load data to database
    pd.DataFrame(list).to_sql('imdb_top250_movies', engine, if_exists='replace')
    x = len(list)
    msg = f"{x} total row loaded for IMDB"
    url = f'/imdb/top-250-movies/{msg}'
    return redirect(url)

@imdb_mod.route('db-restore', methods=['POST'])
def exec_db_restore():
    file = request.files.get('file')
    data = ''
    for raw_data in file:
        data += raw_data.decode('utf-8')

    filename = file.filename.replace('-', '').split(' ')
    new_table_name = '_'.join(['imdb_top250_movies', filename[0], filename[1][:6]])
    data = data.replace('imdb_top250_movies', new_table_name)
    
    # sql statement new table
    table_sql = '''
        create table "public".{0}
        (
            index int8 null,
            movie_title text null,
            year text null,
            place text null,
            star_cast text null,
            rating text null,
            vote text null,
            link text null
        )
    '''.format(new_table_name)
    
    table_exist = '''select count(*)
        from information_schema."tables"
        where table_name = '{0}'
    '''.format(new_table_name)
    
    conn = psycopg2.connect(
        host=DATABASE_SERVER,
        database=DATABASE_NAME,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        port=DATABASE_PORT
    )
    cur = conn.cursor()
    # check if table exist
    cur.execute(table_exist)
    table_exist_results = cur.fetchone()[0]
    
    # sql create new table
    if table_exist_results == 0:
        cur.execute(table_sql)
    else:
        sql = f"truncate table public.{new_table_name};"
        cur.execute(sql)
    print(data)    
    cur.execute(data)
    conn.commit()
    conn.close()
    
    msg = 'Restore DB completed successfully!'
    url = f'/imdb/top-250-movies/{msg}'
    return redirect(url)
    

@imdb_mod.route('db-backup', methods=['GET'])
def exec_db_backup():
    d_backup = str(datetime.datetime.now()).replace('.', '').replace(':', '')
    t_backup_file = str(d_backup) + "-" + 'db_backup'
    t_backup_file += ".sql"
    conn = psycopg2.connect(
        host=DATABASE_SERVER,
        database=DATABASE_NAME,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        port=DATABASE_PORT
    )
    cur = conn.cursor()
    cur.execute('select * from public.imdb_top250_movies')

    data = ''
    for row in cur:
        row = str(row).replace('None', 'null')
        data += "insert into imdb_top250_movies values " + row + ";"
    inmemory_data = io.BytesIO(data.encode('utf-8'))    
    return send_file(inmemory_data, as_attachment=True, attachment_filename=t_backup_file)


@imdb_mod.route('search-movies', methods=['POST'])
def search_movies():
    search_number = request.form['search_number']
    if search_number == '':
        search_number = 10
    conn = psycopg2.connect(
        host=DATABASE_SERVER,
        database=DATABASE_NAME,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        port=DATABASE_PORT
    )
    print(search_number)
    sql = f'select * from public.imdb_top250_movies order by cast(place as int) limit {search_number}'
    print(sql)
    cur = conn.cursor()
    cur.execute(sql)
    l = []
    for row in cur:
        l.append(row)
    search_count = len(l)
    return render_template('imdb/top_250_movies.html', top_10_list=l, search_count=search_count)

@imdb_mod.route('get-top-10-movies', methods=['GET'])
def get_top_10_movies():
    conn = psycopg2.connect(
        host=DATABASE_SERVER,
        database=DATABASE_NAME,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        port=DATABASE_PORT
    )
    cur = conn.cursor()
    cur.execute('select * from public.imdb_top250_movies order by cast(place as int) limit 10')
    l = []
    for row in cur:
        l.append(row)
    return render_template('imdb/top_250_movies.html', top_10_list=l)