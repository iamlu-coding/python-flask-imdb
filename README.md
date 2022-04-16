# Python Flask IMDB
Web app that will get top 250 movies from imdb website and load the data into a postgres database

## Environment Variables
You will need to create a .env file that will contain that following variables:

DATABASE_SERVER=""
DATABASE_PORT="5432"
DATABASE_USERNAME=""
DATABASE_PASSWORD=""
DATABASE_NAME=""

## Recommend to create Virtual Environment
To create a virtual environment run the following command:

python -m venv env

or 

python3 -m venv env

Next activate your environment as the following:

Windows
source env/Scripts/activate

or 

Linux/Mac
source env/bin/activate

## Install requirements packages
Once the virtual environment has been created and activated, next you will need to install all the packages from the requirements.txt file.

Run the following command to install packages:

pip install -r requirements.txt

## To start Web Application
By default the port is set to 8000.  This can be changes in the wsgi.py to any other port number.

Run the following command to start the application.  

python wsgi.py
