# all of below could be configured to work on lists or sets of polygons
import gdstk


def invert(
        polygon: gdstk.Polygon | list[gdstk.Polygon], 
        bounding_polygon: gdstk.Polygon | list[gdstk.Polygon]
        ) -> list[gdstk.Polygon]:
    """Inverts a polygon with respect to a bounding polygon. Both can be lists of polygons.
    
    Parameters
    ----------
    polygon : gdstk.Polygon or list of gdstk.Polygon
        Polygon to invert.
    bounding_polygon : gdstk.Polygon or list of gdstk.Polygon
        Polygon to subtract initial polygon from. Defines the limits of the inversion
    
    Returns
    -------
    list of gdstk.Polygon
    
    Example (not sure this makes sense to do here really.)
    -------
    >>> polygon = gdstk.Polygon([(-1, -1), (3, 2), (-2, 4)])
    >>> bounding_polygon = gdstk.rectangle((-5, -5), (5, 5))
    >>> result = invert(polygon, bounding_polygon)
    >>> result[0].points
    array([[ 5.,  5.],
       [-5.,  5.],
       [-5.,  4.],
       [-2.,  4.],
       [ 3.,  2.],
       [-1., -1.],
       [-2.,  4.],
       [-5.,  4.],
       [-5., -5.],
       [ 5., -5.]])
    """
    return gdstk.boolean(bounding_polygon, polygon, "not")


def heal(
        polygon: gdstk.Polygon | list[gdstk.Polygon], 
        ) -> list[gdstk.Polygon]:
    """Merges a list of polygons.
    
    Parameters
    ----------
    polygon : gdstk.Polygon or list of gdstk.Polygon
        Polygons to merge.
    
    Returns
    -------
    list of gdstk.Polygon
    """
    return gdstk.boolean(polygon, [], "or")


def offset_and_subtract(
        polygon: gdstk.Polygon | list[gdstk.Polygon], 
        distance: float, 
        heal_before: bool=True,
        heal_after: bool=False,
        ) -> list[gdstk.Polygon]:
    """Resizes a polygon by the specified distance and subtracts the original polygon, returning a border.
    
    There is no check whether a polygon is shrunk so much that it is removed. This entry is then just removed.
    
    Parameters
    ----------
    polygon : gdstk.Polygon or list of gdstk.Polygon
        Polygon to invert.
    distance : float
        Distance to resize polygon by. Can be negative.
    heal_before : bool, optional
        If true performs merge on input polygons. Defaults to True.
    heal_after : bool, optional
        If true performs merge on resulting polygons. Defaults to False.
    
    Returns
    -------
    list of gdstk.Polygon
    """
    if heal_before:
        polygon = heal(polygon)
    offset = gdstk.offset(polygon, distance)
    if distance < 0:
        result = gdstk.boolean(polygon, offset, "not")
    else:
        result = gdstk.boolean(offset, polygon, "not")
    if heal_after:
        result = heal(result)
    return result


def separate_resolution(
        polygon: gdstk.Polygon | list[gdstk.Polygon], 
        polarity: bool=True, 
        fine_extent: float=0.1,
        overlap: float=0.03,
        min_area: float=0.1, 
        xor_before: bool=False,
        xor_after: bool=False,
        ) -> tuple[list[gdstk.Polygon], list[gdstk.Polygon]]:
    """Separates a polygon into a main body and an overlapping edge. Useful when separating out resolutions for EBL exposures.
    
    Parameters
    ----------
    polygon : gdstk.Polygon
        The polygon to separate.
    polarity : bool, optional
        Whether the feature will be inverted. Alters which way the edges is extruded. The body will still need to be inverted. Defaults to True, meaning there will be no inversion.
    fine_extent : float, optional
        The thickness of the border. Defaults to 0.1.
    overlap : float, optional
        The amount of overlap between the body and the border. Defaults to 0.03.
    min_area : float, optional
        The area below which only the border will be returns. Only used if polarity is True. Defaults to 0.1.
    xor_before : bool, optional
        If true performs boolean xor on input polygons. Defaults to False.
    xor_after : bool, optional
        If true performs boolean xor on resulting polygons. Defaults to False.
    
    Returns
    -------
    list of gdstk.Polygon
        Polygons forming the edge.
    list of gdstk.Polygon
        Polygons forming the body. If the polygon is smaller than min_area and polarity is True, returns an empty list.
    """
    fine = []
    coarse = []
    if isinstance(polygon, gdstk.Polygon):
        polygon = [polygon]
    if xor_before:
        polygon = gdstk.boolean(polygon, [], "xor")
    if polarity:
        for p in polygon:
            if p.area() < min_area:
                fine.append(p)
        else:
            fine.extend(offset_and_subtract(polygon, -fine_extent))
            coarse.extend(gdstk.offset(polygon, -fine_extent+overlap))
    else:
        fine.extend(offset_and_subtract(polygon, fine_extent))
        coarse.extend(gdstk.offset(polygon, fine_extent-overlap))
    if xor_after:
        fine = gdstk.boolean(fine, [], "xor")
        coarse = gdstk.boolean(coarse, [], "xor")
    return fine, coarse