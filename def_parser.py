"""
DEF Parser
Author: Tri Minh Cao
Email: tricao@utdallas.edu
Date: August 2016
"""

from def_util import *
from util import *
# can make the stack to be an object if needed
stack = []

# store the statements info in a list
sections = []

# dictionaries for mapping

def split_plus(line):
    """
    Split a line according to the + (plus) sign.
    :param line:
    :return:
    """
    new_line = line.split("+")
    return new_line

def split_space(line: object) -> object:
    """
    Split a line according to space.
    :param line:
    :return:
    """
    new_line = line.split()
    return new_line

# open the file and start reading
path = "./libraries/DEF/nets.def"
f = open(path, "r+")
# the program will run until the end of file f
for line in f:
    parts = split_plus(line)
    for each_part in parts:
        info = split_space(each_part)
        if len(info) > 0:
            #print (info)
            #print (split_parentheses(info))
            #print ()
            if info[0] == "PINS":
                new_pins = Pins(int(info[1]))
                stack.append(new_pins)
                #print (new_pins.type)
            elif info[0] == "COMPONENTS":
                new_comps = Components(int(info[1]))
                stack.append(new_comps)
            elif info[0] == "NETS":
                new_nets = Nets(int(info[1]))
                stack.append(new_nets)
            elif info[0] == "END":
                sections.append(stack.pop())
                #print ("finish")
            else:
                if len(stack) > 0:
                    latest_obj = stack[-1]
                    latest_obj.parse_next(info)

# print out results
#comps = sections[0]
#pins = sections[1]
#for comp in comps.comps:
#    print (comp)
#for pin in pins.pins:
#    print (pin)

nets = sections[0]
for net in nets.nets:
    print (net)
