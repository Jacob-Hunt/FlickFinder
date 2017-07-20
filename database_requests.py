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


@app.route("/sendFriendRequest", methods=["GET", "POST"])
def sendFriendRequest():
    """ Send friend request to other user. """
    # get query from html form
    q = request.args.get("fr_addField")

    # find requested user in table
    result = Users.query.filter(func.lower(Users.user)==func.lower(q)).first()
    if not result:
        result = Users.query.filter(func.lower(Users.email)==func.lower(q)).first()

    # return error message if user doesn't exist
    if not result:
        return jsonify(success=False, returnMessage="User doesn't exist")

    # other user ID
    ouID = result.sql_id

    # if user tried to friend self
    if ouID == session['user_id']:
        return jsonify(success=False,
                       returnMessage="Cannot send friend request to self")

    # table prototype for sqlalchemy
    flTable = getFlTable(db, session["user_id"])

    # check if already friends
    connection = engine.connect()
    s = select([flTable]).where(flTable.c.other_user_id == ouID)
    result = connection.execute(s)
    result = result.fetchone()
    if result:
        connection.close()
        return(jsonify(success=False, returnMessage="Already friends"))

    # sqlalchemy table prototypes
    frTableSelf = getFrTable(db, session["user_id"])
    frTableOther = getFrTable(db, ouID)

    # if friend request from other user already received, automatically
    # accept
    s = select([frTableSelf]).where(frTableSelf.c.other_user_id == ouID)
    result = connection.execute(s)
    result = result.fetchone()
    if result:
        if result.received == 1:
            result = addFriend(db, connection, session["user_id"], ouID)
            connection.close()
            if result:
                return jsonify(success=True,
                               returnMessage="You are now friends!")
            else:
                return jsonify(
                               success=False,
                               returnMessage=("Error when processing "
                                              + "friend request")
                              )

    # check if friend request already sent
    s = select([frTableSelf]).where(frTableSelf.c.other_user_id == ouID)
    result = connection.execute(s)
    result = result.fetchone()
    if result:
        if result.sent == 1:
            connection.close()
            return jsonify(
                           success=False,
                           returnMessage=("You have already sent a "
                                         + "friend request")
                          )

    # if checks are passed, update friend-request tables to reflect
    # new request
    ins = frTableSelf.insert().values(other_user_id=int(ouID),
                                      sent=int(1))
    result = connection.execute(ins)
    if not result:
        connection.close()
        return jsonify(success=False,
                       returnMessage="Error when processing friend request")

    ins = frTableOther.insert().values(other_user_id=int(session["user_id"]),
                                                         received=int(1))
    result = connection.execute(ins)
    if not result:
        connection.close()
        return jsonify(success=False,
                       returnMessage="Error when processing friend request")

    # return status
    connection.close()
    return jsonify(success=True, returnMessage="Friend request sent!")


@app.route("/acceptFriendRequest", methods=["GET", "POST"])
def acceptFriendRequest():
    """ Accept a friend request sent by another user """

    # validate form input
    if not request.args.get("usrID"):
        print("Missing argument 'usrID'")
        jsonify(success=False,
                message="acceptFriendRequest script failed")

    # shorthand variable
    usrID = request.args.get("usrID")

    # connect to database
    connection = engine.connect()

    # update database tables
    addFriend(db, connection, session["user_id"], usrID)

    # return status
    return jsonify(success=True,
                   message="acceptFriendRequest script successfully executed")


@app.route("/declineFriendRequest", methods=["GET", "POST"])
def declineFriendRequest():
    """ Decline a friend request sent by another user """

    # validate form input
    if not request.args.get("usrID"):
        print("Missing argument 'usrID'")
        jsonify(success=False,
                returnMessage="/declineFriendRequest missing argument: usrID")

    # shorthand variable
    usrID = request.args.get("usrID")

    # connect to database
    connection = engine.connect()

    # get table prototypes
    frTableSelf = getFrTable(db, session["user_id"])
    frTableOther = getFrTable(db, usrID)

    # delete friend requests from both tables
    result = connection.execute(frTableSelf.delete()
                                .where(frTableSelf.c.other_user_id
                                       == usrID))
    if not result:
        return jsonify(success=False,
                       returnMessage=("Could not delete from "
                                    + "friend request table"))

    result = connection.execute(frTableOther.delete()
                               .where(frTableOther.c.other_user_id
                                      == session["user_id"]))
    if not result:
        return jsonify(success=False,
                       returnMessage=("Could not delete from friend "
                                    + "request table of other user"))

    # return status
    return jsonify(success=True,
                   message="Successfully declined friend request")


@app.route("/changePassword", methods=["GET", "POST"])
def changePassword():
    """ Serverside script for changing password from account settings
        menu """

    # convenience variables
    pwdNew = request.args.get("pwdNew")
    pwdNewConfirm = request.args.get("pwdNewConfirm")
    pwdCurrent = request.args.get("pwdCurrent")

    # validate user input
    if not request.args.get("pwdNew")\
    or not request.args.get("pwdNewConfirm")\
    or not request.args.get("pwdCurrent"):
        return jsonify(success=False,
                       returnMessage="Missing argument for /changePassword")

    # check to make sure new password matches confirmation field
    if pwdNew != pwdNewConfirm:
        return jsonify(success=False, returnMessage="New passwords don't match")

    # get table prototype
    usrTable = getUsrTable(db)

    # if user provided correct password
    if validatePasswordByUserID(pwdCurrent, session["user_id"]):
        # change password in database
        return updatePassword(session["user_id"], pwdNew)
    else:
        return jsonify(success=False, returnMessage="Incorrect password")


@app.route("/deleteAccount", methods=["GET", "POST"])
def deleteAccount():
    """ Serverside script for deleting account from account settings
        menu """

    # validate password
    if not request.args.get("pwdCurrent"):
        return jsonify(success=False, returnMessage="Password not submitted")
    if not validatePasswordByUserID(request.args.get("pwdCurrent"),
                                    session["user_id"]):
        return jsonify(success=False, returnMessage="Incorrect password")

    # delete user from friend lists of other users
    deleteFromFriendLists(session["user_id"])
    # delete user from friend request lists of other users
    deleteFromFriendRequestLists(session["user_id"])
    # delete user from movienight lists of users
    leaveAllMovienights(session["user_id"])
    # delete user's metadata tables
    deleteUserTables(session["user_id"])
    # delete user from users table
    removeFromUsersTable(session["user_id"])
    # return JSON
    return jsonify(success=True, returnMessage="Successfully deleted account")
