"""
Data Structures for LEF Parser
Author: Tri Minh Cao
Email: tricao@utdallas.edu
Date: August 2016
"""

class Statement:
    """
    General class for all types of Statements in the LEF file
    """
    def __init__(self):
        pass

    def parseNext(self, data):
        """
        Method to add information from a statement from LEF file to the
        dictionary.
        :param data: a list of strings that contains pieces of information
        :return: 1 if everything is good, -1 if error, otherwise, return the
        object that will be parsed next.
        """
        print ("You are a piece of shite")
        return 1

class Macro(Statement):
    """
    Macro class to represent the a MACRO (cell) in the LEF file.
    """
    def __init__(self, name):
        # initiate the Statement superclass
        Statement.__init__(self)
        self.type = 'MACRO'
        self.name = name

