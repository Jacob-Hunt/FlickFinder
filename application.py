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


# *** IMPORTS ***

# libraries
import os

# local modules
from config import *
from helpers import *
from page_scripts import *
from JSON_request_scripts import *
from database_requests import *
from movienight_scripts import *

# *** MAIN FUNCTION ***

def main():

    print("API_KEY: " + API_KEY)

    # run server
    app.run(host = os.getenv('IP', server_address),
            port = int(os.getenv('PORT', port_number)))


# *** BEGIN PROGRAM EXECUTION ***

if __name__ == "__main__":
    main()
