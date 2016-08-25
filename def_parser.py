"""
DEF Parser
Author: Tri Minh Cao
Email: tricao@utdallas.edu
Date: August 2016
"""

from def_util import *
from util import *


class DefParser:
    """
    DefParser will parse a DEF file and store related information of the design.
    """

    def __init__(self, def_file):
        self.file_path = def_file
        # can make the stack to be an object if needed
        self.stack = []
        # store the statements info in a list
        self.sections = []

    def parse(self):
        """
        Main method to parse the DEF file
        :return: void
        """
        # open the file and start reading
        f = open(self.file_path, "r+")
        # the program will run until the end of file f
        for line in f:
            parts = split_plus(line)
            for each_part in parts:
                info = split_space(each_part)
                if len(info) > 0:
                    #print (info)
                    # print (split_parentheses(info))
                    # print ()
                    if info[0] == "PINS":
                        new_pins = Pins(int(info[1]))
                        self.stack.append(new_pins)
                        # print (new_pins.type)
                    elif info[0] == "COMPONENTS":
                        new_comps = Components(int(info[1]))
                        self.stack.append(new_comps)
                    elif info[0] == "NETS":
                        new_nets = Nets(int(info[1]))
                        self.stack.append(new_nets)
                    elif info[0] == "END":
                        if len(self.stack) > 0:
                            self.sections.append(self.stack.pop())
                        # print ("finish")
                    else:
                        if len(self.stack) > 0:
                            latest_obj = self.stack[-1]
                            latest_obj.parse_next(info)
        f.close()

    def write_def(self, new_def, back_end=True, front_end=True):
        """
        Write a new def file based on the information in the DefParser object.
        Note: this method writes all information
        :param new_def: path of the new DEF file
        :param back_end: write BEOL information or not.
        :param front_end: write FEOL info or not.
        :return: void
        """
        f = open(new_def, mode="w+")
        #f.write("Ten toi la Nam Thui.\n")
        # first, write the COMPONENTS section
        comps = self.sections[0]
        # check if parsing has been done
        if comps.type != "COMPONENTS_DEF":
            return
        print("Writing COMPONENTS...")
        self.write_components(f, comps)
        f.close()

    def write_components(self, current_file, comps):
        """
        Method to write COMPONENTS section of the DEF.
        :param comps: Components object
        :return: void
        """
        current_file.write("COMPONENTS" + " " + str(comps.num_comps) + " ;\n")
        for each_comp in comps.comps:
            current_file.write(each_comp.to_def_format())
            current_file.write("\n")
        current_file.write("END COMPONENTS")



# Main Class
if __name__ == '__main__':
    read_path = "./libraries/DEF/c880_tri.def"
    def_parser = DefParser(read_path)
    def_parser.parse()
    write_path = "./def_write/test_comps.def"
    def_parser.write_def(write_path)

    ## print out results
    # comps = def_parser.sections[0]
    # pins = def_parser.sections[1]
    # nets = def_parser.sections[2]
    ##print (comps.comp_dict["U132"])
    ##print (pins.pin_dict["N30"])
    ##print (nets.net_dict["N146"])
    # for comp in comps.comps:
    #    print (comp)
    # for pin in pins.pins:
    #    print (pin)
    # for net in nets.nets:
    #    print (net)
