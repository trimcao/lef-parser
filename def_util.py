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
            #print (info[1])
            current_pin = Pin(info[1])
            self.pins.append(current_pin)
            #print ("new")
        else:
            current_pin = self.getLastPin()
            #print ("last")
            # parse the next info
            if (info[0] == "NET"):
                current_pin.net = info[1]
            elif (info[0] == "DIRECTION"):
                current_pin.direction = info[1]
            elif (info[0] == "USE"):
                current_pin.use = info[1]
            elif (info[0] == "LAYER"):
                new_layer = Layer(info[1])
                new_layer.points.append([int(info[3]), int(info[4])])
                new_layer.points.append([int(info[7]), int(info[8])])
                current_pin.layer = new_layer
            elif (info[0] == "PLACED"):
                current_pin.placed = [info[2], info[3]]
                current_pin.orient = info[5]

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
    def __str__(self):
        s = ""
        s += self.type + ": " + self.name + "\n"
        s += "    " + "Name: " + self.net + "\n"
        s += "    " + "Direction: " + self.direction + "\n"
        s += "    " + "Use: " + self.use + "\n"
        s += "    " + "Layer: " + str(self.layer) + "\n"
        s += "    " + "Placed: " + str(self.placed) + " " + self.orient + "\n"
        return s

class Layer:
    """
    Class Layer represents a layer defined inside a PIN object
    """
    def __init__(self, name):
        self.type = "LAYER_DEF"
        self.name = name
        self.points = []

    def __str__(self):
        s = ""
        s += self.name
        for pt in self.points:
            s += " " + str(pt)
        return s


class Components:
    """
    Class Components represents the COMPONENTS section in the DEF file.
    """
    def __init__(self):

