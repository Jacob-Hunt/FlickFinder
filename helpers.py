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
from sqlalchemy import *
from flask import jsonify, redirect,  url_for, render_template, session
from passlib.apps import custom_app_context as pwd_context

# modules
from sql_tables import *
from config import *

# ************************************************************* #

def getUser(userID, db):
    """ Get username """
    connection = db.engine.connect()

    usrTable = getUsrTable(db)
    s = select([usrTable]).where(usrTable.c.sql_id == userID)
    result = connection.execute(s)

    if result:
        result = result.fetchone()
        connection.close()
        return result.user
    else:
        connection.close()
        return None

# ************************************************************* #

def getUserFirstName(userID, db):
    """ Get user first name """
    connection = db.engine.connect()

    usrTable = getUsrTable(db)
    s = select([usrTable]).where(usrTable.c.sql_id == userID)
    result = connection.execute(s)

    if result:
        result = result.fetchone()
        connection.close()
        return result.name_first
    else:
        connection.close()
        return None

# ************************************************************* #

def getUserLastName(userID, db):
    """ Get user last name """
    connection = db.engine.connect()

    usrTable = getUsrTable(db)
    s = select([usrTable]).where(usrTable.c.sql_id == userID)
    result = connection.execute(s)

    if result:
        result = result.fetchone()
        connection.close()
        return result.name_last
    else:
        connection.close()
        return None

# ************************************************************* #

def addFriend(db, connection, user_id_1, user_id_2):
    """ Add users to each other's friends lists """

    # friend list table prototypes
    flTable1 = getFlTable(db, user_id_1)
    flTable2 = getFlTable(db, user_id_2)

    # friend request table prototypes
    frTable1 = getFrTable(db, user_id_1)
    frTable2 = getFrTable(db, user_id_2)

    # add user ids to friend lists of both users, return False if unsuccessful
    connection.execute(flTable1.insert().values(other_user_id=int(user_id_2)))
    connection.execute(flTable2.insert().values(other_user_id=int(user_id_1)))

    # delete from friend-request tables of both users, return false if unsuccessful
    connection.execute(frTable1.delete()
                       .where(frTable1.c.other_user_id == user_id_2))
    connection.execute(frTable2.delete()
                       .where(frTable2.c.other_user_id == user_id_1))

# ************************************************************* #

def checkForMatch(connection, mnLogTable, mnUsersTable, movieID):
    """ Check the match-status of a suggestion """
    # query mn_<id>_log for user_id of all entries with movie_id of 
    # current suggestion and add to an array
    logArray = []
    s = select([mnLogTable.c.user_id]).where(and_(
                                             mnLogTable.c.movie_id == movieID, 
                                             mnLogTable.c.rating == 1))
    result = connection.execute(s)
    for row in result:
        logArray.append(row[mnLogTable.c.user_id])

    # query mn_<id>_users for all user_id and add to an array
    usersArray = []
    s = select([mnUsersTable.c.user_id])
    result = connection.execute(s)
    for row in result:
        usersArray.append(row[mnUsersTable.c.user_id])

    # set match status to True
    matchStatus = True

    # check for match
    for user in usersArray:
        if user not in logArray:
            matchStatus = False
            break

    # return match status
    return matchStatus

# ************************************************************* #

def getSuggestions(API_KEY, pageNumber, genreList):
    """ Get movie suggestions from TMDB """

    # generate TMDB query
    query = ("https://api.themoviedb.org/3/discover/movie?api_key=" 
             + API_KEY 
             + "&language=en-US&sort_by=vote_count.desc&include_adult=false&include_video=true&page=" 
             + str(pageNumber) 
             + "&with_genres=")

    # append genre preferences to TMDB query
    for genre in genreList:
        query += genre
        query += "%7C%20"

    # execute query and return as JSON object
    r = requests.get(query)
    r = r.json()

    for result in r["results"]:
        result["page_number"] = pageNumber

    return r["results"]

