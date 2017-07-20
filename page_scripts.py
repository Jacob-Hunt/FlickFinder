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

# ************************************************************* #

@app.route("/")
def cover():
    """ Root page. """
    # if user is logged in
    if "user_id" in session.keys():
        return redirect(url_for("mainApp"))
    else:
        return render_template("cover.html")

# ************************************************************* #

@app.route("/about", methods=["GET", "POST"])
def about():
    """ About page. """

    # if user is logged in
    if "user_id" in session.keys():
        firstName=getUserFirstName(session["user_id"], db)
    else:
        firstName="Not Logged In"

    return render_template("about.html", firstName=firstName)

# ************************************************************* #

@app.route("/how", methods=["GET", "POST"])
def how():
    """ How to Use FlickFinder page """

    # if user is logged in
    if "user_id" in session.keys():
        firstName=getUserFirstName(session["user_id"], db)
    else:
        firstName="Not Logged In"

    return render_template("howto.html", firstName=firstName)

# ************************************************************* #

@app.route("/privacy", methods=["GET", "POST"])
def privacy():
    """ Privacy Policy """
    return render_template("privacypolicy.htm")

# ************************************************************* #

@app.route("/account", methods=["GET", "POST"])
def account():
    """ Accounts Settings page """

    # if user is logged in
    if "user_id" in session.keys():
        firstName=getUserFirstName(session["user_id"], db)
    else:
        return redirect(url_for("cover"))

    return render_template("account.html", firstName=firstName)

# ************************************************************* #

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Registration page. """

    # if page was reached via registration form
    if request.method == "POST":

        # validate form
        result = validateRegistrationForm(request.form)
        if result['valid'] == False:
            return render_template("register.html")
        else:
            return registerNewUser(request.form)

    # if user arrived via URL or link
    return render_template("register.html")

# ************************************************************* #

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Login script """

    # end any previous session
    session.clear()

    if request.method == "POST":
        # connect to database
        connection = engine.connect()

        # validate form usage
        if not validateLoginForm(request.form).get('valid', False):
            connection.close()
            return render_template("cover.html")

        # convenience variables
        username = request.form.get("user")
        password = request.form.get("pwd")

        # validate password
        if not isPasswordValid(db, connection, username, password):
            connection.close()
            return render_template("cover.html")
        else:
            # log in
            logUserIn(db, connection, username)
            # close connection
            connection.close()
            # redirect user to home page
            return redirect(url_for("mainApp"))

    else:
        # redirect to cover page if user arrived via url
        return redirect(url_for("cover"))

# ************************************************************* #

@app.route("/logout")
def logout():
    """Log user out."""

    # end current session
    session.clear()

    # redirect to login form
    return redirect(url_for("login"))

# ************************************************************* #

@app.route("/app", methods=["GET", "POST"])
def mainApp():
    """ Main app. """
    if "user_id" in session.keys():
        return render_template(
                               "app.html",
                               firstName=getUserFirstName(session["user_id"],
                                                          db),
                               username=getUser(session["user_id"], db)
                              )
    else:
        return redirect(url_for("cover"))

# ************************************************************* #

@app.route("/divs", methods=["GET", "POST"])
def divs():
    """ HTML snippits for app. """
    return render_template(
                           "app_divs.html",

                           firstName=getUserFirstName(
                                      session["user_id"],
                                      db),

                           username=getUser(session["user_id"], db)
                          )
