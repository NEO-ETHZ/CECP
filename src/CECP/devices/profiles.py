import gdstk
import numpy as np

from ..base import Feature, FabString
from ..shapes import rectangle
from ..format import Formatter
from ..builders import make_via
from ..components import make_label




class profiles(Feature):
    """Structures to measure thickness of layers and resist thicknesses after development
    """
    def __init__(self, layer_map: dict[str: Formatter], bounds: gdstk.Polygon=rectangle(800, 300, (0,0))) -> None:
        """
        Parameters
        ----------
        layer_map : dict
            Dictionary of layer formats used for common components. # ? should maybe add a checker for this.
        bounds : gdstk.polygon, optional
            Polygon representing the bounds of device, effectively determining it's size. Defaults to rectangle of 200 x 250.
        
        Attributes
        ----------
        size : (float, float)
            Dimensions of the feature.
        """
        super().__init__(FabString("FeCAPBase"), layer_map, bounds)
    
    def build(self, box_size: float = 130.0, overlap: float = 30.0) -> tuple[gdstk.Cell, list]:
        """
        
        Parameters
        ----------
        box_size : float, optional
            Length of each side of the three identical square cells in microns, defaults to 130
        overlap : float, optional
            Loverlap of the profiles, in microns, defaults to 30
        
        Returns
        -------
        gdstk.Cell
            The cell representing the device.
        dict
            A dict of components of the device that may need to be accessed 
            later. Note that modifying these will not modify the actual 
            polygons in the cell, as these are separate and should be accessed 
            using Formatter.filter.
        """
        ## Create unique cell
        name = FabString(f"profile_stack_{int(box_size * 1e3)}_{int(overlap * 1e3)}")
        device = gdstk.Cell(name)
        device.add(gdstk.Reference(self.main_cell, (0, 0)))


        # Profile layer sequence
        process_layers = ["MET_TE_3", "MET_CH_1", "VIA_SDG_5", "VIA_CL_4", "MET_M1_6"]
        cur_x = 0

        for layer in process_layers:
        # Define three boxes per profile
            pos1 = (cur_x, 0)
            pos2 = (cur_x + box_size, 0)
            pos3 = (cur_x + box_size, -box_size)

            rects = [
                rectangle(box_size, box_size, origin=pos1),
                rectangle(box_size, box_size, origin=pos2),
                rectangle(box_size, box_size, origin=pos3),
            ]
        
            # Apply layer formatting
            device.add(*self.layer_map[layer].apply(rects, self.bounds))

            # Create label and add it
            label_pos = (cur_x + box_size / 2, box_size)
            label = make_label(
                text=layer,
                origin=label_pos,
                size=20.0,
                layer=self.layer_map["labels"].layer,
                datatype=self.layer_map["labels"].datatype,
            )
            device.add(*label)    
            cur_x += 2 * box_size - overlap
        # provide access point to important features
        components = {"label_pos": (box_size, box_size)}
        return device, components