# ************************************************************* #

def getMovieInfo(API_KEY, movieID):
    """ Get information on a movie from TMDB """

    # generate TMDB query URL
    query = ("https://api.themoviedb.org/3/movie/"
             + str(movieID)
             + "?api_key="
             + API_KEY
             +"&language=en-US")

    # query TMDB
    r = requests.get(query)
    r = r.json()

    # return movie info
    return r

# ************************************************************* #

def insertSuggestions(connection, mnSuggestionsTable, suggestions):
    """ Add a JSON of TMDB suggestions to suggestions table """
    sgCounter = 0
    for suggestion in suggestions:
        ins = mnSuggestionsTable.insert().values(
                            query_num = 1,
                            page_num = suggestion["page_number"],
                            query_depth = sgCounter,
                            movie_id = suggestion["id"],
                            title = suggestion["original_title"],
                            description = suggestion["overview"],
                            poster_url = suggestion["poster_path"],
                            release_date = suggestion["release_date"],
                            genres = str(suggestion["genre_ids"]),
                            rating = float(suggestion["vote_average"]),
                            )

        # ensure success
        result = connection.execute(ins)
        if not result:
            connection.close()
            return jsonify(
                           success=False,
                           returnMessage=("Error when inserting movie "
                                          + "suggestions")
                          )
        else:
            sgCounter += 1

        # -- end of loop --

    return jsonify(
                   success=True,
                   returnMessage="Successfully inserted suggestions"
                  )

# ************************************************************* #

def querySuggestionsTable(connection, mnSuggestionsTable, usrPage, genreList):
    """ Get a page of suggestions from suggestions table """
    s = (
         select([mnSuggestionsTable])
         .where(mnSuggestionsTable.c.page_num == usrPage)
        )
    result = connection.execute(s)

    if not result:
        connection.close()
        return {
                   'success': False,
                   'returnMessage': "Error when loading movie suggestions"
               }
    suggestions = []
    for row in result:
        suggestions.append(dict(row))

    # if page not available, query TMDB
    if not suggestions:
        suggestions = getSuggestions(API_KEY, usrPage, genreList)
        # if getSuggestions returned any suggestions
        if len(suggestions) > 0:
            # add suggestions to suggestions table
            insertSuggestions(connection, mnSuggestionsTable, suggestions)
        else:
            # return and end-of-query signal
            return {
                   'success': True,
                   'suggestions': ["EOQ"]
                   }
         
    
    # return suggestions
    return {
               'success': True,
               'suggestions': suggestions
           }

# ************************************************************* #

def cleanSuggestions(db, connection, suggestions, mnID, usrPage, usrDepth):
    """ Check weather or not a suggestion should go in movieJSON """

    # debugging
    print(str(suggestions))

    # skip clearing if end-of-query reached
    if suggestions[0] == "EOQ":
        return suggestions

    # get table prototype
    mnResultsTable = getMnResultsTable(db, mnID)

    # create array prototype
    resultIDs = []

    # query mnResults table and put mnIDs in an array
    s = select([mnResultsTable.c.movie_id])
    result = connection.execute(s)
    for row in result:
        movieID = row[mnResultsTable.c.movie_id]
        resultIDs.append(movieID)

    suggestionsCpy = suggestions.copy()

    for suggestion in suggestionsCpy:
        # check if suggestion's query_depth is less than user's query_depth
        if int(usrDepth) > suggestion["query_depth"]:
            # delete if suggestion's query_depth less than user's
            suggestions.remove(suggestion)
        # delete if suggestion is already in results table
        elif suggestion["movie_id"] in resultIDs:
            suggestions.remove(suggestion)

    return suggestions

# ************************************************************* #

