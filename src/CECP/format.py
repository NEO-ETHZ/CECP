import gdstk

from . import operations
from .utils import helpers


class Formatter:
    """ToDo
    """
    def __init__(self, 
                 layer: int, 
                 datatype: int=0, 
                 polarity: bool=True, 
                 isolate: bool | float=False, 
                 separate_resolution: bool=False):
        """
                
        Parameters
        ----------
        layer : float
            Distance to resize polygon by. Can be negative.
        datatype : bool, optional
            If true performs boolean xor on input polygons. Defaults to False.
        polarity : bool, optional
            Whether to invert polarity of design. True means no changes occur Defaults to True.
        isolate : bool, optional
            Whether to isolate polygons, replacing them with an edge of a set thickness. If True the value is used as the thickness. Defaults to False.
        separate_resolution : bool, optional
            Whether to separate the polygons into fine and coarse polygons. Defaults to False. If True the layer of the fine polygons is this value added to the layer specified.
        
        """
        self.layer = layer
        self.datatype = datatype
        self.polarity = polarity
        self.isolate = isolate
        self.separate_resolution = separate_resolution
    
    def apply(self, 
              polygon: gdstk.Polygon | list[gdstk.Polygon], 
              bounding_polygon: gdstk.Polygon | None=None
              ) -> list[gdstk.Polygon]:
        """Apply the format a list of polygons
        
        Ignoring kwargs for now.
        
        Parameters
        ----------
        polygon : gdstk.Polygon or list of gdstk.Polygon
            Polygons to apply the format to
        bounding_polygon : gdstk.Polygon or None
            Bounding polygon used for inversion operation.. Defaults to None.
        
        Returns
        -------
        list of gdstk.Polygon with the formatting applied.
        """
        if isinstance(polygon, list):
            polygon = helpers.flatten(polygon)
        if self.isolate:
            polygon = operations.offset_and_subtract(polygon, self.isolate)
        if self.separate_resolution:
            fine, polygon = operations.separate_resolution(polygon, polarity=self.polarity)
            for p in fine:
                p.layer = self.layer + self.separate_resolution
                p.datatype = self.datatype
        if not self.polarity:
            if bounding_polygon is None:
                raise ValueError("No bounding polygon provided, necessary for inversion.")
            polygon = operations.invert(polygon, bounding_polygon)
        if isinstance(polygon, gdstk.Polygon):
            polygon = [polygon]
        for p in polygon:
            p.layer = self.layer
            p.datatype = self.datatype
        if self.separate_resolution:
            polygon.extend(fine)
        return polygon
    
    def filter(self, polygons: list[gdstk.Polygon]) -> list[gdstk.Polygon]:
        """Filters a list of polygons for those matching the specified layer 
        and datatype of the format.
        
        Parameters
        ----------
        polygons : list of gdstk.Polygon
            The list of polygons to filter.
        
        Returns
        -------
        list of gdstk.Polygon
            The filtered list.
        """
        filtered_polygons = []
        for polygon in polygons:
            if polygon.layer == self.layer and polygon.datatype == self.datatype:
                filtered_polygons.append(polygon)
        return filtered_polygons
        
    def new(self, kwargs: dict):
        """Returns a new class with modified entries.

        Parameters
        ----------
        kwargs : dict
            Dictionary of attributes to alter.
        
        Returns
        -------
        Formatter
            The new Formatter with modifications.
        """
        args = {
            "layer": self.layer,
            "datatype": self.datatype, 
            "polarity": self.polarity, 
            "isolate": self.isolate, 
            "separate_resolution": self.separate_resolution
            }
        args = args | kwargs
        return type(self)(
            args["layer"], 
            args["datatype"], 
            args["polarity"], 
            args["isolate"], 
            args["separate_resolution"]
        )