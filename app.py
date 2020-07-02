################################################################################
# Application global read-only state using Singleton pattern
#
# Purpose: The App class is a singleton with the responsibility of managing
# the application's global read-only state.  This includes processing the
# application configuration file, and creating and providing access to the
# (Redis Labs) database connection, News API, and logging functionalities.  See
# the Singleton pattern: https://en.wikipedia.org/wiki/Singleton_pattern.
#
# The app uses the News API to access news data and produce news reports:
# - https://github.com/mattlisiv/newsapi-python
# - https://newsapi.org/docs
#
# The app uses the configparser module to read in a standard config file of
# key=value format: https://docs.python.org/3/library/configparser.html
#
# Author: Kevin Browne
# Contact: brownek@mcmaster.ca
#
################################################################################

from newsapi.newsapi_client import NewsApiClient
import configparser
import redis
from logger import *

# App singleton contains all of the read-only state data that must be
# accessible across the application: configuration data, logging and the
# database connection.
class App():

    __instance = None

    # Setup the singleton based on the config file
    def setup(self):

        # Load the config file using the Config Parser module
        config = configparser.ConfigParser()
        config.read("config.cfg")

        # setup the News API module
        self.newsapi = NewsApiClient(api_key=config["NewsAPI"]["apikey"])

        # setup database connection based on the config file values
        self.dbconn = redis.Redis(
            host=config["Database"]["host"],
            port=config["Database"]["port"],
            password=config["Database"]["password"],
            decode_responses=True)

        # Setup logging chain-of-reponsibility chain
        self.__logger = None
        if (config["Logging"]["console"] == "TRUE"):
            self.__logger = ConsoleLogger( self.__logger )
        if (config["Logging"]["file"] == "TRUE"):
            self.log_filename = config["Logging"]["log_filename"]
            self.__logger = FileLogger( self.__logger, self.log_filename )
        if (config["Logging"]["database"] == "TRUE"):
            self.__logger = DatabaseLogger( self.__logger, self.dbconn )

    # Log a message
    def log(self,message):
        if self.__logger == None:
            return
        else:
            self.__logger.log(message)

    # Creates or returns the singleton instance
    def __new__(cls):
        if (cls.__instance is None):
            cls.__instance = super(App, cls).__new__(cls)
            cls.__instance.setup()

        return cls.__instance