def resetUserPosition(connection, usrID, usrPage, mnUsersTable):
    """ Record user position in mnUsersTable """

    stmt = (
            update(mnUsersTable)
            .where(mnUsersTable.c.user_id==usrID)
            .values(user_page=usrPage, user_position=0)
           )
    result = connection.execute(stmt)
    if not result:
        connection.close()
        return jsonify(success=False,
                       returnMessage="Error when resetting user position")
    else:
        return jsonify(success=True,
                       returnMessage="Successfully reset user position")

# ************************************************************* #

def allVotesIn(connection, mnLogTable, mnUsersTable, movieID):
    """ Returns true if all users in a movie night have voted
        on movie with movieID"""

    # query mn_<id>_log for user_id of all entries with movie_id of 
    # current suggestion and add to an array
    logArray = []
    s = (select([mnLogTable.c.user_id])
         .where(mnLogTable.c.movie_id == movieID))
    result = connection.execute(s)
    for row in result:
        logArray.append(row[mnLogTable.c.user_id])
    # debugging
    print("logArray: " + str(logArray))

    # query mn_<id>_users for all user_id and add to an array
    usersArray = []
    s = select([mnUsersTable.c.user_id])
    result = connection.execute(s)
    for row in result:
        usersArray.append(row[mnUsersTable.c.user_id])
    # debugging
    print("usersArray: " + str(usersArray))

    # set return status to True
    allVotesIn = True

    # check if any users haven't voted
    for user in usersArray:
        if user not in logArray:
            allVotesIn = False
            break

    # return status
    return allVotesIn

# ************************************************************* #

def registerNewUser(formInput):
    """ Add database info for new user """

    # shorthand variables
    username = formInput.get("user").lower()
    email = formInput.get("email").lower()
    pw = formInput.get("pwd")
    confirm = formInput.get("confirm")
    first = formInput.get("first")
    last = formInput.get("last")

    # encrypt password
    hashed = pwd_context.encrypt(pw)

    # try adding user to main Users table
    success = insertToUsersTable(username, email, hashed, first, last)
    if not success:
        return render_template("register.html")

    # get sql_id of new user
    result = Users.query.filter_by(user=username).first()
    sql_id = result.sql_id

    # create database tables for new user
    createNewUserTables(sql_id)

    return redirect(url_for("cover"))

# ************************************************************* #

def insertToUsersTable(username, email, hashed, first, last):
    """ Add new user to main database users table """

    newUser = Users(username, email, hashed, first, last)
    db.session.add(newUser)
    try:
        db.session.commit()
    except:
        return False
    return True

# ************************************************************* #

def createNewUserTables(sql_id):
    """ Create database tables for new user """

    # create friend requests table
    frTable = getFrTable(db, sql_id)
    frTable.create(bind=db.engine)

    # create friends list table
    flTable = getFlTable(db, sql_id)
    flTable.create(bind=db.engine)

    # create movie list table
    mvTable = getUserMvTable(db, sql_id)
    mvTable.create(bind=db.engine)

    # create movie nights table
    mnTable = getUserMnTable(db, sql_id)
    mnTable.create(bind=db.engine)

# ************************************************************* #

def validateRegistrationForm(formInput):
    """ Validate registration form input """

    if not formInput.get("user"):
        return {'valid': False,
               'message': "Missing form input: user"}
    elif not formInput.get("email"):
        return {'valid': False,
               'message': "Missing form input: email"}
    elif not formInput.get("pwd"):
        return {'valid': False,
               'message': "Missing form input: pwd"}
    elif not formInput.get("confirm"):
        return {'valid': False,
               'message': "Missing form input: confirm"}
    elif not formInput.get("first"):
        return {'valid': False,
               'message': "Missing form input: first"}
    elif not formInput.get("last"):
        return {'valid': False,
               'message': "Missing form input: last"}
    elif formInput.get("pwd") != formInput.get("confirm"):
        return {'valid': False,
               'message': "Passwords don't match"}
    else:
        return{'valid': True,
              'message': "Successfully validated form"}

# ************************************************************* #

