
import gdstk

from NDL import devices 
from NDL.format_odrso import Formatter
from NDL.array import make_rc_array
from NDL.merge import get_children


layer_map = {
    "mesa": 
        Formatter(0, 0, 0, 1, 0),
    "via":
        Formatter(1, 0, 1, 0, 0),
    "top_electrode":
        Formatter(3, 0, 1, 3, 0)
    }


lib = gdstk.Library()
top = lib.new_cell("TOP")

#"""
# FerroTest Example
ft = devices.test.FerroTest(layer_map)

device_cell, components = ft.build(100)

lib.add(*get_children(device_cell))
top.add(gdstk.Reference(device_cell, (1_000, 0)))

for obj in components:
    (x0, y0), (x1, y1) = obj.bounding_box()
    print(f"{obj}, centred at {(x0+(x1-x0)/2, y0+(y1-y0)/2)}")

array, children = make_rc_array(
    ft,
    [10, 30, 50],
    repeat=3,
    exclusions=[gdstk.rectangle((-1, -1), (1, 1))]
    )

names = [cell.name for cell in lib.cells]
for cell in children:
    if cell.name not in names:
        lib.add(cell)
top.add(gdstk.Reference(array, (0, 0)))


# Coint Example
layer_map = {
    "mesa":                 # extent of ferroelectric used (could separate out trap, but makes everything more annoying)
        Formatter(0, 0, 0, 0, 10),
    "via_mesa_passivation": # hole through passivation to connect top electrode with mesa
        Formatter(5, 0, 1, 0, 10),
    "via_be_hzo":           # hole through hzo* to reach bottom electrode
        Formatter(2, 0, 1, 0, 0),
    "via_be_passivation":   # hole through passivation to reach bottom electrode
        Formatter(5, 0, 1, 0, 10),
    "island":               # isolation of bottom electrode from rest of ground plane
        Formatter(1, 0, 1, 3, 0),
    "te":                   # top electrode, left and right
        Formatter(3, 0, 1, 3, 0)
    }



PSF = devices.ps_ferro.psFerro(layer_map)

device_cell, components = PSF.build(25)

lib.add(*get_children(device_cell))
top.add(gdstk.Reference(device_cell, (-100, 0)))



lib.write_gds("example.gds")
