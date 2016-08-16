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
    def __init__(self, num_pins):
        self.type = "PINS_DEF"
        self.num_pins = num_pins
        self.pins = []

    def parse_next(self, info):
        if (info[0] == "-"):
            # create a new pin
            current_pin = Pin([info[1]])
            self.pins.append(current_pin)
            print ("new")
        else:
            current_pin = self.getLastPin()
            print ("last")

    def getLastPin(self):
        return self.pins[-1]

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
