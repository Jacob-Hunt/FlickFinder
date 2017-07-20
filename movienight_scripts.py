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

# constants
POSTER_URL_ROOT = "https://image.tmdb.org/t/p/w185//"

# ************************************************************* #

@app.route("/newMovieNight", methods=["GET", "POST"])
def newMovieNight():	
    """ Initialize new movie night """

    # ensure that arguments were passed to script
    validation = validateArgs(request.args, ["userList", "genreList"])
    if not validation["success"]:
        return jsonify(success=False, returnMessage=validation["message"])

    # convert list-strings into list data-types
    userList = request.args.get("userList").split(",")
    genreList = request.args.get("genreList").split(",")

    # connect to database
    connection = engine.connect()

    # update movie nights table
    mnID = nmnUpdateMovienightsTable(db, connection, userList, genreList)

    # generate new tables for new movie night
    nmnCreateTables(db, mnID)

    # update movie night tables of included users
    nmnUpdateUserMnTables(db, connection, mnID, userList)

    # add new movie night metadata to database
    nmnLogMetadata(db, connection, mnID, genreList, userList)

    # get first page of suggestions from database
    mnSuggestionsTable = getMnSuggestionsTable(db, mnID)
    result = connection.execute(select([mnSuggestionsTable])
                                .where(mnSuggestionsTable.c.page_num == 1))

    # create return JSON before closing connection
    returnJSON = jsonify(suggestions=[dict(row) for row in result],
                         mnID=mnID,
                         success=True)

    connection.close()

    return returnJSON

# ************************************************************* #

@app.route("/loadMovieNight", methods=["GET", "POST"])
def loadMovieNight():
    """ Load an existing movie night """

    # ensure that arguments were passed to script
    if not request.args.get("mnID"):
        raise RuntimeError("missing script argument 'mnID'")
    if not request.args.get("mnPage"):
        raise RuntimeError("missing script argument 'mnPage'")
    if not request.args.get("mnDepth"):
        raise RuntimeError("missing script argument 'mnDepth'")

    # shorthand variables
    mnID = int(request.args.get("mnID"))
    usrPage = int(request.args.get("mnPage"))
    usrDepth = int(request.args.get("mnDepth"))
    usrID = session["user_id"]

    # connect to database
    connection = engine.connect()

    # get table prototypes
    mnTable = getMnTable(db)
    mnSuggestionsTable = getMnSuggestionsTable(db, mnID)
    mnUsersTable = getMnUsersTable(db, mnID)

    # get genres from table
    s = select([mnTable]).where(mnTable.c.sql_id == mnID)
    result_genres = connection.execute(s)
    if not result_genres:
        connection.close()
        return jsonify(success=False,
                       returnMessage="Error when loading movie night")

    genres = result_genres.fetchone()
    genres = genres.genres
    genres = genres.split(",")

    # get suggestions from table
    result = querySuggestionsTable(connection,
                                   mnSuggestionsTable,
                                   usrPage,
                                   genres)

    # error checking
    if result['success'] == True:
        suggestions = result['suggestions']
    else:
        return jsonify([result])

    # if TMDB has no more available movies, return signal to app.js
    if suggestions[0] == "EOQ":
        return jsonify(suggestions=suggestions,
                       success=True,
                       returnMessage="End of query")

    # delete suggestions that should not go into movieJSON
    suggestions = cleanSuggestions(
                                   db,
                                   connection,
                                   suggestions,
                                   mnID,
                                   usrPage,
                                   usrDepth
                                  )

    # if suggestions list is empty, keep loading pages until it's not
    while len(suggestions) < 1:
        usrPage += 1
        result = querySuggestionsTable(connection,
                                       mnSuggestionsTable,
                                       usrPage,
                                       genres)
        if result['success'] == True:
            suggestions = result['suggestions']
        else:
            return jsonify([result])

        suggestions = cleanSuggestions(
                                       db,
                                       connection,
                                       suggestions,
                                       mnID,
                                       usrPage,
                                       usrDepth
                                      )

        # reset user position when finished
        if len(suggestions) > 0:
            resetUserPosition(connection, usrID, usrPage, mnUsersTable)


    # if TMDB has no more available movies, return signal to app.js
    if suggestions[0] == "EOQ":
        return jsonify(suggestions=suggestions,
                       success=True,
                       returnMessage="End of suggestions")

    # return JSON object
    return jsonify(
                   suggestions=suggestions,
                   genres=genres,
                   success=True,
                   returnMessage=("Successfully executed serverside "
                   + "loadMovieNight script")
                  )

