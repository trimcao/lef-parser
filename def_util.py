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
        if info[0] == "-":
            # create a new pin
            # print (info[1])
            current_pin = Pin(info[1])
            self.pins.append(current_pin)
            # print ("new")
        else:
            current_pin = self.get_last_pin()
            # print ("last")
            # parse the next info
            if info[0] == "NET":
                current_pin.net = info[1]
            elif info[0] == "DIRECTION":
                current_pin.direction = info[1]
            elif info[0] == "USE":
                current_pin.use = info[1]
            elif info[0] == "LAYER":
                new_layer = Layer(info[1])
                new_layer.points.append([int(info[3]), int(info[4])])
                new_layer.points.append([int(info[7]), int(info[8])])
                current_pin.layer = new_layer
            elif info[0] == "PLACED":
                current_pin.placed = [info[2], info[3]]
                current_pin.orient = info[5]

    def get_last_pin(self):
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

    def __init__(self, num_comps):
        self.type = "COMPONENTS_DEF"
        self.num_comps = num_comps
        self.comps = []

    def parse_next(self, info):
        if info[0] == "-":
            new_comp = Component(info[1])
            new_comp.macro = info[2]
            self.comps.append(new_comp)
        else:
            current_comp = self.get_last_comp()
            # parse the next info
            if info[0] == "PLACED":
                current_comp.placed = [int(info[2]), int(info[3])]
                current_comp.orient = info[5]

    def get_last_comp(self):
        return self.comps[-1]


class Component:
    """
    Represents individual component inside the COMPONENTS section in the DEF
    file.
    """

    def __init__(self, name):
        self.type = "COMPONENT_DEF"
        self.name = name
        self.macro = None
        self.placed = None
        self.orient = None

    def __str__(self):
        s = ""
        s += self.type + ": " + self.name + "\n"
        s += "    " + "Macro: " + self.macro + "\n"
        s += "    " + "Placed: " + str(self.placed) + " " + self.orient + "\n"
        return s


class Nets:
    """
    Represents the section NETS in the DEF file.
    """

    def __init__(self, num_nets):
        self.type = "NETS_DEF"
        self.num_nets = num_nets
        self.nets = []

    def parse_next(self, info):
        # remember to check for "(" before using split_parentheses
        # if we see "(", then it means new component or new pin
        # another method is to check the type of the object, if it is a list
        # then we know it comes from parentheses
        if info[0] == "-":
            new_net = Net(info[1])
            self.nets.append(new_net)
        else:
            current_net = self.get_last_net()
            # parse next info
            if isinstance(info[0], list):
                for comp in info:
                    current_net.comp_pin.append(comp)
            elif info[0] == "ROUTED" or info[0] == "NEW":
                new_routed = Routed()
                new_routed.layer = info[1]
                # add points to the new_routed
                for idx in range(2, len(info)):
                    if isinstance(info[idx], list):
                        # this is a point
                        parsed_pt = info[idx]
                        new_pt = []
                        for j in range(len(parsed_pt)):
                            # if we see "*", the new coordinate comes from last
                            #  point's coordinate
                            if parsed_pt[j] == "*":
                                last_pt = new_routed.get_last_pt()
                                new_coor = last_pt[j]
                                new_pt.append(new_coor)
                            else:
                                new_pt.append(int(parsed_pt[j]))
                        # add new_pt to the new_routed
                        new_routed.points.append(new_pt)
                    else:
                        # this should be via end point
                        new_routed.end_via = info[idx]
                # add new_routed to the current_net
                current_net.routed.append(new_routed)

    def get_last_net(self):
        return self.nets[-1]


class Net:
    """
    Represents individual Net inside NETS section.
    """

    def __init__(self, name):
        self.type = "NET_DEF"
        self.name = name
        self.comp_pin = []
        self.routed = []

class Routed:
    """
    Represents a ROUTED definition inside a NET.
    """

    def __init__(self):
        self.type = "ROUTED_DEF"
        self.layer = None
        self.points = []
        self.end_via = None

    def get_last_pt(self):
        return self.points[-1]

