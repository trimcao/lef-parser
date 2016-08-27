"""
DEF Splitter for Split Manufacturing
Author: Tri Minh Cao
Email: tricao@utdallas.edu
Date: August 2016
"""
from def_parser import *
from lef_parser import *

# names of back-end and front-end layers
BEOL = {"metal1"}
FEOL = {"metal2", "metal3", "metal4", "metal5", "metal6", "metal7", "metal8",
        "metal9", "metal10"}

def proper_layers(back_end, front_end):
    if back_end == False and front_end == False:
        pass
    elif back_end == True and front_end == False:
        return BEOL
    elif back_end == False and front_end == True:
        return FEOL
    else:
        return BEOL | FEOL

# outside function needed to output the NETS data selectively, because
# possibly we need to check LEF data and that requires bigger scope.
def output_nets(self, def_info, lef_info, back_end=True, front_end=True):
    """
    Output the NETS section information with possible back end and front
    end selections.
    :param def_info: a DefParser object that contains DEF info.
    :param lef_info: a LefParser object
    :param back_end: whether to write BEOL info or not.
    :param front_end: whether to write FEOL info or not.
    :return: string
    """
    s = ""


def output_net(self, def_info, lef_info, back_end=True, front_end=True):
    """
    Output a Net object inside the NETS section information with possible back
    end and front end selections.
    :param def_info: a DefParser object that contains DEF info.
    :param lef_info: a LefParser object
    :param back_end: whether to write BEOL info or not.
    :param front_end: whether to write FEOL info or not.
    :return: string
    """
    # need to know what layers are good for the current back-end and
    # front-end settings
    good_layers = proper_layers(back_end, front_end)
    # start setting up the string
    s = ""
    s += "- " + self.name + "\n"
    s += " "
    for each_comp in self.comp_pin:
        # study each comp/pin
        # if it's a pin, check the Pin object layer (already parsed)
        if each_comp[0] == "PIN":
            pin_name = each_comp[1]
            if def_info.pins.get_pin(pin_name).get_layer().name in good_layers:
                s += " ( " + " ".join(each_comp) + " )"
        else:
            # for component, need to check LEF info
            comp_id = each_comp[0]
            pin_name = each_comp[1]
            comp = def_info.components.get_comp(comp_id).get_macro()
            print (comp)
            comp_info = lef_info
            # right now, assume all components are in metal1
            s += " ( " + " ".join(each_comp) + " )"
    #s += "\n  + ROUTED " + self.routed[0].to_def_format() + "\n"
    #for i in range(1, len(self.routed)):
    #    s += "    " + "NEW " + self.routed[i].to_def_format() + "\n"
    #s += " ;"
    return s

# Main Class
if __name__ == '__main__':
    lef_file = "./libraries/Nangate/NangateOpenCellLibrary.lef"
    lef_parser = LefParser(lef_file)
    lef_parser.parse()

    print (lef_parser.macro_dict["AND2_X1"])
    print ()
    print (lef_parser.macro_dict["NAND2_X1"])
    print ()
    print (lef_parser.macro_dict["INV_X1"])
    print ()

    #def_file = "./libraries/DEF/c880_tri.def"
    #def_parser = DefParser(def_file)
    #def_parser.parse()

    #nets = def_parser.nets
    #print (nets.nets[1].to_def_format())
    #print
    #s = output_net(nets.nets[1], def_info=def_parser, lef_info=None,
    #               back_end=True, front_end=False)
    #print (s)
