"""
Data structures for DEF Parser
Author: Tri Minh Cao
Email: tricao@utdallas.edu
Date: August 2016
"""

class Pins:
    """
    Class Pins represents the PINS section in DEF file. It contains
    individual Pin objects.
    """
    def __init__(self):
        self.type = "PINS_DEF"
        self.pins[]

    def parseNext(self, data):
        pass

class Pin:
    """
    Class Pin represents an individual pin defined in the DEF file.
    """
    def __init__(self, name):
        self.type = "PIN_DEF"
        self.name = name
        self.net = None
        self.direction = None
        self.use = None
        self.layer = None
        self.placed = None
        self.orient = None

    # add methods to add information to the Pin object
