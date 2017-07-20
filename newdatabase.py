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

from sqlalchemy import *

def main():
    """ Create an empty database for a new installation
        of FlickFinder """

    print()
    print("This file creates a new, empty database for FlickFinder.  "
        + "Make sure to back up your current database before running "
        + "this script.")
    print()

    # prompt user until valid input is given
    while True:
        print("Are you sure you want to continue? (Y/n)")

        response = input()

        if response.upper() == "Y" or response.upper() == "YES":
            print()
            print("Creating new database...")
            print()
            makeDatabase()
            print("Done!")
            print()
            break
        elif response.upper() == "N" or response.upper() == "NO":
            print("Goodbye!")
            break
        else:
            pass
        
    return 0


def makeDatabase():
    """ Database creation script """

    engine = create_engine("sqlite:///database.sqlite")
    connection = engine.connect()

    connection.execute('CREATE TABLE "users" ('
                     +   '"sql_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, '
                     +   '"user" TEXT NOT NULL, '
                     +   '"email" TEXT NOT NULL, '
                     +   '"hashed" TEXT NOT NULL, '
                     +   '"name_first" TEXT NOT NULL, '
                     +   '"name_last" TEXT NOT NULL, '
                     +   'UNIQUE ("email" COLLATE NOCASE), '
                     +   'UNIQUE ("user" COLLATE NOCASE)'
                     + ')'
    )

    connection.execute('CREATE TABLE "movieNights" ('
                     +   '"sql_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, '
                     +   '"num_users" INTEGER NOT NULL  DEFAULT 0, '
                     +   '"num_pages" INTEGER NOT NULL DEFAULT 0, '
                     +   '"genres" TEXT NOT NULL, '
                     +   '"date_created" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'
                     + ')'
    )

    connection.close()


# * * * EXECUTE SCRIPT * * *
if __name__ == "__main__":
    main()
