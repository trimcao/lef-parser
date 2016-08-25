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
        self.tracks = []
        self.gcellgrids = []
        self.rows = []
        self.diearea = None
        self.version = None
        self.dividerchar = None
        self.busbitchars = None
        self.design_name = None
        self.units = None
        self.scale = None

    def parse(self):
        """
        Main method to parse the DEF file
        :return: void
        """
        # open the file and start reading
        f = open(self.file_path, "r+")
        # the program will run until the end of file f
        for line in f:
            # split the string by the plus '+' sign
            parts = split_plus(line)
            for each_part in parts:
                # split each sub-string by space
                info = split_space(each_part)
                if len(info) > 0:
                    #print info
                    if info[0] == "PINS":
                        new_pins = Pins(int(info[1]))
                        self.stack.append(new_pins)
                        # print (new_pins.type)
                    elif info[0] == "VERSION":
                        self.version = info[1]
                    elif info[0] == "DIVIDERCHAR":
                        self.dividerchar = info[1]
                    elif info[0] == "BUSBITCHARS":
                        self.busbitchars = info[1]
                    elif info[0] == "DESIGN" and len(info) <= 2:
                        # differentiate with the DESIGN statement inside
                        # PROPERTYDEFINITIONS section.
                        self.design_name = info[1]
                    elif info[0] == "UNITS":
                        self.units = info[2]
                        self.scale = info[3]
                    elif info[0] == "PROPERTYDEFINITIONS":
                        new_property = Property()
                        self.stack.append(new_property)
                    elif info[0] == "DIEAREA":
                        info = split_parentheses(info)
                        pt1 = (int(info[1][0]), int(info[1][1]))
                        pt2 = (int(info[2][0]), int(info[2][1]))
                        self.diearea = [pt1, pt2]
                    elif info[0] == "COMPONENTS":
                        new_comps = Components(int(info[1]))
                        self.stack.append(new_comps)
                    elif info[0] == "NETS":
                        new_nets = Nets(int(info[1]))
                        self.stack.append(new_nets)
                    elif info[0] == "TRACKS":
                        new_tracks = Tracks(info[1])
                        new_tracks.pos = int(info[2])
                        new_tracks.do = int(info[4])
                        new_tracks.step = int(info[6])
                        new_tracks.layer = info[8]
                        self.tracks.append(new_tracks)
                    elif info[0] == "GCELLGRID":
                        new_gcellgrid = GCellGrid(info[1])
                        new_gcellgrid.pos = int(info[2])
                        new_gcellgrid.do = int(info[4])
                        new_gcellgrid.step = int(info[6])
                        self.gcellgrids.append(new_gcellgrid)
                    elif info[0] == "ROW":
                        new_row = Row(info[1])
                        new_row.site = info[2]
                        new_row.pos = (int(info[3]), int(info[4]))
                        new_row.orient = info[5]
                        new_row.do = int(info[7])
                        new_row.by = int(info[9])
                        new_row.step = (int(info[11]), int(info[12]))
                        self.rows.append(new_row)
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
        # first, write the COMPONENTS section
        comps = self.sections[1]
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
    # write to a new DEF file
    #write_path = "./def_write/test_comps.def"
    #def_parser.write_def(write_path)

    # try printing track
    #for track in def_parser.tracks:
    #    print (track.to_def_format())

    # try printing GCellGrid
    #for gcell in def_parser.gcellgrids:
    #    print(gcell.to_def_format())

    # try printing Row
    #for row in def_parser.rows:
    #    print (row.to_def_format())

    # try printing PROPERTYDEFINITIONS
    #props = def_parser.sections[0]
    #print (props.to_def_format())

    # print out results
    #comps = def_parser.sections[1]
    #print (comps.to_def_format())
    pins = def_parser.sections[2]
    print (pins.to_def_format())
    #nets = def_parser.sections[3]
