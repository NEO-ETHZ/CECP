import gdstk
import numpy as np

from ..base import Feature, FabString
from ..shapes import rectangle
from ..format import Formatter
from ..components import make_label


class MetalLine(Feature):
    """Structure for 4-probe metal line measurements 
    """
    def __init__(self, layer_map: dict[str, Formatter], bounds: gdstk.Polygon = rectangle(5000, 300, (0, 0))) -> None:
        """
        Parameters
        ----------
        layer_map : dict
            Dictionary of layer formats used for common components.
        bounds : gdstk.Polygon, optional
            Overall bounding box of the device, used for layer formatting and clipping. Default size fits largest line.

        Attributes
        ----------
        size : (float, float)
            Dimensions of the feature.
        """
        super().__init__(FabString("MetalLineBase"), layer_map, bounds)

    def build(self, lw: tuple[float, float]) -> tuple[gdstk.Cell, dict]:
        l, w = lw 

        """
        Parameters
        ----------
        lw : (float, float)
        A tuple containing (length, width) of the metal line in microns.

        Returns
        -------
        gdstk.Cell
            The cell representing the device.
        list
            A list of components of the device that may need to be accessed 
            later. Note that modifying these will not modify the actual 
            polygons in the cell, as these are separate and should be accessed 
            using Formatter.filter.
        """
        name = FabString(f"MetalLine_{int(l*1e3)}x{int(w*1e3)}")
        device = gdstk.Cell(name)
        device.add(gdstk.Reference(self.main_cell, (0, 0)))

        # Geometry constants
        pad_size = 80.0
        pad_spacing = 20.0

        # 4 pads evenly spaced along x
        pad_origins = [
            (pad_size / 2.0 + i * (pad_size + pad_spacing), pad_size / 2.0)
            for i in range(4)
        ]
        pads = [rectangle(pad_size, pad_size, origin=pos) for pos in pad_origins]
        device.add(*self.layer_map["MET_M1_6"].apply(pads, self.bounds)) 
        
        # # Format and add all shapes to device cell
        # device.add(
        #     *self.layer_map[layer_key].apply(metal_line, self.bounds),
        #     *self.layer_map[layer_key].apply(pad_left, self.bounds),
        #     *self.layer_map[layer_key].apply(pad_right, self.bounds),
        # )

        # # Label text placed above the line
        # label_pos = (l, pad_size + 25)
        # label = make_label(
        #     text=label_text,
        #     origin=label_pos,
        #     size=30.0,
        #     layer=self.layer_map["labels"].layer,
        #     datatype=self.layer_map["labels"].datatype,
        # )
        # device.add(*label)

        # Pass back metadata (e.g., for layout mapping or auto-placement)
        #components = {"label_pos": label_pos}
        components = []
        return device, components