def validateLoginForm(formInput):
    """ Validate login form """

    # validate form usage'
    if not formInput.get("user"):
        return {'valid': False, 'message': "Missing form input: user"}
    elif not formInput.get("pwd"):
        return {'valid': False, 'message': "Missing form input: password"}
    else:
        return {'valid': True, 'message': "Login form validated"}

# ************************************************************* #

def isPasswordValid(db, connection, username, password):
    """ Check if username/password combination is valid """

    # validate login
    usrTable = getUsrTable(db)
    s = select([usrTable]).where(func.lower(usrTable.c.user) == func.lower(username))
    result = connection.execute(s)
    result = result.fetchone()

    if not result:
        return False
    elif not pwd_context.verify(password, result.hashed):
        return False
    else:
        return True

# ************************************************************* #

def logUserIn(db, connection, username):
    """ Start new user session """
    usrTable = getUsrTable(db)
    session["user_id"] = (connection.execute(select([usrTable])
                          .where(func.lower(usrTable.c.user) == func.lower(username)))
                          .fetchone().sql_id)

# ************************************************************* #

def validateArgs(argsDict, requiredArgsList):
    """ Ensure that serverside script received all required
        arguments """

    for argument in requiredArgsList:
        if not argsDict.get(argument):
            return {'success': False,
                    'message': "Missing argument: '" + argument + "'"}

    return {'success': True,
            'message': "Successfully validated arguments"}

# ************************************************************* #

def nmnCreateTables(db, mnID):
    """ Log new movie night data in database,
        returns movie night ID """

    # get remainting table prototypes
    mnLogTable = getMnLogTable(db, mnID)
    mnResultsTable = getMnResultsTable(db, mnID)
    mnSuggestionsTable = getMnSuggestionsTable(db, mnID)
    mnUsersTable = getMnUsersTable(db, mnID)

    # create tables
    mnLogTable.create(bind=db.engine)
    mnResultsTable.create(bind=db.engine)
    mnSuggestionsTable.create(bind=db.engine)
    mnUsersTable.create(bind=db.engine)

# ************************************************************* #

def nmnUpdateMovienightsTable(db, connection, userList, genreList):
    """ Add new movie night to movie nights table and return
        sql_id of new movie night """
    # get mnTable prototype
    mnTable = getMnTable(db)

    # add movie night to movieNights table
    result = connection.execute(mnTable.insert()
                                .values(num_users=len(userList) + 1,
                                        num_pages=2,
                                        genres=str(genreList)))

    # return sql_key of new movie night
    return result.inserted_primary_key[0]


# ************************************************************* #

def nmnUpdateUserMnTables(db, connection, mnID, userList):
    """ Add new movie night to tables of included users """

    # add movie night ID to movie night table of current user
    mnTableSelf = getUserMnTable(db, session["user_id"])
    connection.execute(mnTableSelf.insert().values(mn_id=mnID))

    # add movie night ID to movie night tables of all included friends
    for user in userList:
        userMnTable = getUserMnTable(db, int(user))
        connection.execute(userMnTable.insert().values(mn_id=mnID))

# ************************************************************* #

def nmnLogMetadata(db, connection, mnID, genreList, userList):
    """ Add metadata of new movie night to relevant tables """

    # get table prototypes
    mnUsersTable = getMnUsersTable(db, mnID)

    # add current user to mnUsers table
    connection.execute(mnUsersTable.insert()
                       .values(user_id=session["user_id"],
                               user_page=1,
                               user_position=1))

    # add included friends to mnUsers table
    for user in userList:
        connection.execute(mnUsersTable.insert().values(user_id=int(user),
                                           user_page=1,
                                           user_position=1))

    # get initial suggestions
    suggestions_p1 = getSuggestions(API_KEY, 1, genreList)
    suggestions_p2 = getSuggestions(API_KEY, 2, genreList)
    suggestions = suggestions_p1 + suggestions_p2

    # add suggestions to mnSuggestionsTable
    addSuggestions(db, connection, mnID, suggestions)

