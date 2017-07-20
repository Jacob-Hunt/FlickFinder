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
import requests
from flask import render_template, redirect, request, session, url_for, jsonify
from sqlalchemy import *
from passlib.apps import custom_app_context as pwd_context

# local modules
from helpers import *
from config import *
from sql_tables import *


@app.route("/getFriendList", methods=["GET", "POST"])
def getFriendList():
    """ Get a JSON object with the names and usernames of friends """
    connection = engine.connect()

    friendList = []
    flTable = getFlTable(db, session["user_id"])

    s = select([flTable])
    result = connection.execute(s)

    for row in result:
        friendDict = {}
        friendDict["firstName"] = getUserFirstName(row[1], db)
        friendDict["lastName"] = getUserLastName(row[1], db)
        friendDict["userName"] = getUser(row[1], db)
        friendDict["userID"] = row[1]
        friendList.append(friendDict)

    connection.close()

    return jsonify(friendList = friendList)

# ************************************************************* #

@app.route("/getFriendRequests", methods=["GET", "POST"])
def getFriendRequests():
    """ Return a JSON object with pending friend requests the current 
        user has received """

    # shorthand variable
    userID = session["user_id"]

    # get table prototypes
    frTable = getFrTable(db, userID)
    usrTable = getUsrTable(db)

    # connect to database
    connection = engine.connect()

    # get user ids and store in array
    idList = []
    s = select([frTable.c.other_user_id]).where(frTable.c.received == 1)
    result = connection.execute(s)
    for row in result:
        idList.append(row[frTable.c.other_user_id])

    # get usernames and store in array
    usrNameList = []
    for item in idList:
        s = select([usrTable.c.user]).where(usrTable.c.sql_id == item)
        result = connection.execute(s)
        result = result.fetchone()
        usrNameList.append("@" + result.user)

    connection.close()

    return jsonify(idList=idList, usrNameList=usrNameList)

# ************************************************************* #

@app.route("/getGenres", methods=["GET", "POST"])
def getGenres():
    """ Returns a JSON object with TMDB genres and corresponding key
        values """

    query = ("https://api.themoviedb.org/3/genre/movie/list?api_key="
             + API_KEY
             + "&language=en-US")

    r = requests.get(query)
    r = r.json()

    return jsonify(r["genres"])

# ************************************************************* #

@app.route("/getMnList", methods=["GET", "POST"])
def getMnList():
    """ Get a user's list of movie night IDs and timestamps """

    # get table prototypes
    mnTable = getMnTable(db)
    userMnTable = getUserMnTable(db, session["user_id"])

    # connect to database
    connection = engine.connect()

    # get user's movie night ids and add results to array
    s = select([userMnTable.c.mn_id])
    result = connection.execute(s)
    if not result:
        connection.close()
        return jsonify(
                       success=False,
                       returnMessage=("Error when retreiving user's "
                                      + "list of movie nights")
                      )
    userMnIdList = []
    for row in result:
        userMnIdList.append(row[userMnTable.c.mn_id])

    # get user's movie night timestamps and add results to array
    userMnDtList = []
    for mnID in userMnIdList:
        s = (select([mnTable.c.date_created])
             .where(mnTable.c.sql_id == mnID))
        result = connection.execute(s)
        if not result:
            connection.close()
            return jsonify(
                       success=False,
                       returnMessage=("Error when retreiving user's "
                                          + "list of movie nights")
                       )
        result = result.fetchone()
        userMnDtList.append(result.date_created)

    # close database connection
    connection.close()

    # return JSON object with lists
    return jsonify(mnIdList=userMnIdList, mnDateTimeList=userMnDtList)

# ************************************************************* #

@app.route("/getUserMnPosition", methods=["GET", "POST"])
def getUserMnPosition():
    """ Get a user's position in a given movie night """

    # ensure that arguments were received
    if not request.args.get("mnID"):
        raise RuntimeError("missing script argument 'mnID'")

    # shorthand variable
    mnID = request.args.get("mnID")

    # get table prototype
    mnUsersTable = getMnUsersTable(db, mnID)

    # connect to database
    connection = engine.connect()

    # get user's position info
    s = (
         select([mnUsersTable])
         .where(mnUsersTable.c.user_id == session["user_id"])
        )
    result = connection.execute(s)
    result = result.fetchone()

    # return JSON object
    return jsonify(page=result.user_page, depth=result.user_position)

# ************************************************************* #

@app.route("/getMatches", methods=["GET", "POST"])
def getMatches():
    """ Get the matches for a given movie night """

    # ensure that arguments were received
    if not request.args.get("mnID"):
        raise RuntimeError("missing script argument 'mnID'")

    # shorthand variables
    mnID = request.args.get("mnID")
    userID = session["user_id"]

    # get table prototypes
    mnResultsTable = getMnResultsTable(db, mnID)
    mnUsersTable = getMnUsersTable(db, mnID)

    # connect to database
    connection = engine.connect()

    # ensure that logged in user is part of movie night
    s = select([mnUsersTable]).where(mnUsersTable.c.user_id == userID)
    result = connection.execute(s)
    result = result.fetchone()
    if not result:
        return jsonify(success=False,
                       returnMessage=("Logged in user not in "
                                      + "requested movie night")
                      )

    # query mnResultsTable for matches
    s = (select([mnResultsTable.c.movie_id])
         .where(mnResultsTable.c.match_status > 0))
    result = connection.execute(s)

    # create empty list to use as a return JSON
    matchInfoList = []

    # for each result
    for row in result:
        # query TMDB for movie data
        movieInfo = getMovieInfo(API_KEY, row[mnResultsTable.c.movie_id])        
        # append result to matchInfoList
        matchInfoList.append(movieInfo)


    # return JSON object
    returnMessage = "Successfully retrieved matches for current movie night."
    return jsonify(success=True,
                   returnMessage=returnMessage,
                   matches=matchInfoList)
