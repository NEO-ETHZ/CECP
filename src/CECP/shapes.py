import gdstk
import numpy as np


def rectangle(x: float, y: float, origin: tuple[float, float] = (0,0)) -> gdstk.Polygon:
    """Returns a rectangular polygon centred around origin of shape (x, y).

    Parameters
    ----------
    x : float
        The horizontal size of the octagon.
    y : float, optional
        The vertical size of the octagon. Defaults to x.
    origin: (float, float), optional
        The coordinate around which to centre the octagon. Defaults to (0, 0).
    
    Returns
    -------
    gdstk.Polygon
        A polygon with the points of a rectangle.
    """
    return gdstk.rectangle(
        (origin[0]-x/2, origin[1]-y/2), 
        (origin[0]+x/2, origin[1]+y/2)
    )


def octagon(x: float, y: float | None = None, origin: tuple[float, float] = (0,0), ratio_x: float = 1/6, ratio_y: float | None = None) -> gdstk.Polygon:
    """Returns an octagon polygon centred around origin of shape (x, y).

    Parameters
    ----------
    x : float
        The horizontal size of the octagon.
    y : float, optional
        The vertical size of the octagon. Defaults to x.
    origin: (float, float), optional
        The coordinate around which to centre the octagon. Defaults to (0, 0).
    ratio_x : float, optional
        How far to cut the corners of a rectangle back in x to form the
        octagonal shape. Defaults to 1/6.
    ratio_y : float, optional
        How far to cut the corners of a rectangle back in y to form the
        octagonal shape. Defaults to 1/6.
    
    Returns
    -------
    gdstk.Polygon
        A polygon with the points of an octagon.
    """
    if y is None:
        y = x
    if ratio_y is None:
        ratio_y = ratio_x
    return gdstk.Polygon([
            (origin[0]+2*x*ratio_x, origin[1]+y/2),
            (origin[0]+x/2,         origin[1]+2*y*ratio_y),
            (origin[0]+x/2,         origin[1]-2*y*ratio_y),
            (origin[0]+2*x*ratio_x, origin[1]-y/2),
            (origin[0]-2*x*ratio_x, origin[1]-y/2),
            (origin[0]-x/2,         origin[1]-2*y*ratio_y),
            (origin[0]-x/2,         origin[1]+2*y*ratio_y),
            (origin[0]-2*x*ratio_x, origin[1]+y/2)
        ])


def connect_rectangles(rectangle1: gdstk.Polygon, rectangle2: gdstk.Polygon) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]:
    """Returns vertices of a polygon to simply connect two rectangle using
    their closest corners.
    
    The corners used are determined by the position of 
    the centroids, in a 45 degree rotated quadrant system.
    
    Parameters
    ----------
    rectangle1 : gdstk.Polygon
        First rectangle to get closest corners from.
    rectangle2 : gdstk.Polygon
        Second rectangle to get closest corners from.
    
    Returns
    -------
    ((x0, y0), (x1, y1), (x2, y2), (x3, y3))
        Corner coordinates of the connecting trapezoid.
    """
    rp1 = rectangle1.points
    rp2 = rectangle2.points
    c1 = rp1.mean(axis=0)
    c2 = rp2.mean(axis=0)
    dx = c2[0] - c1[0]
    dy = c2[1] - c1[1]
    ax = np.abs(dx) > np.abs(dy)
    # could be made a bit more concise
    if dx >= 0 and dy >= 0:
        if ax: # 2 right of 1
            return (rp1[1], rp2[0], rp2[3], rp1[2])
        else:  # 2 above 1
            return (rp1[2], rp2[1], rp2[0], rp1[3])
    elif dx < 0 and dy >= 0:
        if ax: # 2 left of 1
            return (rp1[3], rp2[2], rp2[1], rp1[0])
        else:  # 2 above 1
            return (rp1[2], rp2[1], rp2[0], rp1[3])
    elif dx >= 0 and dy < 0:
        if ax: # 2 right of 1
            return (rp1[1], rp2[0], rp2[3], rp1[2])
        else:  # 2 below 1
            return (rp1[0], rp2[3], rp2[2], rp1[1])
    elif dx < 0 and dy < 0:
        if ax: # 2 left of 1
            return (rp1[3], rp2[2], rp2[1], rp1[0])
        else:  # 2 below 1
            return (rp1[0], rp2[3], rp2[2], rp1[1])