# ************************************************************* #

def addSuggestions(db, connection, mnID, suggestions):

    mnSuggestionsTable = getMnSuggestionsTable(db, mnID)
    sgCounter = 0
    for suggestion in suggestions:
        connection.execute(mnSuggestionsTable
                           .insert().values(
                               query_num = 1,
                               page_num = suggestion["page_number"],
                               query_depth = sgCounter,
                               movie_id = suggestion["id"],
                               title = suggestion["original_title"],
                               description = suggestion["overview"],
                               poster_url = suggestion["poster_path"],
                               release_date = suggestion["release_date"],
                               genres = str(suggestion["genre_ids"]),
                               rating = float(suggestion["vote_average"]),
                               )
                          )
        # incriment counter
        sgCounter += 1

# ************************************************************* #

def validatePasswordByUserID(password, userID):
    """ Check if a password supplied by user matches password in database """

    # connect to database
    connection = db.engine.connect()

    # get table prototypes
    usrTable = getUsrTable(db)

    # get hashed password
    result = (connection.execute(select([usrTable.c.hashed])
              .where(usrTable.c.sql_id == userID))
              .fetchone())
    if not result:
        return False
    else:
        hashed = result.hashed

    # validate password
    if not pwd_context.verify(password, result.hashed):
        return False
    else:
        return True

# ************************************************************* #

def updatePassword(userID, newPassword):
    """ Change password of a user in users database"""
 
    # encrypt new password
    hashed = pwd_context.encrypt(newPassword)

    # get table prototype
    usrTable = getUsrTable(db)

    # connect to database
    connection = engine.connect()

    # change database hash to new hash
    connection.execute(
                       update(usrTable)
                       .where(usrTable.c.sql_id==session["user_id"])
                       .values(hashed=hashed)
                      )

    # close connection and return JSON
    connection.close()
    return jsonify(success=True,
                   returnMessage="Password successfully changed")

# ************************************************************* #

def deleteFromFriendLists(userID):
    """ Remove a user from the friend lists of other users """

    # connect to database
    connection = engine.connect()

    # get prototype for friend list
    flTable = getFlTable(db, userID)

    # get user IDs of all friends and add to array
    friendIDs = []
    result = connection.execute(select([flTable.c.other_user_id]))
    for row in result:
        friendIDs.append(row[flTable.c.other_user_id])

    # for each friend
    for ID in friendIDs:
        # get prototype for this friend's friend-table
        friendFlTable = getFlTable(db, ID)
        # remove row where user_id == userID from table
        connection.execute(friendFlTable.delete()
                           .where(friendFlTable.c.other_user_id == userID))

    # close connection
    connection.close()

# ************************************************************* #

def deleteFromFriendRequestLists(userID):
    """ Remove a user from the friend request lists of other users """

    # connect to database
    connection = engine.connect()

    # get prototype for friend request list
    frTable = getFrTable(db, userID)

    # get user IDs of all friends and add to array
    friendIDs = []
    result = connection.execute(select([frTable.c.other_user_id]))
    for row in result:
        friendIDs.append(row[frTable.c.other_user_id])

    # for each friend
    for ID in friendIDs:
        # get prototype for this friend's friend-table
        friendFrTable = getFrTable(db, ID)
        # remove row where user_id == userID from table
        connection.execute(friendFrTable.delete()
                           .where(friendFrTable.c.other_user_id == userID))

    # close connection
    connection.close()

# ************************************************************* #

def leaveAllMovienights(userID):
    """ Remove a user from all movie nights """

    # connect to database
    connection = engine.connect()

    # get prototype for <userID>_movieNights
    mnListTable = getUserMnTable(db, userID)

    # get all mnIDs from movieNights table and add to an array
    mnIDlist = []
    result = connection.execute(select([mnListTable.c.mn_id]))
    for row in result:
        mnIDlist.append(row[mnListTable.c.mn_id])

    # for each mnID
    for ID in mnIDlist:
        # leave movie night
        leaveMnScript(userID, str(ID))

    return True

