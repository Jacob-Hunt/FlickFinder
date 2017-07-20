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


# libraries
from sqlalchemy import *
import requests

# modules
from config import db

# ************************************************************* #
# *** TABLE PROTOTYPES ***

def getFlTable(db, userID):
    """ Generate sqlalchemy prototype for a _friendsList table """
    # get name of friends list
    flTableName = str(userID) + "_friendsList"

    # table prototype for sqlalchemy
    flTable = Table(
                    flTableName,
                    db.metadata,

                    Column('sql_id',
                           Integer,
                           nullable=False,
                           autoincrement=True,
                           primary_key=True),

                    Column('other_user_id',
                           Integer,
                           nullable=False),

                    extend_existing=True
                   )

    return flTable

# ************************************************************* #

def getFrTable(db, userID):
    """ Generate sqlalchemy prototype for a _friendRequests table """
    # get name of friend request table
    frTableName = str(userID) + "_friendRequests"

    # table prototype for sqlalchemy
    frTable = Table(
                    frTableName,
                    db.metadata,

                    Column('sql_id',
                           Integer,
                           nullable=False,
                           autoincrement=True,
                           primary_key=True),

                    Column('other_user_id',
                           Integer,
                           nullable=False),

                    Column('sent',
                           Integer,
                           server_default=literal(0),
                           nullable=False),

                    Column('received',
                           Integer,
                           server_default=literal(0),
                           nullable=False),

                    extend_existing=True
                   )

    return frTable

# ************************************************************* #

def getMnTable(db):
    """ Generate sqlalchemy prototype for movie nights table """

    tableName = "movieNights"

    # num_users = number of users in movie night
    # num_pages = number of pages in movie night
    mnTable = Table(
                    tableName,
                    db.metadata,

                    Column('sql_id',
                           Integer,
                           nullable=False,
                           autoincrement=True,
                           primary_key=True),

                    Column('num_users',
                           Integer,
                           nullable=False),

                    Column('num_pages',
                           Integer,
                           nullable=False),

                    Column('genres',
                           Text),

                    Column('date_created',
                           DateTime,
                           nullable=False),

                    extend_existing=True
                   )

    return mnTable

# ************************************************************* #

def getUsrTable(db):
    """ Generate sqlalchemy prototype for users table """

    tableName = "users"
    
    # table prototype for sqlalchemy
    usrTable = Table(
                     tableName,
                     db.metadata,

                     Column('sql_id',
                            Integer,
                            nullable=False,
                            autoincrement=True,
                            primary_key=True,
                            unique=False),

                     Column('user',
                            Text,
                            nullable=False,
                            unique=True),

                     Column('email',
                            Text,
                            nullable=False,
                            unique=True),

                     Column('hashed',
                            Text,
                            nullable=False,
                            unique=False),

                     Column('name_first',
                            Text,
                            nullable=False,
                            unique=False),

                     Column('name_last',
                            Text,
                            nullable=False,
                            unique=False),

                     extend_existing=True
                    )

    return usrTable

# ************************************************************* #

def getUserMnTable(db, usrID):
    """ Get sqlalchemy prototype for user table of movie nights """

    tableName = str(usrID) + "_movieNights"

    mnTable = Table(
                    tableName,
                    db.metadata,

                    Column('sql_id',
                           Integer,
                           nullable=False,
                           autoincrement=True,
                           primary_key=True),

                    Column('mn_id',
                           Integer,
                           nullable=False),

                    extend_existing=True
                   )

    return mnTable

# ************************************************************* #

def getUserMvTable(db, usrID):
    """ Get sqlalchemy prototype for user table of movie ratings """

    tableName= str(usrID) + "_movieList"

    mvTable = Table(
                    tableName,
                    db.metadata,

                    Column('sql_id',
                           Integer,
                           nullable=False,
                           autoincrement=True,
                           primary_key=True),

                    Column('movie_id',
                           Integer,
                           nullable=False),

                    Column('rating',
                           Integer,
                           server_default=literal(0)),

                    extend_existing=True
                   )

    return mvTable

# ************************************************************* #

def getMnLogTable(db, mnID):
    """ Generate sqlalchemy prototype for movie night log table """
    tableName = "mn_" + str(mnID) + "_log"

    mnLogTable = Table(
                       tableName,
                       db.metadata,

                       Column('sql_id',
                              Integer,
                              nullable=False,
                              autoincrement=True,
                              primary_key=True),

                       Column('movie_id',
                              Integer,
                              nullable=False),

                       Column('user_id',
                              Integer,
                              nullable=False),

                       Column('rating',
                              Integer,
                              nullable=False),

                       extend_existing=True
                      )

    return mnLogTable

# ************************************************************* #

def getMnResultsTable(db, mnID):
    """ Generate sqlalchemy prototype for movie night results table """
    tableName = "mn_" + str(mnID) + "_results"

    mnResultsTable = Table(
                           tableName,
                           db.metadata,

                           Column('sql_id',
                                  Integer,
                                  nullable=False,
                                  autoincrement=True,
                                  primary_key=True),

                           Column('movie_id',
                                  Integer,
                                  nullable=False),

                           Column('match_status',
                                  Integer),

                           extend_existing=True
                          )

    return mnResultsTable

# ************************************************************* #

def getMnSuggestionsTable(db, mnID):
    """ Generate sqlalchemy prototype for movie night suggestions table """
    tableName = "mn_" + str(mnID) + "_suggestions"

    mnSuggestionsTable = Table(
                               tableName,
                               db.metadata,

                               Column('sql_id',
                                      Integer,
                                      nullable=False,
                                      autoincrement=True,
                                      primary_key=True),

                               Column('query_num',
                                      Integer,
                                      nullable=False),

                               Column('page_num',
                                      Integer,
                                      nullable=False),

                               Column('query_depth',
                                      Integer,
                                      nullable=False),

                               Column('movie_id',
                                      Integer,
                                      nullable=False),

                               Column('title',
                                      Text),

                               Column('description',
                                      Text),

                               Column('poster_url',
                                      Text),

                               Column('release_date',
                                      Text),

                               Column('genres',
                                      Text),

                               Column('rating',
                                      REAL),

                               extend_existing=True
                              )

    return mnSuggestionsTable

# ************************************************************* #

def getMnUsersTable(db, mnID):
    """ Generate sqlalchemy prototype for movie night user list table """
    tableName = "mn_" + str(mnID) + "_users"

    # user_page = what page of selections user is on
    # user_position = how deep user is into current page of selections
    mnUsersTable = Table(
                         tableName,
                         db.metadata,

                         Column('sql_id',
                                Integer,
                                nullable=False,
                                autoincrement=True,
                                primary_key=True),

                         Column('user_id',
                                Integer,
                                nullable=False),

                         Column('user_page',
                                Integer,
                                server_default=literal(0)),

                         Column('user_position',
                                Integer,
                                server_default=literal(0)),

                         extend_existing=True
                        )

    return mnUsersTable

# ************************************************************* #

class Users(db.Model):
    sql_id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Text, unique=True)
    email = db.Column(db.Text, unique=True)
    hashed = db.Column(db.Text, unique=False)
    name_first = db.Column(db.Text, unique=False)
    name_last = db.Column(db.Text, unique=False)

    def __init__(self, username, email, hashed, name_first, name_last):
        self.user = username
        self.email = email
        self.hashed = hashed
        self.name_first = name_first
        self.name_last = name_last
