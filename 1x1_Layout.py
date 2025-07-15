###Layout for a 1 x 1 cm2 chip

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from importlib import resources as impresources

import gdstk

from NDL.devices import FeCAP, FeFET, HallBar, profiles, metal_lines ##################
from NDL.devices.FeCAP import FeCAP_test_str, FeCAP_small ################## , FeCAP_design4, FeCAP_design6
from NDL.devices.HallBar import HallBar_design4, HallBar_design6 ##################
from NDL.devices.FeFET import FeFET_design4, FeFET_design6 ##################
from NDL.devices.profiles import profiles
from NDL.devices.metal_lines import MetalLine
from NDL.format_odrso import Formatter
from NDL.array import make_rc_array, make_multiparam_array
from NDL.merge import get_children

from NDL import merge
from NDL import templates

layer_map = {
    "MET_CH_1":     Formatter(1, 0, 1, 0, 0),
    "MET_SD_2":     Formatter(2, 0, 1, 0, 0),
    "MET_TE_3":     Formatter(3, 0, 1, 0, 0),
    "VIA_CL_4":     Formatter(4, 0, 1, 0, 0),
    "VIA_SDG_5":    Formatter(5, 0, 1, 0, 0),
    "MET_M1_6":     Formatter(6, 0, 1, 0, 0),
    "info":         Formatter(29, 99, 1, 0, 0),
    "labels":       Formatter(30, 99, 1, 0, 0)   
}




lib = gdstk.Library()
top = lib.new_cell("TOP")

# count device IDs
id_count = 0

######## FeCAP array ########

# Initialize device structure
TestStr = FeCAP.FeCAP_test_str(layer_map) 

# Sweep over mesa_size and arrange devices in an array
array_TestStr, children_TestStr = make_rc_array(
    TestStr,    
    [120, 100.0, 80.0, 60.0, 40.0, 20.0], # mesa sizes in um
    repeat_para=3, #repetitions per parameter
    repeat_perp=6, # number of devices per column
    label_schema = "{x:02d}",
    label_fmt = {
        "size": 65,
        "vertical": False,
        "rotation": 90,
    },
    count_0 = id_count,
    )

id_count += len(array_TestStr.references)

# Add child cells to the library
names = [cell.name for cell in lib.cells]
for cell in children_TestStr:
    if cell.name not in names:
        lib.add(cell)

# Add array to top-level layout        
top.add(gdstk.Reference(array_TestStr, (2600, 3125)))




# --------------FeFET Arrays--------------
fefet_6 = FeFET.FeFET_design6(layer_map)
fefet_4 = FeFET.FeFET_design4(layer_map)

channel_x = [6.0]
channel_y = [7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0]

# -------------- FeFET_design4 --------------
array_fefet_4, children_4 = make_multiparam_array(
    generating_class=fefet_4,
    parameters=[channel_x, channel_y],
    label_schema="{x:03d}",
    axis=1,       # rows: channel_x, cols: repetitions
    repeat_perp=26,
    meta_rc=1,
    label_fmt = {
        "size": 50,
        "vertical": False,
        "rotation": 90,
    },
    count_0 = id_count,
)

id_count += len(array_fefet_4.references)

lib.add(*children_4)
top.add(gdstk.Reference(array_fefet_4, (-2600, 1250)))


# -------------- FeFET_design6 --------------
array_fefet_6, children_6 = make_multiparam_array(
    generating_class=fefet_6,
    parameters=[channel_x, channel_y],
    label_schema="{x:03d}",
    axis=1,
    repeat_perp=26,
    meta_rc=1, 
    label_fmt = {
        "size": 50,
        "vertical": False,
        "rotation": 90,
    },  
    count_0 = id_count,
)

id_count += len(array_fefet_6.references)

lib.add(*children_6)
top.add(gdstk.Reference(array_fefet_6, (2700, 1250)))

#--------------HallBar Arrays--------------
hallbar_6 = HallBar.HallBar_design6(layer_map)
hallbar_4 = HallBar.HallBar_design4(layer_map)

channel_y = [20.0, 14.0, 8.0]

