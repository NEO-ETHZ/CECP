from abc import ABC, abstractmethod
import gdstk

from .format import Formatter

class Feature(ABC):
    """Base class that all device classes should inherit from.
    
    Note that is is *essential* to write a build function if you subclass this.
    # ? maybe this could also require to specify the label location
    """
    def __init__(self, name: str, layer_map: dict[str: Formatter], bounds: gdstk.Polygon) -> None:
        self.name = name
        self.layer_map = layer_map
        self.bounds = bounds
        (x0, y0), (x1, y1) = bounds.bounding_box()
        self.size = (x1 - x0, y1 - y0)
        self.main_cell = gdstk.Cell(self.name)
    
    @abstractmethod
    def build(self) -> tuple[gdstk.Cell, list]:
        """Returns the cell of the device.
        
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
        pass

    def get_label_loc(self) -> tuple[float, float]:
        """Get the position where a label should be centred.
        
        Returns
        -------
        (float, float)
            Coordinates where centre of label should go.
        """
        pass


class FabString(str):
    """String checking and formatting for compatibility with Heidelberg tools.
    
    Used for verifying cell names.
    
    The string type is slightly more tedious to inherit from apparently.
    """
    def __new__(cls, text, **kw):
        if type(text) is not str:
            raise TypeError(f"Expected string, got {type(text)}.")
        legal_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        max_len = 47 # might not be absolute max length
        if "." in text:
            text = text.replace(".", "p")
        illegal_chars = {char for char in text if char not in legal_characters}
        if illegal_chars != set():
            raise ValueError(f"Illegal characters in name: {text} ('"+"', '".join(illegal_chars)+"').")
        if len(text) > max_len:
            raise ValueError(f"Max name length of {max_len} exceeded.")
        return str.__new__(cls, text, **kw)