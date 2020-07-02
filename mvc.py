################################################################################
# Model-View-Controller pattern for user interaction
#
# Purpose: The core application functionality is carried out using the MVC
# pattern, with a view for user interface (console), a model for database
# access, and controller for communication between view and model as well as
# business logic (in this case, report generation).  See the MVC pattern:
# https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller.  If
# the individual classes in this module got much larger, I'd pull them out
# into their own modules/files... but given their size, it's likely more
# readable to include them all in one file.
#
# Author: Kevin Browne
# Contact: brownek@mcmaster.ca
#
################################################################################

from app import *
from report import *
from time import time

# View is responsible for user interface... i.e. presenting options to the user
# and collecting user input.  Each method represents a different option page.
# We use decorator @staticmethod because the methods will access no object
# instance variables.
class View():

    @staticmethod
    def main_page():
        print("****************************************")
        print("(1) Create a new report")
        print("(2) Print a report")
        print("(3) Exit")
        option = input("Enter number to select an option: ")
        return int(option)

    @staticmethod
    def create_report():
        print("****************************************")
        print("Enter the data below to create a report!")
        report_name = input("Name: ")
        print("Some potential source IDs: cbc-news, abc-news, cnn, espn, " + \
              "cbs-news, buzzfeed, nbc-news, usa-today")
        source_id = input("Source ID: ")
        return report_name, source_id

    @staticmethod
    def add_to_report():
        print("Do you wish to add more data to the report?")
        print("(1) Add a search term for article title only")
        print("(2) Add a search term for article title and body")
        print("(3) Finish report creation")
        option = input("Enter number to select an option: ")
        return int(option)

    @staticmethod
    def search_term():
        search_term = input("Enter search term: ")
        return search_term

    @staticmethod
    def print_report(report_names):
        i = 1
        for report in report_names:
            print("(" + str(i) + ") " + report)
            i = i + 1
        report_id = int(input("Enter number of the report to generate: "))
        output_filename = input("Enter filename for report output: ")
        return report_id, output_filename


# Controller uses the view object to present the UI to the user, and manipulates
# data in the database using the model.  The controller also handles business
# logic such as creating the decorator pattern objects necessary to write the
# report to a file.
class Controller():

    # Controller initialized with a view and model object
    def __init__(self,view, model):
        self.__view = view
        self.__model = model

    # Have the view present main page with options to create/print reports, exit
    def run(self):

        while True:
            option = self.__view.main_page()
            App().log("Selected main page option " + str(option))
            if (option == 1):
                self.__create_report()
            elif (option == 2):
                self.__print_report()
            else:
                print("Goodbye!")
                exit()

    # create a report, first with the base information required, and then
    # ask for any additions to the report with different search terms
    def __create_report(self):

        # get the base report data... a report name and source id
        report_name, source_id = self.__view.create_report()
        App().log("Created report: name=" + report_name)

        # get any additions to the report in terms of title or all searches
        title_search_terms = []
        all_search_terms = []
        while True:

            # keep asking for search terms, append to the relevant list
            option = self.__view.add_to_report()
            if (option == 1):
                search_term = self.__view.search_term()
                title_search_terms.append(search_term)
                App().log("Created report title search term: " + search_term)
            elif (option == 2):
                search_term = self.__view.search_term()
                all_search_terms.append(search_term)
                App().log("Created report all search term: " + search_term)
            else:
                # when done, have the model save our report data to the database
                self.__model.create_report(report_name, source_id, \
                                           ','.join(title_search_terms), \
                                           ','.join(all_search_terms))
                App().log("Finished created report")
                break

    # Present the user with a list of all possible reports, ask them to select
    # a report to print and the output filename.  Create the base report and
    # any decorator objects necessary to create the report, then write it to the
    # output file.
    def __print_report(self):

        # ask user to select the report to print
        report_names = self.__model.get_report_names()
        report_id, output_filename = self.__view.print_report(report_names)
        App().log("Printing report: name=" + report_names[(report_id - 1)])

        # Measure time to create and print the report.... record start time
        start_time = time()

        # create the report by creating the base report, and then decorating it
        source_id, title_search_terms, all_search_terms = \
          self.__model.get_report_data(report_id)
        report = ReportBase(source_id)
        if (len(title_search_terms) != 0):
            title_search_terms_list = title_search_terms.split(",")
            for search_term in title_search_terms_list:
                report = ReportTitleSearch(report, source_id, search_term)
        if (len(all_search_terms) != 0):
            all_search_terms_list = all_search_terms.split(",")
            for search_term in all_search_terms_list:
                report = ReportAllSearch(report, source_id, search_term)
        App().log("Base report and decorators created")

        # output the report
        output_file = open(output_filename, "w")
        output_file.write(report.report_text())
        output_file.close()

        # Measure time to create and print the report using the end time
        end_time = time()
        total_time = round(end_time - start_time, 4)
        App().log("Report written to file: " + output_filename)
        App().log("Time to generate report: " + str(total_time) + "s")
        print("Report written to file!")


# Model handles interaction with the database, used by the controller
class Model():

    # Creates an entry in the Redis database for a report, storing the report
    # name, source id and any title/all search terms.  We use this schema for
    # storing data in the database:
    #
    #      key      hash
    #   report1 ->  report_name -> "CNN sports report"
    #               source_id -> "cnn"
    #               title_search_terms = "nba,mlb,nfl,nhl"
    #               all_search_terms = "basketball,raptors,football"
    #
    #  Where we store report data as a hash at keys report1, report2,
    #  reporti, ...
    #
    #  Note that we store the search terms as a comma separated list.  Also
    #  note that we keep track of the number of reports at key report:count.
    #  We use this to determine the next report key to use.
    #
    def create_report(self, report_name, source_id, title_search_terms, \
                      all_search_terms):
        count = App().dbconn.get("report:count")
        if (count == None):
            count = 1
        else:
            count = int(count) + 1
        App().dbconn.set("report:count", count)
        report_key = "report:" + str(count)
        App().dbconn.hset(report_key, "report_name", report_name)
        App().dbconn.hset(report_key, "source_id", source_id)
        App().dbconn.hset(report_key, "title_search_terms", title_search_terms)
        App().dbconn.hset(report_key, "all_search_terms", all_search_terms)
        App().log("Report inserted into database: name=" + report_name)

    # Returns the report names in a list, with the 1,2,3,... order in the list
    # corresponding to the report:1,report:2,report:3,... keys in the database
    def get_report_names(self):
        count = int(App().dbconn.get("report:count"))
        i = 1
        report_names = []
        while i <= count:
            report_name = App().dbconn.hget("report:" + str(i), "report_name")
            report_names.append( report_name )
            i = i + 1
        App().log("Report names retrieved: " + str(report_names))
        return report_names

    # Returns the source id, title search terms and all search terms for the
    # report stored at the key "report:report_id" in the database
    def get_report_data(self,report_id):
        report_key = "report:" + str(report_id)
        source_id = App().dbconn.hget(report_key, "source_id")
        title_search_terms = App().dbconn.hget(report_key, "title_search_terms")
        all_search_terms = App().dbconn.hget(report_key, "all_search_terms")
        App().log("Retrieved report data for report id: " + str(report_id))
        return source_id, title_search_terms, all_search_terms
