################################################################################
# Main application script
#
# Purpose: This application allows users to define reports of news information
# by selecting a source (e.g. CBC News, NBC News, etc) and adding optional
# search terms for the title and/or entire article.  Report definitions are
# saved in a Redis Labs database with an associated name.  The application
# allows users to generate reports based on the report definitions, which
# involves utilizing the News API.  See the documentation file for more details.
#
# This script runs the application using the MVC objects.  This script should
# arguably be included in the MVC module, but I keep it separate here under the
# assumption the application may grow in the future, incorporate more modules,
# etc.
#
# Author: Kevin Browne
# Contact: brownek@mcmaster.ca
#
################################################################################

from mvc import *

controller = Controller(View(), Model())
controller.run()
