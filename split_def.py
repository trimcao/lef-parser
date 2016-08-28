"""
DEF Splitter for Split Manufacturing
Author: Tri Minh Cao
Email: tricao@utdallas.edu
Date: August 2016
"""
from def_parser import *
from lef_parser import *

def proper_layers(back_end, front_end):
    if back_end == False and front_end == False:
        pass
    elif back_end == True and front_end == False:
        return BEOL
    elif back_end == False and front_end == True:
        return FEOL
    else:
        return BEOL | FEOL

# names of back-end and front-end layers
BEOL = {"metal1"}
FEOL = {"metal2", "metal3", "metal4", "metal5", "metal6", "metal7", "metal8",
        "metal9", "metal10"}

SPLIT_LAYER = "metal2"


# outside function needed to output the NETS data selectively, because
# possibly we need to check LEF data and that requires bigger scope.
def output_nets(nets, def_info, lef_info):
    """
    Output the NETS section information with possible back end and front
    end selections.
    :param def_info: a DefParser object that contains DEF info.
    :param lef_info: a LefParser object
    :return: string
    """
    s = ""
    # add each net's data to nets_str
    nets_str = ""
    num_nets = 0
    for net in nets.nets:
        net_data = output_net(net, def_info, lef_info)
        if net_data != "":
            nets_str += net_data
            nets_str += "\n"
            num_nets += 1
    if num_nets > 0:
        s += "NETS " + str(num_nets) + " ;\n"
        s += nets_str
        s += "END NETS"
    return s


def output_net_routes(net, def_info, lef_info):
    """
    Return None if there are no routes in the
    :param net: a Net object
    :param def_info: a DefParser object that contains DEF info.
    :param lef_info: a LefParser object
    :return: routes if good route exists, None if no route available.
    """
    s = ""
    # output routes
    num_route = 0
    first_route_done = False
    for i in range(len(net.routed)):
        if net.routed[i].get_layer() in GOOD_LAYERS:
            num_route += 1
            if first_route_done:
                s += "    " + "NEW " + net.routed[i].to_def_format() + "\n"
            else:
                s += "  + ROUTED " + net.routed[i].to_def_format() + "\n"
                first_route_done = True
    if num_route == 0:
        return "no route"
    else:
        return s

def output_net(net, def_info, lef_info):
    """
    Output a Net object inside the NETS section information with possible back
    end and front end selections.
    :param def_info: a DefParser object that contains DEF info.
    :param lef_info: a LefParser object
    :return: string
    """
    # check number of routes and get the routes
    routes = output_net_routes(net, def_info, lef_info)
    if routes == "no route":
        return ""
    # start setting up the string
    s = ""
    s += "- " + net.name + "\n"
    s += " "
    for each_comp in net.comp_pin:
        # study each comp/pin
        # if it's a pin, check the Pin object layer (already parsed)
        if each_comp[0] == "PIN":
            pin_name = each_comp[1]
            if def_info.pins.get_pin(pin_name).get_metal_layer() in GOOD_LAYERS:
                s += " ( " + " ".join(each_comp) + " )"
        else:
            # for component, need to check LEF info
            comp_id = each_comp[0]
            pin_name = each_comp[1]
            comp = def_info.components.get_comp(comp_id).get_macro()
            #print (comp)
            # get info from LEF Parser
            comp_info = lef_info.macro_dict[comp]
            # get pin layer info
            pin_info = comp_info.pin_dict[pin_name]
            if pin_info.get_top_metal() in GOOD_LAYERS:
                s += " ( " + " ".join(each_comp) + " )"
    # output routes
    s += "\n"
    s += routes
    s += " ;"
    return s

def output_comps(comps):
    """
    Method to write/output a component to the DEF file
    :param comp: component to be written
    :param def_info: DEF file data
    :param lef_info: LEF file data
    :return: a string that contains Components section in DEF format.
    """
    # assume all components are in bottom layers
    if "metal1" in GOOD_LAYERS:
        return comps.to_def_format()
    else:
        return ""

def output_pin(pin, def_info):
    """
    Method to write/output a pin to the DEF file
    :param pin: Pin object
    :param def_info: DEF data
    :return: a string that contains a Pin in DEF format.
    """
    #print (pin.get_layer())
    if pin.get_metal_layer() in GOOD_LAYERS:
        return pin.to_def_format()
    else:
        return ""

def output_pins(pins, def_info):
    """
    Method to write/output the PINS section to the DEF file.
    :param pins: Pin object
    :param def_info: DEF data
    :return: a tring that contains the PINS section in DEF format
    """
    s = ""
    num_pins = 0
    pins_string = ""
    for each_pin in pins.pins:
        pin_data = output_pin(each_pin, def_info)
        if pin_data != "":
            pins_string += pin_data
            pins_string += "\n"
            num_pins += 1
    # only write PINS section when we have > 0 pins
    if num_pins > 0:
        s = "PINS " + str(num_pins) + " ;\n"
        s += pins_string
        s += "END PINS"
    return s

def output_tracks(def_info):
    """
    Method to write/output TRACKS to DEF file.
    :param def_info: DEF data
    :return: a string that contains TRACKS info in DEF format.
    """
    s = ""
    for track in def_info.tracks:
        if track.get_layer() in GOOD_LAYERS:
            s += track.to_def_format()
            s += "\n"
    return s

# Main Class
if __name__ == '__main__':

    # user will choose whether to keep back_end and/or front_end
    BACK_END = True
    FRONT_END = False

    # need to know what layers are good for the current back-end and
    # front-end settings
    GOOD_LAYERS = proper_layers(BACK_END, FRONT_END)

    lef_file = "./libraries/Nangate/NangateOpenCellLibrary.lef"
    lef_parser = LefParser(lef_file)
    lef_parser.parse()

    #print (lef_parser.macro_dict["AND2_X1"])
    #print ()
    #print (lef_parser.macro_dict["NAND2_X1"])
    #print ()
    #for pin in lef_parser.macro_dict["INV_X1"].pin_dict.values():
    #    print (pin.name)
    #    print (pin.is_lower_metal("metal2"))
    #    print

    def_file = "./libraries/DEF/c880_tri.def"
    def_parser = DefParser(def_file)
    def_parser.parse()

    #nets = def_parser.nets
    #chosen_net = nets.net_dict["N51"]
    #print (chosen_net.to_def_format())
    #print
    #for net in nets.nets:
    #    s = output_net(net, def_info=def_parser, lef_info=lef_parser)
    #    if s != "":
    #        print (s)

    #print (output_pins(def_parser.pins, def_parser))
    #print (output_tracks(def_parser))
    #print (output_nets(def_parser.nets, def_parser, lef_parser))
