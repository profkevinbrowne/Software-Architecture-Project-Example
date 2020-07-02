################################################################################
# Report generation using the Decorator pattern
#
# Purpose: The classes in this module allow for reports to be generated.  The
# Decorator pattern is used: https://en.wikipedia.org/wiki/Decorator_pattern.
# The Report class defines the Component, the ReportBase class defines the
# ConcreteComponent that will be decorated (by default, all reports include
# the headlines from the associated source), ReportExtension defines the
# Decorator class, and ReportTitleSearch/ReportAllSearch define the
# ConcreteDecorator classes that "decorate" the report with additional
# information (results for searching for articles with a given term in the
# title of the articles, or in the entire article).
#
# We use the News API to access news data and produce news reports:
# - https://github.com/mattlisiv/newsapi-python
# - https://newsapi.org/docs
#
# Author: Kevin Browne
# Contact: brownek@mcmaster.ca
#
################################################################################

from app import *

# Defines what it means to be a report... must have a report_text method.  This
# is the "Component" in the Decorator pattern.
class Report(ABC):

    @abstractmethod
    def report_text(self):
        pass

# The base report will be a string of the top headlines for the given source.
# This corresponds to the ConcreteComponent of the Decorator pattern, it can
# optionally be decorated to extend the report contents.
class ReportBase(Report):

    # Calls News API to get top headlines, puts headline data into a string
    def report_text(self):
        App().log("Building report base, source id= " + self.__source_id)
        headlines = App().newsapi.get_top_headlines(sources=self.__source_id)
        report_text = "Headlines from " + self.__source_id + "\n\n"
        for article in headlines["articles"]:
            report_text = report_text + \
                          "Title: " + str(article["title"]) + "\n" + \
                          "Description: " + str(article["description"]) + "\n\n"
        return report_text

    def __init__(self,source_id):
        self.__source_id = source_id

# Extensions to the report will involve a search term, this defines what it
# means to be an extension.  This class corresponds to the Decorator class in
# the Decorator pattern.
class ReportExtension(Report):

    def __init__(self,report,source_id,search_term):
        self.report = report
        self.source_id = source_id
        self.search_term = search_term

# This class decorates the report with data retrieved from the News API
# for any article with a title containing the search term.  It corresponds to
# the ConcreteDecorator class in the Decorator pattern.
class ReportTitleSearch(ReportExtension):

    # Calls News API to get search results, puts result data into a string
    def report_text(self):
        App().log("Building report title search, term= " + self.search_term)
        report_text = self.report.report_text()
        headlines = App().newsapi.get_everything(sources=self.source_id,
                                                 qintitle=self.search_term)
        report_text = report_text + "****************************************"
        report_text = report_text + "\n\nSearch results for '" + \
                      self.search_term + "' in the title only: \n\n"
        for article in headlines["articles"]:
            report_text = report_text + \
                          "Title: " + str(article["title"]) + "\n" + \
                          "Author: " + str(article["author"]) + "\n\n"
        return report_text


# This class decorates the report with data retrieved from the News API
# for any article with a title OR body containing the search term.  It
# corresponds to the ConcreteDecorator class in the Decorator pattern.
class ReportAllSearch(ReportExtension):

    # Calls News API to get search results, puts result data into a string
    def report_text(self):
        App().log("Building report all search, term=" + self.search_term)
        report_text = self.report.report_text()
        headlines = App().newsapi.get_everything(sources=self.source_id,
                                                 q=self.search_term)
        report_text = report_text + "****************************************"
        report_text = report_text + "\n\nSearch results for '" + \
                      self.search_term + "' in the title or content: \n\n"
        for article in headlines["articles"]:
            report_text = report_text + \
                          "Title: " + str(article["title"]) + "\n" + \
                          "Content: " + str(article["content"]) + "\n\n"
        return report_text
