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
        Statement object.
        :param data: a list of strings that contains pieces of information
        :return: 1 if parsing is done, -1 if error, otherwise, return the
        object that will be parsed next.
        """
        # right now, the program assumes the syntax of LEF file is correct
        if data[0] == "MACRO":
            name = data[1]
            newState = Macro(name)
            return newState
        elif data[0] == "END":
            return 1
        return 0

    def toString(self):
        """
        turn a statement object into string
        :return: string representation of Statement objects
        """
        s = ""
        s += self.type + " " + self.name + "\n"
        for key in self.info:
            s += "    " + key + ": " + str(self.info[key]) + "\n"
        return s

class Macro(Statement):
    """
    Macro class represents a MACRO (cell) in the LEF file.
    """
    def __init__(self, name):
        # initiate the Statement superclass
        Statement.__init__(self)
        self.type = 'MACRO'
        self.name = name
        # other info is stored in this dictionary
        self.info = {}

    def parseNext(self, data):
        """
        Method to add information from a statement from LEF file to a Macro
        object.
        :param data: a list of strings that contains pieces of information
        :return: 0 if in progress, 1 if parsing is done, -1 if error,
        otherwise, return the
        object that will be parsed next.
        """
        if data[0] == "CLASS":
            self.info["CLASS"] = data[1]
        elif data[0] == "ORIGIN":
            xCor = float(data[1])
            yCor = float(data[2])
            self.info["ORIGIN"] = (xCor, yCor)
        elif data[0] == "SIZE":
            width = float(data[1])
            height = float(data[3])
            self.info["SIZE"] = (width, height)
        elif data[0] == "SITE":
            self.info["SITE"] = data[1]
        elif data[0] == "OBS":
            newObs = Obs()
            self.info["OBS"] = newObs
            return newObs
        elif data[0] == "END":
            if data[1] == self.name:
                return 1
            else:
                return -1
        return 0

    # eventually I will override the toString() method
    #def toString(self):


class Obs(Statement):
    """
    Class Obs represents an OBS statement in the LEF file.
    """
    # Note: OBS statement does not have name
    def __init__(self):
        Statement.__init__(self)
        self.type = "OBS"
        self.name = ""
        self.info = {}

    def parseNext(self, data):
        if data[0] == "END":
            return 1
        elif data[0] == "LAYER":
            name = data[1]
            newLayerDef = LayerDef(data[1])
            self.info["LAYER"] = newLayerDef
        elif data[0] == "RECT":
            # error if the self.info["LAYER"] does not exist
            self.info["LAYER"].addRect(data)
        return 0

class LayerDef():
    """
    Class LayerDef represents the Layer definition inside a PORT or OBS
    statement.
    """
    # NOTE: LayerDef has no END statement
    # I think I still need a LayerDef class, but it will not be a subclass of
    #  Statement. It will be a normal object that stores information.
    def __init__(self, name):
        self.type = "LayerDef"
        self.name = name
        self.shapes = []

    def addRect(self, data):
        x0 = data[1]
        y0 = data[2]
        x1 = data[3]
        y1 = data[4]
        points = [(x0, y0), (x1, y1)]
        rect = Rect(points)
        self.shapes.append(rect)

class Rect():
    """
    Class Rect represents a Rect definition in a LayerDef
    """
    # Question: Do I really need a Rect class?
    def __init__(self, points):
        self.points = points