# -------------- HallBar_design4 --------------

array_hallbar_4, children_hb4 = make_multiparam_array(
    generating_class=hallbar_4,
    parameters=[channel_y],
    label_schema="{x:03d}",
    axis=0,           # repeat_perp horizontally
    repeat_perp=7,
    repeat_para=3,
    meta_rc=1,
    label_fmt = {
        "size": 65,
        "vertical": False,
        "rotation": 90,
    },  
    count_0 = id_count,
)

id_count += len(array_hallbar_4.references)

lib.add(*children_hb4)
top.add(gdstk.Reference(array_hallbar_4, (-2600, -1325)))

# -------------- HallBar_design6 --------------
array_hallbar_6, children_hb6 = make_multiparam_array(
    generating_class=hallbar_6,
    parameters=[channel_y],
    label_schema="{x:03d}",
    axis=0,
    repeat_perp=7,
    repeat_para=3,
    label_fmt = {
        "size": 65,
        "vertical": False,
        "rotation": 90,
    },  
    count_0 = id_count,
)

id_count += len(array_hallbar_6.references)

lib.add(*children_hb6)
top.add(gdstk.Reference(array_hallbar_6, (2600, -1325)))


#FeCAP_small Example

layer_map_new = {
    "MET_CH_1":     Formatter( 1,  0, 0, 3, 0),
    "MET_SD_2":     Formatter( 2,  0, 1, 0, 0),
    "MET_TE_3":     Formatter( 3,  0, 1, 0, 0),
    "VIA_CL_4":     Formatter( 4,  0, 1, 0, 0),
    "VIA_SDG_5":    Formatter( 5,  0, 1, 0, 0),
    "MET_M1_6":     Formatter( 6,  0, 0, 3, 0),
    "info":         Formatter(29, 99, 1, 0, 0),
    "labels":       Formatter(30, 99, 1, 0, 0),
}

fecap_small = FeCAP.FeCAP_small(layer_map_new)


array_FeCAP_small, children_FeCAP_small = make_rc_array(
    fecap_small,
    [30.0, 25.0, 20.0, 15.0, 10.0, 8.0, 6.0],
    repeat_para=2, #repetitions per parameter
    repeat_perp=7,
    label_schema="{x:03d}",
    count_0 = id_count,
)
array_FeCAP_small.name = "Array_FeCAP6_small1"

id_count += len(array_FeCAP_small.references)

# Add child cells to the library
names = [cell.name for cell in lib.cells]
for cell in children_FeCAP_small:
    if cell.name not in names:
        lib.add(cell)

      

# Add array to top-level layout        
top.add(gdstk.Reference(array_FeCAP_small, (2600, -3125)))


array_FeCAP_small2, children_FeCAP_small2 = make_rc_array(
    fecap_small,
    [30.0, 25.0, 20.0, 15.0, 10.0, 8.0, 6.0],
    repeat_para=2, #repetitions per parameter
    repeat_perp=7,
    label_schema="{x:03d}",
    count_0 = id_count,
)
array_FeCAP_small2.name = "Array_FeCAP6_small2"

id_count += len(array_FeCAP_small2.references)

# Add child cells to the library
names = [cell.name for cell in lib.cells]
for cell in children_FeCAP_small2:
    if cell.name not in names:
        lib.add(cell)

print(type(array_FeCAP_small2))  
# Add array to top-level layout        
top.add(gdstk.Reference(array_FeCAP_small2, (-2600, -3125)))





#profiles
# Create profile stack instance
profile_stack = profiles(layer_map)

# Build the profile structure
profile_cell, profile_components = profile_stack.build()

# Add child cells and reference to top layout
lib.add(*get_children(profile_cell))
top.add(gdstk.Reference(profile_cell, (-4500, 3500)))

# Initialize metal line generator
metal_line_gen = MetalLine(layer_map)

# # === Single MetalLine test structure ===
# test_line = metal_line_gen.build((2000.0, 1.0))  # length 2000 µm, width 1 µm
# lib.add(test_line[0])  # add the generated cell to the library
# top.add(gdstk.Reference(test_line[0], (-2000, 3500)))  # position far away to avoid collision