# ************************************************************* #

@app.route("/leaveMovieNight", methods=["GET", "POST"])
def leaveMovieNight():
    """ Remove current user from a movie night """

    # ensure that arguments were received
    if not request.args.get("mnID"):
        raise RuntimeError("missing script argument 'mnID'")
    
    # leave movie night
    returnMessage = leaveMnScript(session["user_id"],
                                  request.args.get("mnID"))

    # Success!    
    return jsonify(success=True,
                   returnMessage=returnMessage)

# ************************************************************* #

@app.route("/logRating", methods=["GET", "POST"])
def logRating():
    """ Log how the user rated a suggestion;
        thumbs-up = 1, thumbs-down = -1 """

    # ensure that arguments were received
    if not request.args.get("mnID"):
        raise RuntimeError("missing script argument 'mnID'")
    if not request.args.get("rating"):
        raise RuntimeError("missing script argument 'rating'")
    if not request.args.get("movieID"):
        raise RuntimeError("missing script argument 'movieID'")

    # shorthand variables
    mnID = request.args.get("mnID")
    userID = session["user_id"]
    rating = request.args.get("rating")
    movieID = request.args.get("movieID")

    # get table prototypes
    mnLogTable = getMnLogTable(db, mnID)
    mnUsersTable = getMnUsersTable(db, mnID)
    mnResultsTable = getMnResultsTable(db, mnID)
    userMvTable = getUserMvTable(db, userID)
    mnSuggestionsTable = getMnSuggestionsTable(db, mnID)

    # connect to database
    connection = engine.connect()

    # add rating to movie night log
    ins = mnLogTable.insert().values(movie_id=int(movieID),
                                     user_id=int(userID),
                                     rating=int(rating))
    result = connection.execute(ins)
    if not result:
        connection.close()
        return jsonify(success=False,
                       returnMessage="Error when logging user input")


    # check if movie already in user's movie table
    itExists = (
                db.session.query(userMvTable)
                .filter(userMvTable.c.movie_id==movieID)
                .first()
               )


    # if movie already in user's movie table
    if itExists:
        # update value of rating field by adding value of this rating
        stmt = (
                update(userMvTable)
                .where(userMvTable.c.movie_id==movieID)
                .values(rating=userMvTable.c.rating+rating)
               )
        result = connection.execute(stmt)
        if not result:
            connection.close()
            return jsonify(success=False,
                           returnMessage="Error when logging user input")

    else:
        # insert movie into user's movie table and assign rating
        ins = (
               userMvTable.insert()
               .values(movie_id=int(movieID), rating=int(rating))
              )
        result = connection.execute(ins)
        if not result:
            connection.close()
            return jsonify(success=False,
                           returnMessage="Error when logging user input")


    # check for match if user voted "thumbs up"
    matchStatus = False
    if int(rating) > 0:
        mnUsersTable = getMnUsersTable(db, mnID)
        matchStatus = checkForMatch(connection,
                                    mnLogTable,
                                    mnUsersTable,
                                    movieID)


    # if match, log in results table
    if matchStatus == True:

        # log in results table
        ins = mnResultsTable.insert().values(movie_id=int(movieID),
                                             match_status=1)
        result = connection.execute(ins)
        if not result:
            connection.close()
            return jsonify(success=False,
                           returnMessage="Error when logging user input")


    # if thumbs-down, add to blacklist
    if int(rating) < 0:
        # add to blacklist
        ins = mnResultsTable.insert().values(movie_id=int(movieID),
                                             match_status=-1)
        result = connection.execute(ins)
        if not result:
            connection.close()
            return jsonify(success=False,
                           returnMessage="Error when logging user input")


    # Success!
    connection.close()
    return jsonify(success=True,
                   matchStatus=matchStatus,
                   movieID=movieID,
                   returnMessage="Successfully logged user input")

# ************************************************************* #

