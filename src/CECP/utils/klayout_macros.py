import logging


def run_klayout_macro(script_body: str, klayout_path: str) -> None:
    """Create, run and then delete a python  macro in KLayout.

    Args:
        script_body: The python code to execute inside the macro.
        klayout_path: Path to the KLayout executable. It is best to add it your
        OS path to avoid messing about with this.
    """
    logging.info("running KLayout macro...")
    import subprocess
    import os
    scriptfilename = "temp.lym"
    script_header = """<?xml version="1.0" encoding="utf-8"?>
<klayout-macro>
<description/>
<version/>
<category>pymacros</category>
<prolog/>
<epilog/>
<doc/>
<autorun>false</autorun>
<autorun-early>false</autorun-early>
<priority>0</priority>
<shortcut/>
<show-in-menu>false</show-in-menu>
<group-name/>
<menu-path/>
<interpreter>python</interpreter>
<dsl-interpreter-name/>
<text>"""
    script_footer = """</text>
</klayout-macro>"""

    with open(scriptfilename, 'w') as f:
        f.write(script_header)
        f.write(script_body)
        f.write(script_footer)
    subprocess.run([klayout_path, '-z', '-r', scriptfilename])
    os.remove(scriptfilename)


def resave_klayout(infile: str, klayout_path: str = "klayout") -> None:
    """I have seen that KLayout can generate smaller files and remove things that makes the conversion
    for the DWL fail. This function just opens and saves it in KLayout to handle that.
    """
    script_body = f"""import pya
file_path = "{infile}"
layout = pya.Layout()
lmap = layout.read(file_path)
layout.write(file_path)"""
    run_klayout_macro(script_body, klayout_path)


def export_png(infile: str, 
    layers: list[int],
    edge_coords: tuple[float, float, float, float],
    lyp_file: str = R"default.lyp",
    klayout_path: str = "klayout",
    px_per_um: float | None = 0.5, # set this to None if want to eplxicitly set pixels in x_res, y_res
    x_res: int = 640,
    y_res: int = 480
    ) -> None:
    R"""Example usage:

    steps = [
        [21, 90],
        [21, 90, 24],
        [21, 90, 24, 20],
        [21, 90, 24, 20, 23],
        [21, 90, 24, 20, 23, 26, 30]
    ]

    for layer_list in steps:
        export_png(
            R"...\single_cell.gds",
            layer_list,
            (-300, 300, -25, 225),
            klayout_path=R"...klayout_app.exe",
            px_per_um=6
        )
    """
    script_body = f"""import pya
from pathlib import Path

l = {edge_coords[0]} # left
r = {edge_coords[1]} # right
b = {edge_coords[2]} # bottom
t = {edge_coords[3]} # top

px_per_um = {px_per_um}

file_path = R"{infile}" #Path("{infile}").absolute().as_posix()
app = pya.Application.instance()
mw = app.main_window()

mw.load_layout(file_path)

lv = mw.current_view()

lv.load_layer_props(R"{lyp_file}")

layers_to_print = [{", ".join([str(layer) for layer in layers])}]

for lyp in lv.each_layer():
  #lyp.fill_color     = 0
  #lyp.frame_color    = 0
  #lyp.dither_pattern = 0
  lyp.visible = False
  if lyp.source_layer in layers_to_print:
    lyp.visible = True
  
lv.update_content()

lv.set_config("grid-visible", "false")
lv.set_config("grid-show-ruler", "false")
lv.max_hier()

lv.zoom_box(pya.DBox(l, b, r, t))
if px_per_um is None:
  x_res = {x_res}
  y_res = {y_res}
else:
  x_res = int(px_per_um*(r-l)) 
  y_res = int(px_per_um*(t-b))

lv.save_image(R"image_file_{layers}.png", x_res, y_res)
pya.MainWindow.instance().close_current_view()"""
    run_klayout_macro(script_body, klayout_path)
