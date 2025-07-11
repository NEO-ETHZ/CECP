import gdstk
import logging
from importlib import resources as impresources

from . import templates

def get_children(cell: gdstk.Cell) -> set[gdstk.Cell]:
    """Find all cells referenced in the cell specified, recursively.
    
    Parameters
    ----------
    cell : gdstk.Cell
        The cell for which to get all cells it depends on.
    
    Returns
    -------
    set of gdstk.Cell
        All cells referenced by the cell for it's whole hierarchy.
    """
    ref_cells = set()
    ref_cells.add(cell)
    for ref in cell.references:
        ref_cells.add(ref.cell)
        ref_cells = ref_cells.union(get_children(ref.cell))
    return ref_cells


def get_template_cell(
        cell_name: str,
        source_library: str,
        ) -> tuple[gdstk.Cell, list[gdstk.Cell]]:
    """Import a cell from an external library.
    
    Parameters
    ----------
    cell_name : str
        Name of the cell to import.
    source_library : str
        Path to the .gds containing the cell to import.
    
    Returns
    -------
    gdstk.Cell
        The cell specified.
    list of gdstk.Cell
        The cells referenced in the specfied cell. Also contains the cell itself.
    
    Raises
    ------
    ValueError
        Should change this to meaningful error
    
    Example
    --------------
    >>> lib = gdstk.Library()
    >>> main = lib.new_cell("main")
    >>> left_marker, cells = get_template_cell("Align_left", "templates/optical_markers.gds")
    >>> _ = lib.add(*cells)
    >>> right_marker, cells = get_template_cell("Align_right", "templates/optical_markers.gds")
    >>> _ = lib.add(*cells)
    >>> _ = main.add(gdstk.Reference(left_marker, (-44_000, 0)))
    >>> _ = main.add(gdstk.Reference(right_marker, (44_000, 0)))
    >>> lib.save_gds("SomeOutFile.gds")
    """
    lib = gdstk.read_gds(source_library)
    valid_cells = [cell for cell in lib.cells if cell.name == cell_name]
    if len(valid_cells) == 0:
        raise ValueError("No matching cell found, aborting.")
    elif len(valid_cells) > 1:
        raise ValueError("Multiple matching cells found, aborting.")
    cell = valid_cells[0]
    children = get_children(cell)
    return cell, children


def place_cell_in_template(
        cell_to_place: gdstk.Cell, 
        origin: tuple[float, float]=(0, 0), 
        template: str="BRNC_C20mm_dice.gds", 
        target_cell_name: str="user_design_area"
    ) -> gdstk.Library:
    """Place a cell into the target cell of the selected template file.
    
    Parameters
    ----------
    cell_to_place : gdstk.Cell
        Cell to place inside design.
    origin: (float, float), optional
        Position to placecell. Defaults (0, 0).
    template : str, optional
        Name of GDS file to insert the cell into. File must be present in the templates directory. Defaults to BRNC_C20mm_dice.gds.
    target_cell_name : str, optional
        Name of the target cell in the design in which to insert the cell.
    
    Returns
    -------
    gdstk.Library
        The template library with added cell.
    """
    with impresources.as_file(impresources.files(templates).joinpath(template)) as inp_file:
        template_lib = gdstk.read_gds(inp_file)
    
    destination_cell = [c for c in template_lib.cells if isinstance(c, gdstk.Cell) and c.name == target_cell_name][0]
    destination_cell.add(gdstk.Reference(cell_to_place, origin))
    
    children = get_children(cell_to_place)
    template_cell_names = [cell.name for cell in template_lib.cells]
    template_lib.add(cell_to_place)
    
    for cell in children:
        current_cell_names = [cell.name for cell in template_lib.cells]
        if cell.name not in current_cell_names:
            template_lib.add(cell)
        if cell.name in template_cell_names :
            logging.warning(f"Cell '{cell.name}' already present in library.")    
    return template_lib