@app.route("/loadNextPage", methods=["GET", "POST"])
def loadNextPage():
    """ Load the next page of suggestions for movie night """

    # ensure that arguments were received
    if not request.args.get("mnID"):
        raise RuntimeError("missing script argument 'mnID'")
    if not request.args.get("mnPage"):
        raise RuntimeError("missing script argument 'mnPage'")
    if not request.args.get("genreList"):
        raise RuntimeError("missing script argument 'genreList'")

    # shorthand variables
    mnID = request.args.get("mnID")
    mnPage = request.args.get("mnPage")
    usrID = session["user_id"]

    genreList = request.args.get("genreList")
    genreList = genreList.split(",")

    # get table prototypes
    mnSuggestionsTable = getMnSuggestionsTable(db, mnID)
    mnUsersTable = getMnUsersTable(db, mnID)

    # connect to database
    connection = engine.connect()

    # update mnUsersTable
    stmt = (
            update(mnUsersTable)
            .where(mnUsersTable.c.user_id==usrID)
            .values(user_page=mnPage, user_position=1)
           )
    result = connection.execute(stmt)
    if not result:
        connection.close()
        return jsonify(success=False,
                       returnMessage="Error when loading movie suggestions")

    # if next page of suggestions is available in mnSuggestionsTable:
    if (
        db.session.query(mnSuggestionsTable)
        .filter(mnSuggestionsTable.c.page_num==mnPage)
        .first()
       ):

        # return JSON object with next page of suggestions
        s = (
             select([mnSuggestionsTable])
             .where(mnSuggestionsTable.c.page_num == mnPage)
            )
        result = connection.execute(s)
        if not result:
            connection.close()
            return jsonify(success=False,
                           returnMessage="Error when loading movie suggestions")

        return jsonify(suggestions = [dict(row) for row in result],
                       success=True)

    else:
        # get mnTable prototype
        mnTable = getMnTable(db)

        # incriment num_pages in mnTable for current movie night
        stmt = (
                update(mnTable)
                .where(mnTable.c.sql_id==mnID)
                .values(num_pages=mnPage)
               )
        result = connection.execute(stmt)
        if not result:
            connection.close()
            return jsonify(success=False,
                           returnMessage="Error when loading movie suggestions")

        # query TMDB for next page
        suggestions = getSuggestions(API_KEY, mnPage, genreList)

        # check if final page of results has been reached
        if not suggestions:
            return jsonify(returnMessage="EOQ", success=False)

        # add suggestions to mnSuggestionsTable
        insertSuggestions(connection, mnSuggestionsTable, suggestions)

        # return JSON object with next page of suggestions
        s = (select([mnSuggestionsTable])
             .where(mnSuggestionsTable.c.page_num == mnPage))
        result = connection.execute(s)
        return jsonify(suggestions=[dict(row) for row in result],
                       success=True)

# ************************************************************* #

@app.route("/getMovie", methods=["GET", "POST"])
def getMovie():
    """ Get the title and poster of a movie based on ID """

    # ensure that arguments were received
    if not request.args.get("movieID"):
        raise RuntimeError("missing script argument 'movieID'")
    if not request.args.get("mnID"):
        raise RuntimeError("missing script argument 'mnID'")

    # shorthand variables
    movieID = request.args.get("movieID")
    mnID = request.args.get("mnID")

    mnSuggestionsTable = getMnSuggestionsTable(db, mnID)

    # connect to database
    connection = engine.connect()

    # get title and poster path
    s = (
         select([mnSuggestionsTable])
         .where(mnSuggestionsTable.c.movie_id == movieID)
        )
    result = connection.execute(s)
    result = result.fetchone()

    title = result.title
    posterURL = POSTER_URL_ROOT + result.poster_url

    return jsonify(title=title, posterURL=posterURL)

# ************************************************************* #

@app.route("/updateUserPosition", methods=["GET", "POST"])
def updateUserPosition():
    """ Update a log a user's current position in movie night suggestions """

    # ensure that arguments were received
    if not request.args.get("userPosition"):
        raise RuntimeError("missing script argument 'userPosition'")
    if not request.args.get("mnID"):
        raise RuntimeError("missing script argument 'mnID'")

    # shorthand variables
    userPosition = request.args.get("userPosition")
    mnID = request.args.get("mnID")
    userID = session["user_id"]

    # get table prototype for mn_<id>_users table
    mnUsersTable = getMnUsersTable(db, mnID)

    # connect to database
    connection = engine.connect()

    # change value of user_position in table to value of userPosition 
    # variable
    stmt = (
            update(mnUsersTable)
            .where(mnUsersTable.c.user_id==userID)
            .values(user_position=userPosition)
           )
    result = connection.execute(stmt)
    if not result:
        connection.close()
        return jsonify(
                       success=False,
                       returnMessage=("Error when updating user "
                                      + "position in suggestion list")
                      )

    # close database connection
    connection.close()

    return jsonify(success=True,
                   message="Succesfully updated user position")
