# ************************************************************* #
#
#    FlickFinder Alpha 0.2
#    Copyright (C) 2017  Jacob Hunt (jacobhuntgit@gmail.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2,  as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see 
#    https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html.
#
# ************************************************************* #


# library imports
from sys import path, exit
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *

# un-comment the following line if you wish to put apiKey.py
# in parent folder of main app:
#path.append('../')

# API key from The Movie DB
try:
    apiKey = __import__("apiKey")
except:
    print()
    exit("ERROR: FlickFinder requires a valid api key from \n"
       + "https://www.themoviedb.org/ to work properly.\n\n"
       + "Go to https://www.themoviedb.org/faq/api?language=en \n"
       + "for instructions on how to obtain one.  If you \n"
       + "already have an api key, go into apiKey.py and \n"
       + "replace '<ENTER API KEY HERE>' with your api key.\n")

# create Flask object
app = Flask(__name__)

# UN-COMMENT THE FOLLOWING TWO LINES FOR SSL ENCRYPTION
#from flask_sslify import SSLify
#sslify = SSLify(app)

# set the secret key
app.secret_key = "<ADD SECRET KEY HERE>"

# global variable to store api key
API_KEY = apiKey.apiKey

# configure database engine
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite"
app.config['SQLALCHEMY_ECHO'] = True
engine = create_engine("sqlite:///database.sqlite")

# launch database engine
db = SQLAlchemy()
db.init_app(app)

# configure server
server_address = "0.0.0.0"
port_number = 8080
