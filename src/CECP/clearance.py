import gdstk
import logging

"""
here sign means:
 1 : move out -> makes bigger
-1 : move in  -> makes smaller
 0 : split between two (50 % goes in, 50 % goes out)

Not implemented yet.
"""


class Clearance:
    """Class to implement lithography and process clearances and ease their enforcement.
    
    The polygon's centroid is used for the scaling operations.
    """
    def __init__(self, x, y=None, perc_x=0, perc_y=None):
        if y is None:
            y = x
        if perc_y is None:
            perc_y= perc_x
        self.fixed = (x, y)
        self.perc = (perc_x, perc_y)
    
    def apply_clearance(self, polygon, sign=1, **kwargs):
        """Returns list of polygons with the clearance applied.
        """
        if self.fixed[0] != self.fixed[1]:
            logging.warning("Non-uniform fixed clearance is not implemented (yet?) for arbitrary polygons. Resorting to uniform clearance using the largest value. Alternatively use a bounding box based approach")
        scaled_polygon = self._apply_scale(polygon, self.perc[0], self.perc[1], sign)
        result = gdstk.offset(scaled_polygon, sign*self.fixed[0])
        return self._apply_kwargs(result, **kwargs)
    
    def get_clearance_bbox(self, polygon, sign=1, **kwargs):
        """Returns the bounding box of the polygon with the clearance applied.
        
        Supports anisotropic clearances, but does not retain shape information of original polygon.
        """
        scaled_polygon = self._apply_scale(polygon, self.perc[0], self.perc[1], sign)
        result = self._offset_bbox(scaled_polygon, self.fixed[0], self.fixed[1], sign)
        return self._apply_kwargs(result, **kwargs)
    
    def apply_clearances(self, *polygons, xor=False, sign=1, **kwargs):
        """
        """
        cleared_polygons = []
        for polygon in polygons:
            if xor:
                cleared_polygons = gdstk.boolean(cleared_polygons, self.apply_clearance(polygon), "xor")
            else:
                cleared_polygons += self.apply_clearance(polygon, sign=sign)
        return self._apply_kwargs(cleared_polygons, **kwargs)
    
    def get_clearance_bboxes(self, *polygons, xor=False, sign=1, **kwargs):
        """
        """
        cleared_polygons = []
        for polygon in polygons:
            if xor:
                cleared_polygons = gdstk.boolean(cleared_polygons, self.get_clearance_bbox(polygon, sign=sign), "xor")
            else:
                cleared_polygons += self.get_clearance_bbox(polygon, sign=sign)
        return self._apply_kwargs(cleared_polygons, **kwargs)
    
    def get_boundary_clearance(self, polygon, sign=1, **kwargs):
        """Returns polygon which is the clearance itself, without the actual polygon
        
        Useful for isolate operation
        """
        if sign == 1:
            result = gdstk.boolean(
                self.apply_clearance(polygon, sign=sign),
                polygon,
                "not"
            )
        else:
            result = gdstk.boolean(
                polygon,
                self.apply_clearance(polygon, sign=sign),
                "not"
            )
        return self._apply_kwargs(result, **kwargs)
    
    def fill_to_bbox(self, polygons, bbox_polygon, excl_polygon=True, **kwargs):
        """
        excl_polygon controls whether the original polygons should also be included in the final output.
        only defined for enlarging (positive sign)
        """
        result = bbox_polygon.copy()
        for polygon in polygons:
            if not excl_polygon:
                clearance_poly = gdstk.boolean(
                    self.apply_clearance(polygon, sign=1),
                    polygon, "not")
            else:
                clearance_poly = self.apply_clearance(polygon, sign=1)
            result = gdstk.boolean(result, clearance_poly, "not")
        return self._apply_kwargs(result, **kwargs)
    
    @staticmethod
    def _apply_kwargs(poly_obj, **kwargs):
        """Helper to apply polygon keyword arguments (e.g. layer/dataype).
        Should always be called prior to returning polygons outsode of the class.
        Takes either polygon or list of polygons (though doesn't check for bveing polygon atm)
        """
        if isinstance(poly_obj, list):
            for polygon in poly_obj:
                for k,v in kwargs.items():
                    try:
                        setattr(polygon, k, v)
                    except AttributeError:
                        continue
        else:
            for k,v in kwargs.items():
                try:
                    setattr(poly_obj, k, v)
                except AttributeError:
                    continue
        return poly_obj
        
    @staticmethod
    def _apply_scale(polygon: gdstk.Polygon, sx: float, sy: float, sign: int) -> gdstk.Polygon:
        """Returns a rescaled polygon based on the supplied polygon with 
        respect to its centroid.
        
        Parameters
        ----------
        polygon : gdstk.Polygon
            Polygon to rescale.
        sx, sy : float
            Scale to apply in x and y. E.g. 0.2 responds to increasing size 20 %.
        sign : int, should be -1, 0, 1
            Direction in which to apply scaling. If 0 no scaling is applied.
        
        Returns
        -------
        gdstk.Polygon
            A rescaled version of the original polygon
        """
        if sign == 0:
            logging.info("No scaling applied, behaviour for sign=0 not defined.")
            return polygon
        centroid = polygon.points.mean(axis=0)
        return polygon.scale(1+sign*sx, 1+sign*sy, centroid)

    @staticmethod
    def _offset_bbox(polygon: gdstk.Polygon, ox: float, oy: float, sign: int)-> gdstk.Polygon:
        """Returns a rectangle corresponding to the linearly offset bounding 
        box of the supplied polygon.
        
        Parameters
        ----------
        polygon : gdstk.Polygon
            Polygon to rescale.
        ox, oy : float
            Offset to apply in x and y.
        sign : int, should be -1, 0, 1
            Direction in which to apply offset. If 0, the offset is applied 
            symmetrically (only really makes sense for not fully connected 
            polygons). 0 not actually implemented yet.
        
        Returns
        -------
        A offset version of the original polygon
        """
        if sign == 0:
            raise NotImplementedError()
        ((x0, y0), (x1, y1)) = polygon.bounding_box()
        return gdstk.rectangle((x0-sign*ox, y0-sign*oy), (x1+sign*ox, y1+sign*oy))

    def __add__(self, other):
        # should these be doubled?
        return Clearance(
            self.fixed[0] + other.fixed[0],
            self.fixed[1] + other.fixed[1],
            self.perc[0] * other.perc[0],
            self.perc[1] * other.perc[1]
            )

    def __radd__(self, other):
        return other.__add__(self)

    def __sub__(self, other):
        # should these be doubled?
        return Clearance(
            self.fixed[0] - other.fixed[0],
            self.fixed[1] - other.fixed[1],
            self.perc[0] * other.perc[0],
            self.perc[1] * other.perc[1]
            )

    def __rsub__(self, other):
        return Clearance(
            other.fixed[0] - self.fixed[0],
            other.fixed[1] - self.fixed[1],
            other.perc[0] * self.perc[0],
            other.perc[1] * self.perc[1]
            )
    
    def __mul__(self, val):
        try:
            val = float(val)
        except TypeError:
            raise TypeError(f"Multiplication only defined for 'float' * 'Clearance', not for {type(val)}. Could not coerce into float.")
        return Clearance(
            self.fixed[0] * val,
            self.fixed[1] * val,
            self.perc[0] * val,
            self.perc[1] * val,
        )

    def __rmul__(self, val):
        return self.__mul__(val)
    
    def __repr__(self):
        return f"<Clearance: {self.fixed} - {self.perc}>"
    