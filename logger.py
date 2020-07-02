################################################################################
# Logger using Chain-of-Responsibility pattern
#
# Purpose: Defines a general logger class for carrying out logging
# functionality, as well as logger subclasses for console, file, and database
# logging.  The loggers follow the chain-of-responsbility pattern:
#   https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern
#
# Author: Kevin Browne
# Contact: brownek@mcmaster.ca
#
################################################################################

from abc import ABC, abstractmethod
import datetime

# Define what it means to be a logger object in chain-of-responsiblity pattern
class Logger(ABC):

    def log(self, message):
        if (self.__next_logger == None):
            return
        else:
            self.__next_logger.log(message)

    def __init__(self,next_logger):
        self.__next_logger = next_logger

# Logs directly to a file, appends message on next line
class FileLogger(Logger):

    def __init__(self,next_logger,log_filename):
        self.__log_file = open(log_filename, "a+")
        super().__init__(next_logger)

    def log(self, message):
        self.__log_file.write(str(datetime.datetime.now()) + ": " + message \
                              + "\n")
        super().log(message)

# Logs message directly to the console
class ConsoleLogger(Logger):

    def log(self, message):
        print(str(datetime.datetime.now()) + ": " + message)
        super().log(message)

# Logs message to the redis database, uses timestamp as field in a hash with key
# "log", and message is the value
class DatabaseLogger(Logger):

    def __init__(self,next_logger,dbconn):
        self.__dbconn = dbconn
        super().__init__(next_logger)

    def log(self, message):
        self.__dbconn.hset("log", str(datetime.datetime.now()), message)
        super().log(message)