# ************************************************************* #

def deleteUserTables(userID):
    """ Delete a user's metadata tables """

    # get table prototypes
    tables = [getFrTable(db, userID),
              getFlTable(db, userID),
              getUserMvTable(db, userID),
              getUserMnTable(db, userID)]

    # drop tables
    for table in tables:
        table.drop(engine)

    return True

# ************************************************************* #

def leaveMnScript(userID, mnID):
    """ Remove user from a given movie night """

    # get table prototypes
    mnResultsTable = getMnResultsTable(db, mnID)
    mnLogTable = getMnLogTable(db, mnID)
    mnUsersTable = getMnUsersTable(db, mnID)
    userMnTable = getUserMnTable(db, userID)

    # connect to database
    connection = engine.connect()

    # scan mnLogTable for any movies which current user has downvoted
    s = (
         select([mnLogTable])
         .where(mnLogTable.c.user_id == userID
                and mnLogTable.c.rating < 0)
        )
    result = connection.execute(s)

    # list prototype
    downvoteArray = []

    # for each suggestion in query result
    for row in result:
        # add each movieID to a downvoteArray
        downvoteArray.append(row[mnLogTable.c.movie_id])

    # delete user's entries in mn_<id>_log
    d = mnLogTable.delete().where(mnLogTable.c.user_id == userID)
    connection.execute(d)

    # delete user from mn_<id>_users
    d = mnUsersTable.delete().where(mnUsersTable.c.user_id == userID)
    connection.execute(d)

    # delete movie night from userMnTable
    d = userMnTable.delete().where(userMnTable.c.mn_id == mnID)
    connection.execute(d)

    # if no more users in movie night, delete movie night from
    # database)
    s = select([mnUsersTable])
    result = connection.execute(s)
    exists = result.fetchone()
    if not exists:

        # generate a list of tables to drop
        tablesToDelete = []
        tablesToDelete.append(getMnLogTable(db, mnID))
        tablesToDelete.append(getMnResultsTable(db, mnID))
        tablesToDelete.append(getMnSuggestionsTable(db, mnID))
        tablesToDelete.append(getMnUsersTable(db, mnID))

        # drop all tables in list
        for table in tablesToDelete:
            table.drop(engine)

        # delete movie night from movie nights table
        mnTable = getMnTable(db)
        d = mnTable.delete().where(mnTable.c.sql_id == mnID)
        connection.execute(d)

        # close database connection
        connection.close()

        returnMessage = ("Successfully left movie night; last user "
                         + "movie night, movie night deleted")

        return returnMessage


    # if users are still in movie night, update results table
    for suggID in downvoteArray:

        # check to see if everyone else in movie night upvoted
        # suggestion
        matchStatus = checkForMatch(connection,
                                    mnLogTable,
                                    mnUsersTable,
                                    suggID)

        # if so, switch match status to "1" in results table
        if matchStatus == True:
            # change status from reject to match
            u = (mnResultsTable.update()
                 .where(mnResultsTable.c.movie_id == suggID)
                 .values(match_status = 1))
            connection.execute(u)

        # if some users have not yet voted on movie, delete
        # movie from results table
        elif not allVotesIn(connection,
                            mnLogTable,
                            mnUsersTable,
                            suggID):
            d = (mnResultsTable.delete()
                 .where(mnResultsTable.c.movie_id == suggID))
            connection.execute(d)

        return "Successfully left movie night"

# ************************************************************* #

def removeFromUsersTable(userID):
    """ Remove a user from users table """
    connection = engine.connect()
    usrTable = getUsrTable(db)
    connection.execute(usrTable.delete()
                       .where(usrTable.c.sql_id == userID))
    connection.close()
    return True
