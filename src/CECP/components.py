import gdstk
import numpy as np


def make_label(text: str, size: float=30, origin: tuple[float, float]=(0, 0), rotation: float=0, vertical: bool=False, layer: int=0, datatype: int=0) -> list[gdstk.Polygon]:
    """Create text label and centre at (0, 0).
    Size is roughly height in um for capitalised characters.
    
    Parameters
    ----------
    text : string
        The text to convert to polygons.
    size : float, optional
        The heigh in um of a capitalised letter. Defaults to 40.
    origin : (float, float), optional
        The position to centre the polygons around. Defaults to (0, 0).
    rotation : float, optional
        Angle by which to rotate the text in degrees. Defaults to 0.
    vertical : bool, optional
        Whether to write the text vertically. Defaults to False.
    layer : int, optional
        The layer to set for the polgons. Defaults to 0.
    datatype : int, optional
        The datatype to set for the polgons. Defaults to 0.
    
    Returns
    -------
    list of gdstk.Polygon
        A list containg the polygons representing the text supplied.
    """
    ratio = 16/11 # may depend on font, but fonts are not implemented anyway
    text_polygons = gdstk.text(text, size*ratio, (0, 0), vertical=vertical, layer=layer, datatype=datatype)
    [polygon.rotate(np.deg2rad(rotation)) for polygon in text_polygons]
    # centre text w.r.t. to bounding box, so anchor is there not bottom left
    if len(text_polygons) != 0:
        ((x0, y0), (x1, y1)) = text_polygons[0].bounding_box()
        bbox = [[x0, y0], [x1, y1]]
        for polygon in text_polygons:
            polygon_bbox = polygon.bounding_box()
            if bbox[0][0] > polygon_bbox[0][0]:
                bbox[0][0] = polygon_bbox[0][0]
            if bbox[0][1] > polygon_bbox[0][1]:
                bbox[0][1] = polygon_bbox[0][1]
            if bbox[1][0] < polygon_bbox[1][0]:
                bbox[1][0] = polygon_bbox[1][0]
            if bbox[1][1] < polygon_bbox[1][1]:
                bbox[1][1] = polygon_bbox[1][1]
        # shift text
        for polygon in text_polygons:
            polygon.translate(*(-1 * np.mean(bbox, axis=0)))
            polygon.translate(origin)
    return text_polygons
    