# add template and optical litho markers
templ_lib = lib

# mask aligner
left_marker, cells = merge.get_template_cell("Align_left", impresources.files(templates) / "optical_markers.gds")
_ = templ_lib.add(*cells)
right_marker, cells = merge.get_template_cell("Align_right", impresources.files(templates) / "optical_markers.gds")
_ = templ_lib.add(*cells)
_ = top.add(
    #gdstk.Reference(left_marker, (-5_200, 4_000)),
    gdstk.Reference(left_marker, (-5_200, 3_000)),
    gdstk.Reference(left_marker, (-5_200, 2_000)),
    gdstk.Reference(left_marker, (-5_200, 1_000)),
    #gdstk.Reference(left_marker, (-5_200, 0)),
    gdstk.Reference(left_marker, (-5_200, -1_000)),
    gdstk.Reference(left_marker, (-5_200, -2_000)),
    gdstk.Reference(left_marker, (-5_200, -3_000)),
    #gdstk.Reference(left_marker, (-5_200, -4_000)),
    )
_ = top.add(
    #gdstk.Reference(left_marker, (5_200, 4_000)),
    gdstk.Reference(left_marker, (5_200, 3_000)),
    gdstk.Reference(right_marker, (5_200, 2_000)),
    gdstk.Reference(right_marker, (5_200, 1_000)),
    #gdstk.Reference(right_marker, (5_200, 0)),
    gdstk.Reference(right_marker, (5_200, -1_000)),
    gdstk.Reference(right_marker, (5_200, -2_000)),
    gdstk.Reference(left_marker, (5_200, -3_000)),
    #gdstk.Reference(left_marker, (5_200, -4_000)),
    )
_ = top.add(
    #gdstk.Reference(left_marker, (0, 4_000)),
    gdstk.Reference(right_marker, (0, 3_000)),
    gdstk.Reference(left_marker, (0, 2_000)),
    gdstk.Reference(right_marker, (0, 1_000)),
    gdstk.Reference(right_marker, (0, -1_000)),
    gdstk.Reference(left_marker, (0, -2_000)),
    gdstk.Reference(right_marker, (0, -3_000)),
    #gdstk.Reference(left_marker, (0, -4_000)),
    )
_ = top.add(
    gdstk.Reference(right_marker, (-4000, 4_000)),
    gdstk.Reference(left_marker, (-2600, 4_000)),
    gdstk.Reference(right_marker, (-1200, 4_000)),
    gdstk.Reference(right_marker, (1200, 4_000)),
    gdstk.Reference(left_marker, (2600, 4_000)),
    gdstk.Reference(right_marker, (4000, 4_000)),
    )    
_ = top.add(
    gdstk.Reference(right_marker, (-4000, -4_000)),
    gdstk.Reference(left_marker, (-2600, -4_000)),
    gdstk.Reference(right_marker, (-1200, -4_000)),
    gdstk.Reference(right_marker, (1200, -4_000)),
    gdstk.Reference(left_marker, (2600, -4_000)),
    gdstk.Reference(right_marker, (4000, -4_000)),
    )     


# direct write
dwl_marker, cells = merge.get_template_cell("AlignmentMarks_BrightField", impresources.files(templates) / "DWL_AlignmentMarks.gds")
_ = templ_lib.add(*cells)
_ = top.add(
    gdstk.Reference(dwl_marker, (0, 0)),
    gdstk.Reference(dwl_marker, (5_200, 0)),
    gdstk.Reference(dwl_marker, (-5_200, 0)),
    gdstk.Reference(dwl_marker, (5_200, 4000)),
    gdstk.Reference(dwl_marker, (5_200, -4000)),
    gdstk.Reference(dwl_marker, (-5_200, 4000)),
    gdstk.Reference(dwl_marker, (-5_200, -4000)),
    gdstk.Reference(dwl_marker, (0, 4000)),
    gdstk.Reference(dwl_marker, (0, -4000)),
    )

# === Final Write ===
templ_lib.write_gds("1x1_Layout.gds")



