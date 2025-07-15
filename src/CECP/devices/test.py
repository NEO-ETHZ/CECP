import gdstk
from ..base import Feature, FabString
from ..shapes import octagon, rectangle
from ..format import Formatter
from ..builders import make_via
from .. import components


UVL_CL = 2 # this should not be here really


class FourPoint(Feature):
    """
    """
    def __init__(self):
        raise NotImplementedError()


class ViaChain(Feature):
    """
    """
    def __init__(self):
        raise NotImplementedError()


class ProfilometerTest(Feature):
    """Profilometer test structure. Can be used to probe the height of an 
    etched or lifted-off structure or resist layer. Typically arranged into an 
    array for all process layers.
    """
    def __init__(self, layer_map: dict[str: Formatter], dim: tuple[float, float]=(100, 100), bounds: gdstk.Polygon=rectangle(150, 150)):
        """
        Parameters
        ----------
        layer_map : dict
            Dictionary of layer formats used for common components. # ? should maybe add a checker for this.
        dim : (float, float)
            Size of the rectangle to expose for the measurement.
        bounds : gdstk.polygon, optional
            Polygon representing the bounds of device, effectively determining it's size. Defaults to rectangle of 150 x 150.
        
        Attributes
        ----------
        size : (float, float)
            Dimensions of the feature.
        """
        super().__init__(FabString("ProfilometerTest"), layer_map, bounds)
        self.dim = dim
        # remove isolate as otherwise structure will be too small
        for key, item in self.layer_map.items():
            if item.isolate:
                item.isolate = 0
        self.components = {}
    
    def build(self, layer_key: str):
        """Generate the cell of such a test rectangle.
        
        Parameters
        ----------
        layer_key : str
            Key of layer_map for which to generate the test device.
        
        Returns
        -------
        gdstk.Cell
            The cell representing the device. Consists of a label and the 
            rectangle to measure.
        (float, float)
            The centre coordinates of the measurement rectangle
        """
        layer = self.layer_map[layer_key].layer
        name = FabString(f"ProfilometerTest_L{layer}_{layer_key}")
        device = gdstk.Cell(name)
        device.add(gdstk.Reference(self.main_cell, (0, 0)))
        parts = [rectangle(self.dim[0], self.dim[1], origin=(0, -15))]
        parts += components.make_label(str(layer), origin=(0, 60))
        device.add(
            *self.layer_map[layer_key].apply(parts, self.bounds, override_sep_res=True),
        )
        return device, {"label_pos":(0, 0)}
        

# class ProfilometerArray(Feature):
#     """I imagine this is not a class but just calls a function from array.py
#     """
#     def __init__(self, layer_map: dict[str: Formatter]):
#         raise NotImplementedError()


class InsulatorLeakage(Feature):
    """
    """
    def __init__(self):
        raise NotImplementedError()


class FerroTest(Feature):
    """Ferroelectric test device. Does not provide a bottom electrode, but 
    expects that connection to be made by breaking another device or a short 
    through the passivation.
    """
    def __init__(self, layer_map: dict[str: Formatter], bounds: gdstk.Polygon=rectangle(200, 250)) -> None:
        """
        Parameters
        ----------
        layer_map : dict
            Dictionary of layer formats used for common components. # ? should maybe add a checker for this.
        bounds : gdstk.polygon, optional
            Polygon representing the bounds of device, effectively determining it's size. Defaults to rectangle of 200 x 250.
        """
        super().__init__(FabString("FerroTestBase"), layer_map, bounds)
        # if there were something common it would go here.
        # e.g. if wanted to avoid the edge or something, but leave empty for now
        self.components = {
            "label_pos": (0, 100)
        }
    
    def build(self, mesa_size: float) -> tuple[gdstk.Cell, list]:
        """See parent for detailed doc string (pretty empty at the moment).
        
        Parameters
        ----------
        mesa_size : float
            Dimension of the top electrode. The top electrode is an octagon.
        
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
        # ensure the cell name is unique
        name = FabString(f"FerroTest_{int(mesa_size*1e3)}")
        device = gdstk.Cell(name)
        device.add(gdstk.Reference(self.main_cell, (0, 0)))
        # == add parametric components ==
        # mesa, extent of device
        mesa = octagon(mesa_size) 
        device.add(
            *self.layer_map["mesa"].apply(mesa, self.bounds)
        )
        # etch through passivation if specified
        if "via" in self.layer_map.keys():
            via = make_via(mesa)
            device.add(
                *self.layer_map["via"].apply(via, self.bounds),
            )
        # va metallisation & probing pad if specified
        if "top_electrode" in self.layer_map.keys():
            top_electrode = gdstk.offset(mesa, -1)
            device.add(
                *self.layer_map["top_electrode"].apply(top_electrode, self.bounds)
            )
        # provide access point to important features
        # ? might make sense to package this as a dictionary
        components = {
            "mesa": mesa,
            "metadata": {
                "mesa_area": mesa.area(),
            },
        } | self.components
        return device, components
    
    def get_label_loc(self) -> tuple[float, float]:
        """Get the position where a label should be centred.
        
        Returns
        -------
        (float, float)
            Coordinates where centre of label should go.
        """
        return (self.size[0]/2, self.size[1]/4)