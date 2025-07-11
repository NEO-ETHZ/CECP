import gdstk
from ..base import Feature, FabString
from ..shapes import octagon, rectangle, connect_rectangles
from ..format import Formatter
from ..builders import make_via
from ..clearance import Clearance


class HallBar_design4(Feature):
    """planar HallBars that can be measured at level 3. 
    """
    def __init__(self, layer_map: dict[str: Formatter], bounds: gdstk.Polygon = rectangle(500, 340, (0,0))) -> None:
        """
        Parameters
        ----------
        layer_map : dict
            Dictionary of layer formats used for common components. # ? should maybe add a checker for this.
        bounds : gdstk.Polygon, optional
            Polygon representing the bounds of device, effectively determining it's size. Defaults to rectangle of 200 x 250.
        
        Attributes
        ----------
        size : (float, float)
            Dimensions of the feature.
        """
        super().__init__(FabString("HallBar_4_Base"), layer_map, bounds)
        # if there were something common it would go here.
        # e.g. if wanted to avoid the edge or something, but leave empty for now
    
    def build(self, channel_y: float) -> tuple[gdstk.Cell, list]:
        """See parent for detailed doc string (pretty empty at the moment).
        
        Parameters
        ----------
 

        channel_y : float
            HallBar width or y-dimension of channel.   
        
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
        # ensure the cell name is unique
        name = FabString(f"HallBar_3_{int(channel_y*1e3)}")
        device = gdstk.Cell(name)
        device.add(gdstk.Reference(self.main_cell, (0, 0)))


        # == add parametric components ==
        (x0, y0), (x1, y1) = self.bounds.bounding_box()
        ccl = 2.0
        gap = 2.5 #margin from bounding  box edges

        #Channel length
        channel_x = 250.0
        gate_x = 180.0
        gate_T_x = 90.0
        pass_via_x = 80.0
        #Channel square dimensions
        channel_square_size = 20.0

        #HZO VIA dimensions 
        hzo_via_size = 40.0
        hzo_via_R_center_x = channel_x/2 + 50 + hzo_via_size/2
        hzo_via_TR_center_x = 0.0 + 100.0
        hzo_via_TR_center_y = channel_y/2 + 100 + hzo_via_size/2

        #top right (TR) and side right R squares
        channel_square_center_y = 0.0 + channel_y/2 + 20.0
        channel_square_center_x1 = 0.0 + 75.0
        channel_square_center_x2 = 0.0 + channel_x/2 -3*ccl - hzo_via_size/2
        #Channel coonecting rectangle size
        channel_rect_x = ccl
        channel_rect_y = 15.0
        channel_rect_center_x = channel_square_center_x1
        channel_rect_center_y = 0.0 + channel_y/2 + channel_rect_y/2

        
        
        
        #MET_CH_1 Channel bar + 4 connecting rectangles + 6 trapezium pads + center lower rectangle
        channel_bar = rectangle(250.0, channel_y) 

        channel_rect_TR = rectangle(channel_rect_x, channel_rect_y, origin=(channel_rect_center_x, channel_rect_center_y))
        
        channel_rect_BR = channel_rect_TR.copy().mirror((0, 0), (1, 0))
        channel_rect_TL = channel_rect_TR.copy().mirror((0, 0), (0, 1))
        channel_rect_BL = channel_rect_BR.copy().mirror((0, 0), (0, 1))



        #VIA_CL_4 HZO opening VlA to channel contact
        hzo_via_TR = rectangle(hzo_via_size, hzo_via_size, origin=(hzo_via_TR_center_x, hzo_via_TR_center_y))
        hzo_via_R = rectangle(hzo_via_size, hzo_via_size, origin=(hzo_via_R_center_x, 0.0)) 

        hzo_via_BR = hzo_via_TR.copy().mirror((0, 0), (1, 0))
        hzo_via_TL = hzo_via_TR.copy().mirror((0, 0), (0, 1))
        hzo_via_BL = hzo_via_BR.copy().mirror((0, 0), (0, 1))
        hzo_via_L  = hzo_via_R.copy().mirror((0, 0), (0, 1))


        #VIA_SDG_5: etch hrough passivation + G via
        pass_via_TR = gdstk.offset(hzo_via_TR, ccl)
        pass_via_R = gdstk.offset(hzo_via_R, ccl)
        pass_via_BR = [poly.copy().mirror((0, 0), (1, 0)) for poly in pass_via_TR]
        pass_via_TL = [poly.copy().mirror((0, 0), (0, 1)) for poly in pass_via_TR]
        pass_via_BL = [poly.copy().mirror((0, 0), (0, 1)) for poly in pass_via_BR]
        pass_via_L  = [poly.copy().mirror((0, 0), (0, 1)) for poly in pass_via_R]   


        

        #MET_TE_3, Top electrode defining the gate, centered at 0,0 + rectangles to make T shape
        gate = rectangle(gate_x, channel_y - 2*ccl)

        gate_T_y = (y1-y0)/2 -gap- ccl - channel_y/2 + ccl
        ##bottom of gate_T_rectangle is 0.0 + channel_y/2 - ccl = gate_T_y_center - gate_T_y/2
        gate_T_y_center = channel_y/2 - ccl + gate_T_y/2

        gate_T= rectangle(gate_T_x, gate_T_y, origin=(0.0, gate_T_y_center))

        ##VIA_SDG_5: pass G via
        pass_via_rect = rectangle(pass_via_x, channel_y - 4*ccl)

        #MET_M1_6 Top metal pad, comprising of 4 trapeziums TR, BR, TL, BL + L,R trapziums + center polygon
        ##R trapezium
        top_pad_R = gdstk.Polygon([
            (x1-gap, y0+gap),
            (x1-gap, y1-gap),
            (channel_x/2 - 3*ccl - hzo_via_size - 3*ccl, channel_y/2 + ccl),
            (channel_x/2 - 3*ccl - hzo_via_size - 3*ccl, - channel_y/2 -ccl),

        ])

        ##TR_pad
        top_pad_TR = gdstk.Polygon([
            (channel_x/2 - 3*ccl - hzo_via_size - 3*ccl - gap, channel_y/2 + ccl),
            (x1-gap-ccl, y1-gap),
            (50.0 + ccl, y1-gap),
            (50.0 + ccl, channel_y/2 + ccl),

        ])
        
        top_pad_L = top_pad_R.copy().mirror((0, 0), (0, 1))
        top_pad_BR = top_pad_TR.copy().mirror((0, 0), (1, 0))
        top_pad_TL = top_pad_TR.copy().mirror((0, 0), (0, 1))
        top_pad_BL = top_pad_BR.copy().mirror((0, 0), (0, 1))

        top_pad_center = gdstk.Polygon([
            (-50.0, channel_square_center_y),
            (-50.0, y1-gap),
            ( 50.0, y1-gap),
            ( 50.0, channel_square_center_y),
            ])
        
                
        ##VIA_SDG_5: pass G via
        pass_via_rect = gdstk.offset(top_pad_center, -5*ccl)

        #MET_CH_1 channel pads + center bottom rectangle
        channel_TR = gdstk.offset(top_pad_TR, -ccl)
        channel_R = gdstk.offset(top_pad_R, -ccl)

        channel_BR = [poly.copy().mirror((0, 0), (1, 0)) for poly in channel_TR]
        channel_TL = [poly.copy().mirror((0, 0), (0, 1)) for poly in channel_TR]
        channel_BL = [poly.copy().mirror((0, 0), (0, 1)) for poly in channel_BR]
        channel_L  = [poly.copy().mirror((0, 0), (0, 1)) for poly in channel_R]

        channel_rect_bottom = rectangle(100.0, (y1-y0)/2-channel_y/2-ccl-gap, origin=(0.0, y0 + gap + ((y1-y0)/2-channel_y/2-ccl-gap)/2))
        
        #MET_SD_2 metal contact to channel
        cont_TR = gdstk.offset(top_pad_TR, -2*ccl)
        cont_R = gdstk.offset(top_pad_R, -2*ccl)

        cont_BR = [poly.copy().mirror((0, 0), (1, 0)) for poly in cont_TR]
        cont_TL = [poly.copy().mirror((0, 0), (0, 1)) for poly in cont_TR]
        cont_BL = [poly.copy().mirror((0, 0), (0, 1)) for poly in cont_BR]
        cont_L  = [poly.copy().mirror((0, 0), (0, 1)) for poly in cont_R]
        

        device.add(
        *self.layer_map["MET_CH_1"].apply(channel_bar, self.bounds),
        *self.layer_map["MET_CH_1"].apply(channel_rect_TR, self.bounds),
        *self.layer_map["MET_CH_1"].apply(channel_rect_BR, self.bounds),
        *self.layer_map["MET_CH_1"].apply(channel_rect_TL, self.bounds),
        *self.layer_map["MET_CH_1"].apply(channel_rect_BL, self.bounds),
        *self.layer_map["MET_CH_1"].apply(channel_TR, self.bounds),
        *self.layer_map["MET_CH_1"].apply(channel_BR, self.bounds),
        *self.layer_map["MET_CH_1"].apply(channel_TL, self.bounds),
        *self.layer_map["MET_CH_1"].apply(channel_BL, self.bounds),
        *self.layer_map["MET_CH_1"].apply(channel_R, self.bounds),
        *self.layer_map["MET_CH_1"].apply(channel_L, self.bounds),
        *self.layer_map["MET_CH_1"].apply(channel_rect_bottom, self.bounds),
        *self.layer_map["MET_SD_2"].apply(cont_TR, self.bounds),
        *self.layer_map["MET_SD_2"].apply(cont_BR, self.bounds),
        *self.layer_map["MET_SD_2"].apply(cont_TL, self.bounds),
        *self.layer_map["MET_SD_2"].apply(cont_BL, self.bounds),
        *self.layer_map["MET_SD_2"].apply(cont_R, self.bounds),
        *self.layer_map["MET_SD_2"].apply(cont_L, self.bounds),
        *self.layer_map["MET_TE_3"].apply(gate, self.bounds),  
        *self.layer_map["MET_TE_3"].apply(gate_T, self.bounds),  
        *self.layer_map["VIA_CL_4"].apply(hzo_via_TR, self.bounds),
        *self.layer_map["VIA_CL_4"].apply(hzo_via_BR, self.bounds),
        *self.layer_map["VIA_CL_4"].apply(hzo_via_TL, self.bounds),
        *self.layer_map["VIA_CL_4"].apply(hzo_via_BL, self.bounds),
        *self.layer_map["VIA_CL_4"].apply(hzo_via_R, self.bounds),
        *self.layer_map["VIA_CL_4"].apply(hzo_via_L, self.bounds),
        *self.layer_map["VIA_SDG_5"].apply(pass_via_TR, self.bounds),
        *self.layer_map["VIA_SDG_5"].apply(pass_via_BR, self.bounds),
        *self.layer_map["VIA_SDG_5"].apply(pass_via_TL, self.bounds),
        *self.layer_map["VIA_SDG_5"].apply(pass_via_BL, self.bounds),
        *self.layer_map["VIA_SDG_5"].apply(pass_via_R, self.bounds),
        *self.layer_map["VIA_SDG_5"].apply(pass_via_L, self.bounds),
        *self.layer_map["VIA_SDG_5"].apply(pass_via_rect, self.bounds),
        *self.layer_map["MET_M1_6"].apply(top_pad_R, self.bounds),
        *self.layer_map["MET_M1_6"].apply(top_pad_L, self.bounds),
        *self.layer_map["MET_M1_6"].apply(top_pad_TR, self.bounds),
        *self.layer_map["MET_M1_6"].apply(top_pad_TL, self.bounds),
        *self.layer_map["MET_M1_6"].apply(top_pad_BR, self.bounds),
        *self.layer_map["MET_M1_6"].apply(top_pad_BL, self.bounds),
        *self.layer_map["MET_M1_6"].apply(top_pad_center, self.bounds)
        )

   # provide access point export relevant features
        components = {
            "label_pos": (0, -90),
        }
        return device, components
    
    

class HallBar_design6(Feature):
    """planar gated HallBars that can be measured at level 6. 
    """
    def __init__(self, layer_map: dict[str: Formatter], bounds: gdstk.Polygon = rectangle(500, 340, (0,0))) -> None:
        """
        Parameters
        ----------
        layer_map : dict
            Dictionary of layer formats used for common components. # ? should maybe add a checker for this.
        bounds : gdstk.Polygon, optional
            Polygon representing the bounds of device, effectively determining it's size. Defaults to rectangle of 200 x 250.
        
        Attributes
        ----------
        size : (float, float)
            Dimensions of the feature.
        """
        super().__init__(FabString("HallBar_6_Base"), layer_map, bounds)
    
    def build(self, channel_y: float) -> tuple[gdstk.Cell, list]:
        """See parent for detailed doc string (pretty empty at the moment).
        
        Parameters
        ----------
        channel_y : float
            HallBar width or y-dimension of channel.   
        
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
        # ensure the cell name is unique
        name = FabString(f"HallBar_6_{int(channel_y*1e3)}")
        device = gdstk.Cell(name)
        device.add(gdstk.Reference(self.main_cell, (0, 0)))


        # == add parametric components ==
        (x0, y0), (x1, y1) = self.bounds.bounding_box()
        ccl = 2.0
        gap = 2.5 #margin from bounding  box edges

        #Channel length
        channel_x = 250.0
        gate_x = 180.0
        pass_via_x = 80.0
        #Channel square dimensions
        channel_square_size = 20.0

        #HZO VIA dimensions 
        hzo_via_size = 6.0

        #top right (TR) and side right R squares
        channel_square_center_y = 0.0 + channel_y/2 + 20.0
        channel_square_center_x1 = 0.0 + 75.0
        channel_square_center_x2 = 0.0 + channel_x/2 -3*ccl - hzo_via_size/2
        #Channel coonecting rectangle size
        channel_rect_x = ccl
        channel_rect_y = 5.0
        channel_rect_center_x = channel_square_center_x1
        channel_rect_center_y = 0.0 + channel_y/2 + channel_rect_y/2

        
        
        
        #MET_CH_1 Channel bar + 4 squares + 4 connecting rectangles + 4 connnecting trapeziums
        channel_bar = rectangle(250.0, channel_y) 

        channel_sq_TR = rectangle(channel_square_size, channel_square_size, origin=(channel_square_center_x1, channel_square_center_y)) 
        channel_rect_TR = rectangle(channel_rect_x, channel_rect_y, origin=(channel_rect_center_x, channel_rect_center_y))
        channel_trapezoid_TR = gdstk.Polygon(connect_rectangles(channel_sq_TR, channel_rect_TR))

        channel_TR = channel_sq_TR
        for polygon in [channel_rect_TR, channel_trapezoid_TR]:
            channel_TR = gdstk.boolean(channel_TR, polygon, operation="or")

        channel_BR = [poly.copy().mirror((0, 0), (1, 0)) for poly in channel_TR]
        channel_TL = [poly.copy().mirror((0, 0), (0, 1)) for poly in channel_TR]
        channel_BL = [poly.copy().mirror((0, 0), (0, 1)) for poly in channel_BR]


        #VIA_CL_4 HZO opening VlA to channel contact
        hzo_via_TR = rectangle(hzo_via_size, hzo_via_size, origin=(channel_square_center_x1, channel_square_center_y))
        hzo_via_R = rectangle(hzo_via_size, hzo_via_size, origin=(channel_square_center_x2, 0.0)) 

        hzo_via_BR = hzo_via_TR.copy().mirror((0, 0), (1, 0))
        hzo_via_TL = hzo_via_TR.copy().mirror((0, 0), (0, 1))
        hzo_via_BL = hzo_via_BR.copy().mirror((0, 0), (0, 1))
        hzo_via_L  = hzo_via_R.copy().mirror((0, 0), (0, 1))


        #VIA_SDG_5: etch hrough passivation + G via
        pass_via_TR = gdstk.offset(hzo_via_TR, ccl)
        pass_via_R = gdstk.offset(hzo_via_R, ccl)
        pass_via_BR = [poly.copy().mirror((0, 0), (1, 0)) for poly in pass_via_TR]
        pass_via_TL = [poly.copy().mirror((0, 0), (0, 1)) for poly in pass_via_TR]
        pass_via_BL = [poly.copy().mirror((0, 0), (0, 1)) for poly in pass_via_BR]
        pass_via_L  = [poly.copy().mirror((0, 0), (0, 1)) for poly in pass_via_R]   


        #MET_SD_2 metal contact to channel
        cont_TR = gdstk.offset(hzo_via_TR, 2*ccl)
        cont_R = gdstk.offset(hzo_via_R, 2*ccl)

        cont_BR = [poly.copy().mirror((0, 0), (1, 0)) for poly in cont_TR]
        cont_TL = [poly.copy().mirror((0, 0), (0, 1)) for poly in cont_TR]
        cont_BL = [poly.copy().mirror((0, 0), (0, 1)) for poly in cont_BR]
        cont_L  = [poly.copy().mirror((0, 0), (0, 1)) for poly in cont_R]

        #MET_TE_3, Top electrode defining the gate, centered at 0,0
        gate = rectangle(gate_x, channel_y - 2*ccl)

        ##VIA_SDG_5: pass G via
        pass_via_rect = rectangle(pass_via_x, channel_y - 4*ccl)

        #MET_M1_6 Top metal pad, comprising of 4 trapeziums TR, BR, TL, BL + L,R trapziums + center polygon
        ##R trapezium
        top_pad_R = gdstk.Polygon([
            (x1-gap, y0+gap),
            (x1-gap, y1-gap),
            (channel_x/2 - 3*ccl - hzo_via_size - 3*ccl, channel_y/2 + ccl),
            (channel_x/2 - 3*ccl - hzo_via_size - 3*ccl, - channel_y/2 -ccl),

        ])

        ##TR_pad
        top_pad_TR = gdstk.Polygon([
            (channel_x/2 - 3*ccl - hzo_via_size - 3*ccl - gap, channel_y/2 + ccl),
            (x1-gap-ccl, y1-gap),
            (50.0 + ccl, y1-gap),
            (50.0 + ccl, channel_y/2 + ccl),

        ])
        
        top_pad_L = top_pad_R.copy().mirror((0, 0), (0, 1))
        top_pad_BR = top_pad_TR.copy().mirror((0, 0), (1, 0))
        top_pad_TL = top_pad_TR.copy().mirror((0, 0), (0, 1))
        top_pad_BL = top_pad_BR.copy().mirror((0, 0), (0, 1))

        top_pad_center = gdstk.Polygon([
            (-pass_via_x/2 - ccl, -channel_y/2.0),
            (-50.0, channel_square_center_y),
            (-50.0, y1-gap),
            ( 50.0, y1-gap),
            ( 50.0, channel_square_center_y),
            ( pass_via_x/2 + ccl, -channel_y/2.0),
        ])
        
        # add polygons to device cell
        device.add(
        *self.layer_map["MET_CH_1"].apply([channel_bar, channel_TR, channel_BR, channel_TL, channel_BL], self.bounds),
        *self.layer_map["MET_SD_2"].apply([cont_TR, cont_BR, cont_TL, cont_BL, cont_R, cont_L], self.bounds),
        *self.layer_map["MET_TE_3"].apply([gate], self.bounds),   
        *self.layer_map["VIA_CL_4"].apply([hzo_via_TR, hzo_via_BR, hzo_via_TL, hzo_via_BL, hzo_via_R, hzo_via_L], self.bounds),
        *self.layer_map["VIA_SDG_5"].apply([pass_via_TR, pass_via_BR, pass_via_TL, pass_via_BL, pass_via_R, pass_via_L, pass_via_rect], self.bounds),
        *self.layer_map["MET_M1_6"].apply([top_pad_R, top_pad_L, top_pad_TR, top_pad_TL, top_pad_BR, top_pad_BL, top_pad_center], self.bounds),
        )

        #provide access point export relevant features
        components = {
            "label_pos": (0, -90),
        }
        return device, components
    