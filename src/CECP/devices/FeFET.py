import gdstk
import numpy as np
from ..base import Feature, FabString
from ..shapes import octagon, rectangle
from ..format import Formatter
from ..builders import make_via
from ..clearance import Clearance
from .. components import make_label

class FeFET_design4(Feature):
    """planar FeFETs that can be measured at level 4. The metal pads are 50um apart.
    """
    def __init__(self, layer_map: dict[str: Formatter], bounds: gdstk.Polygon = rectangle(170, 370, (-57,-45))) -> None:
        """
        Parameters
        ----------
        layer_map : dict
            Dictionary of layer formats used for common components. # ? should maybe add a checker for this.
        bounds : gdstk.polygon, optional
            Polygon representing the bounds of device, effectively determining it's size. Defaults to rectangle of 200 x 250.
        
        Attributes
        ----------
        size : (float, float)
            Dimensions of the feature.
        """
        super().__init__(FabString("FeFET_4_Base"), layer_map, bounds)
    
    def build(self, channel_x: float, channel_y: float) -> tuple[gdstk.Cell, list]:
        """See parent for detailed doc string (pretty empty at the moment).
        
        Parameters
        ----------
        channel_x : float
            x-dimension of channel. 

        channel_y : float
            y-dimension of channel.    
        
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
        name = FabString(f"FeFET_3_{int(channel_x*1e3)}x{int(channel_y*1e3)}")
        device = gdstk.Cell(name)
        device.add(gdstk.Reference(self.main_cell, (0, 0)))


        # == add parametric components ==
        (x0, y0), (x1, y1) = self.bounds.bounding_box()
        ccl = 2.0
        
        #vertical gap between components
        gap = 4.0
        
        #The y-dimensions of top pads (4 gnd, S,D,G) are chosen such that the pad centers are 50um apart from each other.
        # The total height of the 7 pads + 6*gaps was chosen to be 328um (<bounding y 360)
        
        #gate, defined by TE, dimensions
        gate_x = 14
        gate_y = 10



        
        #gnd pad dimensions and x centers
        gnd_x = 87.0
        gnd_y = 36.0
        gnd_center_x = -33.0

        #SOURCE AND DRAIN dimensions and centers
        SD_x = 70.0
        SD_y = 56.0
        S_center_x = -25.0
        S_center_y = 0.0 + 50.00 ##or 0.0 + gnd_y/2 + gap + SD_y/2 

        #GATE dimensions and centers
        G_x = SD_x + 12.5 #added something to merge with bounding path (vertical gate path)
        G_y = 48.0
        G_center_x = S_center_x + 12.5/2
        G_center_y = 0.0 - 3*50.00

        #HZO VIA dimensions and center ##same as SD center in design4 devices 
        hzo_via_size = 25.0
        via_S_center_x = S_center_x
        via_S_center_y = S_center_y


        #MET_TE_3, Top electrode defining the gate: gate_rect above channel (gate_rect)  + rect below gate_top_pad (gate_rect_big) + vertial and horizontal paths
        ###MET_TE_3 gate rect above channel centered at 0,0 
        gate_rect = rectangle(gate_x, gate_y) 

        #MET_CH_1 channel:  channel bar + channel SD pads (rect + trapeziums) + channel comb
        ##MET_CH_1, Channel bar, centered at 0,0
        channel_bar = rectangle(channel_x, 2*via_S_center_y) 
       
        #VIA_CL_4 HZO opening VlA to channel contact
        hzo_via_S = rectangle(hzo_via_size, hzo_via_size, origin=(via_S_center_x, via_S_center_y))
        hzo_via_D = hzo_via_S.copy().mirror((0, 0), (1, 0))

        #VIA_SDG_5: etch hrough passivation, S via, D via, G via
        pass_via_S = gdstk.offset(hzo_via_S, ccl)
        pass_via_D = [polygon.copy().mirror((0, 0), (1, 0)) for polygon in pass_via_S]
        pass_via_G = [polygon.copy().translate(0, -200) for polygon in pass_via_S] 

        #MET_M1_6 Top metal pad, comprising of 
        #1. SD pads: SD rectangle
        #2. G pad: G big rect pad 
        #3. comb-like structure = 4 gnd pads (combs) + connecting vertical rectangle 
        
        ##SD pads
        top_pad_S_rect = rectangle(SD_x, SD_y, origin=(S_center_x, S_center_y))
        top_pad_D_rect = top_pad_S_rect.copy().mirror((0, 0), (1, 0))

        ###gnd pad 2: gnd pad near gate/channel, smaller in x
        gnd2_x = gnd_x - 34.0
        top_pad_gnd2 = rectangle(gnd2_x, gnd_y, origin=(-50.0, 0.0)) 

        ###gnd pad 1,3,4: regular gnd pads, same x centers, different y centers 
        top_pad_gnd1 = rectangle(gnd_x, gnd_y, origin=(gnd_center_x, 0.0 + 2*50.0)) 
        top_pad_gnd3 = rectangle(gnd_x, gnd_y, origin=(gnd_center_x, 0.0 - 2*50.0))
        top_pad_gnd4 = rectangle(gnd_x, gnd_y, origin=(gnd_center_x, 0.0 - 4*50.0))

        ###gnd pad connecting vertical rectangle
        top_pad_gnd_vert = rectangle(60, 360, origin=(-106.5, -45.0))
        
        top_pad_gnd = top_pad_gnd2
        for pad in [top_pad_gnd1, top_pad_gnd3, top_pad_gnd4, top_pad_gnd_vert]:
            top_pad_gnd = gdstk.boolean(top_pad_gnd, pad, operation="or")

        ###G big rect pad
        top_pad_G_rect_big = rectangle(G_x, G_y, origin=(G_center_x, G_center_y))
             
        top_pad_G = top_pad_G_rect_big

        ##MET_TE_3, rect below gate_top_pad (gate_rect_big)
        gate_rect_big = gdstk.offset(top_pad_G, -ccl)
        ##MET_TE_3, vertical and horizontal paths
        ###gate vertical bounding path (6um wide) connecting small and big gate rectangle
        ####gate big rect pad: top right corner: 20.5, -128 
        ####gate small rect above channel: top right corner: 7,5
        gate_vert_path = gdstk.rectangle((20.5-6, -128), (20.5, 5))
        ###gate horizontal bounding path (10um wide) connecting vertical path and small gate rectangle abve channel
        ####gate big rect pad: bottom right corner: 7,-5
        gate_hor_path = gdstk.rectangle((7, -5), (20.5-6, 5))

        gate = gate_rect_big
        for pad in [gate_rect, gate_vert_path, gate_hor_path]:
            gate = gdstk.boolean(gate, pad, operation="or")

        #MET_SD_2 metal contact to channel: contact rectangle + + contact trapeziums + contact bar 
        cont_S_rect = gdstk.offset(top_pad_S_rect, -2*ccl)
        

        cont_S_trapezium = gdstk.Polygon([
            (0.0 - 10 + 2*ccl, 0.0 + 15 + ccl),                          # o1
            (0.0 + 10 - 2*ccl, 0.0 + 15 + ccl),                          # o2
            (0.0 + 10 - 2*ccl, 0.0 + (gnd_y / 2) + gap + 2*ccl),         # o3
            (0.0 - 20 + 2*ccl, 0.0 + (gnd_y / 2) + gap + 2*ccl)          # o4
            ])
        

        cont_S = gdstk.boolean(cont_S_rect, cont_S_trapezium, operation="or")
        cont_D = [polygon.copy().mirror((0, 0), (1, 0)) for polygon in cont_S]

        cont_bar_y = ((15 + ccl)*2 - channel_y)/2
        cont_bar_x = channel_x - 2*ccl
        cont_bar_center_y = 0.0 + 15.0 + ccl - cont_bar_y/2
        cont_bar_S = rectangle(cont_bar_x, cont_bar_y, origin=(0, cont_bar_center_y))
        cont_bar_D = cont_bar_S.copy().mirror((0, 0), (1, 0))


        ##MET_CH_1, channel SD pads
        channel_S = gdstk.offset(cont_S, ccl)
        channel_D = gdstk.offset(cont_D, ccl)
 

        ##MET_CH_1, Channel comb
        channel_comb = gdstk.offset(top_pad_gnd, -ccl)

        # add info label
        label = make_label(f"W{int(channel_x)} L{int(channel_y)}", 25, origin=(-103.5, 50), rotation=90)

        # add polygons to the device
        device.add(
        *self.layer_map["MET_CH_1"].apply([channel_comb, channel_bar, channel_S, channel_D], self.bounds),
        *self.layer_map["MET_SD_2"].apply([cont_S, cont_D, cont_bar_S, cont_bar_D], self.bounds),
        *self.layer_map["MET_TE_3"].apply([gate], self.bounds),
        *self.layer_map["VIA_CL_4"].apply([hzo_via_S, hzo_via_D], self.bounds),
        *self.layer_map["VIA_SDG_5"].apply([pass_via_S, pass_via_D, pass_via_G], self.bounds),
        *self.layer_map["MET_M1_6"].apply([top_pad_S_rect, top_pad_D_rect, top_pad_gnd, top_pad_G], self.bounds),
        *self.layer_map["info"].apply(label, self.bounds),
        )

        # provide access point export relevant features
        components = {
            "label_pos": (-106.5, -150),
        }
        return device, components


class FeFET_design6(Feature):
    """planar FeFETs that can be measured at level 6. The metal pads are 50um apart.
    """
    def __init__(self, layer_map: dict[str: Formatter], bounds: gdstk.Polygon = rectangle(170, 370, (-57,-45))) -> None:
        """
        Parameters
        ----------
        layer_map : dict
            Dictionary of layer formats used for common components. # ? should maybe add a checker for this.
        bounds : gdstk.polygon, optional
            Polygon representing the bounds of device, effectively determining it's size. Defaults to rectangle of 200 x 250.
        
        Attributes
        ----------
        size : (float, float)
            Dimensions of the feature.
        """
        super().__init__(FabString("FeFET_6_Base"), layer_map, bounds)
    
    def build(self, channel_x: float, channel_y: float) -> tuple[gdstk.Cell, list]:
        """See parent for detailed doc string (pretty empty at the moment).
        
        Parameters
        ----------
        channel_x : float
            x-dimension of channel. 

        channel_y : float
            y-dimension of channel.    
        
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
        name = FabString(f"FeFET_6_{int(channel_x*1e3)}x{int(channel_y*1e3)}")
        device = gdstk.Cell(name)
        device.add(gdstk.Reference(self.main_cell, (0, 0)))


        # == add parametric components ==
        (x0, y0), (x1, y1) = self.bounds.bounding_box()
        ccl = 2.0
        
        #vertical gap between components
        gap = 4.0
        
        #The y-dimensions of top pads (4 gnd, S,D,G) are chosen such that the pad centers are 50um apart from each other.
        # The total height of the 7 pads + 6*gaps was chosen to be 328um (<bounding y 360)
        
        #gate, defined by TE, dimensions
        gate_x = 14
        gate_y = 10

       
        #gnd pad dimensions and x centers
        gnd_x = 87.0
        gnd_y = 36.0
        gnd_center_x = -33.0

        #SOURCE AND DRAIN dimensions and centers
        SD_x = 70.0
        SD_y = 56.0
        S_center_x = -25.0
        S_center_y = 0.0 + 50.00 ##or 0.0 + gnd_y/2 + gap + SD_y/2 

        #GATE dimensions and centers
        G_x = SD_x + 12.5 #added something to merge with bounding path (vertical gate path)
        G_y = 48.0
        G_center_x = S_center_x + 12.5/2
        G_center_y = 0.0 - 3*50.00

        #HZO VIA dimensions and center
        hzo_via_size = 4.0
        via_S_center_x = 0.0
        via_S_center_y = 18.0

        #MET_TE_3, Top electrode defining the gate, centered at 0,0
        gate = rectangle(gate_x, gate_y) 

        #MET_CH_1 channel:  channel bar + channel SD rectangle + channel comb
        ##MET_CH_1, Channel bar, centered at 0,0
        channel_bar = rectangle(channel_x, 2*via_S_center_y) 
       
        #VIA_CL_4 HZO opening VlA to channel contact
        hzo_via_S = rectangle(hzo_via_size, hzo_via_size, origin=(via_S_center_x, via_S_center_y))
        hzo_via_D = hzo_via_S.copy().mirror((0, 0), (1, 0))

        #VIA_SDG_5: etch hrough passivation, S via, D via, G via
        pass_via_S = gdstk.offset(hzo_via_S, ccl)
        pass_via_D = [polygon.copy().mirror((0, 0), (1, 0)) for polygon in pass_via_S]
        pass_via_G = rectangle(gate_x - 6*ccl, gate_y - 4*ccl) #centered at 0,0 like gate

        #MET_SD_2 metal contact to channel: contact rectangle + contact bar
        cont_S = gdstk.offset(hzo_via_S, 2*ccl)
        cont_D = [polygon.copy().mirror((0, 0), (1, 0)) for polygon in cont_S]


        cont_bar_y = (2*via_S_center_y - 4*ccl - hzo_via_size - channel_y)/2
        cont_bar_x = channel_x - 2*ccl
        cont_bar_center_y = via_S_center_y - (hzo_via_size + 4*ccl + cont_bar_y)/2
        cont_bar_S = rectangle(cont_bar_x, cont_bar_y, origin=(0, cont_bar_center_y))
        cont_bar_D = cont_bar_S.copy().mirror((0, 0), (1, 0))

        ##MET_CH_1, channel SD rectangle 
        channel_rect_S = gdstk.offset(hzo_via_S, 3*ccl)
        channel_rect_D = [polygon.copy().mirror((0, 0), (1, 0)) for polygon in channel_rect_S]
 
        #MET_M1_6 Top metal pad, comprising of 
        #1. SD pads: SD rectangle + trapezium
        #2. G pad: G big rect pad + G small rect above channel + G vertical bounding path + G horizontal connection bw bounding path and rect above channel 
        #3. comb-like structure = 4 gnd pads (combs) + connecting vertical rectangle 
        
        ##SD pads
        top_pad_S_rect = rectangle(SD_x, SD_y, origin=(S_center_x, S_center_y))
        top_pad_D_rect = top_pad_S_rect.copy().mirror((0, 0), (1, 0))

        top_pad_S_trapezium = gdstk.Polygon([
            (via_S_center_x - 10, via_S_center_y - 10),             # o1
            (via_S_center_x + 10, via_S_center_y - 10),             # o2
            (via_S_center_x + 10, 0.0 + (gnd_y / 2) + gap),         # o3
            (via_S_center_x - 20, 0.0 + (gnd_y / 2) + gap)          # o4
            ])
        top_pad_D_trapezium = top_pad_S_trapezium.copy().mirror((0, 0), (1, 0))


        ###gnd pad 2: gnd pad near gate/channel, smaller in x
        gnd2_x = gnd_x - 34.0
        top_pad_gnd2 = rectangle(gnd2_x, gnd_y, origin=(-50.0, 0.0)) 

        ###gnd pad 1,3,4: regular gnd pads, same x centers, different y centers 
        top_pad_gnd1 = rectangle(gnd_x, gnd_y, origin=(gnd_center_x, 0.0 + 2*50.0)) 
        top_pad_gnd3 = rectangle(gnd_x, gnd_y, origin=(gnd_center_x, 0.0 - 2*50.0))
        top_pad_gnd4 = rectangle(gnd_x, gnd_y, origin=(gnd_center_x, 0.0 - 4*50.0))

        ###gnd pad connecting vertical rectangle
        top_pad_gnd_vert = rectangle(60, 360, origin=(-106.5, -45.0))
        
        top_pad_gnd = top_pad_gnd2
        for pad in [top_pad_gnd1, top_pad_gnd3, top_pad_gnd4, top_pad_gnd_vert]:
            top_pad_gnd = gdstk.boolean(top_pad_gnd, pad, operation="or")

        ###G big rect pad
        top_pad_G_rect_big = rectangle(G_x, G_y, origin=(G_center_x, G_center_y))
        ###G small rect above channel
        top_pad_G_rect_small_1 = gdstk.offset(gate, -ccl)
        ###G vertical bounding path (6um wide) connecting small and big G rectangle
        ####G big rect pad: top right corner: 22.5, -126 or 22.5,-122
        ####G small rect above channel: top right corner: 5,3
        top_pad_G_vert_path = gdstk.rectangle((22.5 - 6, -126), (22.5, 3))
        ###G horizontal bounding path (6um wide) connecting vertical path and small G rectangle
        ####G small rect above channel: bottom right corner: 5,-3
        top_pad_G_hor_path = gdstk.rectangle((5, -3), (22.5 - 6, 3))
        
        top_pad_G = top_pad_G_rect_big
        for pad in [top_pad_G_rect_small_1, top_pad_G_vert_path, top_pad_G_hor_path]:
            top_pad_G = gdstk.boolean(top_pad_G, pad, operation="or")


        ##MET_CH_1, Channel comb
        channel_comb = gdstk.offset(top_pad_gnd, -ccl)
        
        # add info label
        label = make_label(f"W{int(channel_x)} L{int(channel_y)}", 25, origin=(-103.5, 50), rotation=90)
        
        # add all polygons to the device cell
        device.add(
            *self.layer_map["MET_CH_1"].apply([channel_comb, channel_bar, channel_rect_S, channel_rect_D], self.bounds), 
            *self.layer_map["MET_SD_2"].apply([cont_S, cont_D, cont_bar_S, cont_bar_D], self.bounds),
            *self.layer_map["MET_TE_3"].apply([gate], self.bounds),
            *self.layer_map["VIA_CL_4"].apply([hzo_via_S, hzo_via_D], self.bounds),
            *self.layer_map["VIA_SDG_5"].apply([pass_via_S, pass_via_D, pass_via_G], self.bounds),
            *self.layer_map["MET_M1_6"].apply([top_pad_S_rect, top_pad_D_rect, top_pad_S_trapezium, top_pad_D_trapezium, top_pad_gnd, top_pad_G], self.bounds),
            *self.layer_map["info"].apply(label, self.bounds),
        )

        # provide access point export relevant features
        components = {
            "label_pos": (-106.5, -150),
        }
        return device, components
    