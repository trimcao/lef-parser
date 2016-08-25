"""
Lef Parser
Author: Tri Cao
Email: tricao@utdallas.edu
Date: August 2016
"""
from lef_util import *
from util import *

SCALE = 2000

class LefParser:
    """
    LefParser object will parse the LEF file and store information about the
    cell library.
    """
    def __init__(self, lef_file):
        self.lef_path = lef_file
        # dictionaries to map the definitions
        self.macro_dict = {}
        # can make the stack to be an object if needed
        self.stack = []
        # store the statements info in a list
        self.statements = []

    def parse(self):
        # Now try using my data structure to parse
        # open the file and start reading
        f = open(self.lef_path, "r+")
        # the program will run until the end of file f
        for line in f:
            info = str_to_list(line)
            if len(info) != 0:
                # if info is a blank line, then move to next line
                # check if the program is processing a statement
                if len(self.stack) != 0:
                    curState = self.stack[len(self.stack) - 1]
                    nextState = curState.parse_next(info)
                else:
                    curState = Statement()
                    nextState = curState.parse_next(info)
                # check the status return from parse_next function
                if nextState == 0:
                    # continue as normal
                    pass
                elif nextState == 1:
                    # remove the done statement from stack, and add it to the statements
                    # list
                    if len(self.stack) != 0:
                        # add the done statement to a dictionary
                        done_obj = self.stack.pop()
                        if isinstance(done_obj, Macro):
                            self.macro_dict[done_obj.name] = done_obj
                        self.statements.append(done_obj)
                elif nextState == -1:
                    pass
                else:
                    self.stack.append(nextState)
                    # print (nextState)
        f.close()



# Main Class
if __name__ == '__main__':
    path = "./libraries/FreePDK45/FreePDK45nm.lef"
    lef_parser = LefParser(path)
    lef_parser.parse()

    to_draw = []
    to_draw.append(input("Enter the first macro: "))
    to_draw.append(input("Enter the second macro: "))
    #to_draw = ["AND2X1", "AND2X2"]


    plt.figure(figsize=(12, 9), dpi=80)
    plt.axes()

    num_plot = 1
    for macro_name in to_draw:
        # check user's input
        if macro_name not in lef_parser.macro_dict:
            print ("Error: This macro does not exist in the parsed library.")
            quit()
        macro = lef_parser.macro_dict[macro_name]
        sub = plt.subplot(1, 2, num_plot)
        # need to add title
        sub.set_title(macro.name)
        draw_macro(macro)
        num_plot += 1
        # scale the axis of the subplot
        plt.axis('scaled')


    # start drawing
    print ("Start drawing...")
    plt.show()

    #print (macro_dict)
    #print (len(macro_dict))
