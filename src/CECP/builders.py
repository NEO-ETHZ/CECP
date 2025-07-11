# this is to automate some device building
import gdstk
import numpy as np

from .clearance import Clearance

def make_via(
    polygon: gdstk.Polygon | list[gdstk.Polygon],
    clearance: Clearance=Clearance(2),
    subdivide: None | gdstk.Cell | gdstk.Polygon=None, 
    ) -> list[gdstk.Polygon]:
    """
    
    Parameters
    ----------
    polygon : gdstk.Polygon or list of gdstk.Polygon
        Polygon to connect via to.
    clearance : float, optional
        How much to reduce via size with respect to the polygon. Defaults to 2.
    subdivide : None or gdstk.Polygon or gdstk.Cell, optional
        Whether to divide the area into smaller vias. Defaults to None. If is a 
        polygon this will used as the via.
    
    Returns
    -------
    list of gdstk.Polygon
    # ! todo add: cell capability here
    """
    # might use layer later (e.g. for polarity?)
    if isinstance(subdivide, gdstk.Cell):
        raise NotImplementedError()
    elif isinstance(subdivide, gdstk.Polygon):
        (x0, y0), (x1, y1) = subdivide.bounding_box()
        size_via = (x1 - x0, y1 - y0)
        subdivide_rect = gdstk.rectangle((x0, y0), (x1, y1))
        shrunk_polygon = clearance.apply_clearance(polygon, sign=-1)[0]
        (x0, y0), (x1, y1) = shrunk_polygon.bounding_box()
        shrunk_polygon_rect = gdstk.rectangle((x0, y0), (x1, y1))
        via = []
        for origin in layout(shrunk_polygon_rect, subdivide_rect, np.max(size_via)/2):
            sub_via = subdivide.copy()
            sub_via.translate(origin)
            if shrunk_polygon.contain_all(*sub_via.bounding_box()):
                via.append(sub_via)
        return via
    via = clearance.apply_clearance(polygon, sign=-1)
    return via


def layout(big_rectangle: gdstk.Polygon, small_rectangle: gdstk.Polygon, separation: float) -> list[tuple[float, float]]:
    """Gets the coordinates so that the maximal number of smaller rectangles 
    are placed inside the larger rectangle.
    
    This is achieved by shifting the boxes for the centre and counting which 
    result gives the most fits.
    
    Parameters
    ----------
    big_rectangle : gdstk.polygon
        Rectangular bounds in which smaller rectangle should be distributed.
    small_rectangle
        Rectangular bounds to determine where the shapes can be placed inside 
        larger rectangle.
    separation : float
        How much space to have between two rectangles.
    
    Returns
    -------
    list of (float, float)
        The centre coordinates of the small rectangles so they are distributed 
        inside the larger rectangle.
    """
    (x0, y0), (x1, y1) = big_rectangle.bounding_box()
    big_size = (x1 - x0, y1 - y0)
    big_origin = (x0 + big_size[0]/2, y0 + big_size[1]/2)
    (x0, y0), (x1, y1) = small_rectangle.bounding_box()
    small_size = (x1 - x0 + separation, y1 - y0 + separation)
    
    x_num = np.max([int(big_size[0] / small_size[0]), 1])
    y_num = np.max([int(big_size[1] / small_size[1]), 1])
    x_shift = -x_num / 2 * small_size[0]
    y_shift = -y_num / 2 * small_size[1]
    if x_num % 2 == 0 or x_num == 1:
        x_shift += small_size[0] / 2
    if y_num % 2 == 0 or y_num == 1:
        y_shift += small_size[1] / 2
    coords = []
    for x in range(x_num):
        for y in range(y_num):
            coords.append(
                (
                    big_origin[0] + x_shift + x * small_size[0],
                    big_origin[1] + y_shift + y * small_size[1],
                )
            )
    return coords
    