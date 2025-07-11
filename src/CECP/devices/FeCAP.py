import gdstk
from ..base import Feature, FabString
from ..shapes import octagon, rectangle, connect_rectangles
from ..format import Formatter
from ..builders import make_via
from ..clearance import Clearance
from .. import operations
from .. components import make_label

class FeCAP_test_str(Feature):
    """Ferroelectric test capacitors with shared bottom electrode. 
    """
    def __init__(self, layer_map: dict[str: Formatter], bounds: gdstk.Polygon=rectangle(255, 200, (0,0))) -> None:
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
        super().__init__(FabString("FeCAP_test_Base"), layer_map, bounds)
    
    def build(self, mesa_size: float) -> tuple[gdstk.Cell, list]:
        """
        
        Parameters
        ----------
        mesa_size : float
            Dimension of the top electrode. Is the shape of an octagon.
        
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
        ## Create unique cell
        name = FabString(f"FerroTest_{int(mesa_size*1e3)}")
        device = gdstk.Cell(name)
        device.add(gdstk.Reference(self.main_cell, (0, 0)))


        # == add parametric components ==

        (x0, y0), (x1, y1) = self.bounds.bounding_box()

        # mesa, extent of device #####Dimension of the top electrode. The top electrode is an octagon.####
        mesa = octagon(mesa_size, origin=(x0 + 160/2, y0  + 153/2))
        offset = 5.0
        
        ##MET_CH_1: Bounding box
        box = self.bounds

        
        # for leakage current measurements, don't pattern a Mesa. Open above the mesa???
        ## top electrode = mesa
        
        ##MET_M1_6 Top metal pad consisting of octagon + filling + gnd pad + L shaped pad
        top_pad_oct = gdstk.offset(mesa, offset)

     

        #filling
        #filling rectangle anchored to bottom-left corner of device bounding box with offset
        top_pad_fill_rect = rectangle(160, 153, origin=(x0 + 160/2, y0  + 153/2)) 
        top_pad_oct2 = gdstk.offset(top_pad_oct, offset)
        top_pad_fill = gdstk.boolean(top_pad_fill_rect, top_pad_oct2, "not")
          

        #gnd pad anchored to top-left corner of device bounding box with offset
        top_pad_gnd = rectangle(235, 37, origin=(x0 + 235/2, y1 - offset - 37/2)) 
        
        #Lpad lower rectangle anchored to bottom-right corner of device bounding box with offset
        top_pad_L_rect1 = rectangle(85, 153, origin=(x1 - offset - 85/2, y0 + 153/2))
        #Lpad lower rectangle anchored to top-right corner of device bounding box without offset, for array continuity
        top_pad_L_rect2 = rectangle(10, 47, origin=(x1 - offset - 10/2, y1 - 47/2))
        top_pad_L = gdstk.boolean(top_pad_L_rect1, top_pad_L_rect2, operation="or")


        ##MET_SD_2 Metal Contact to channel
        cont_rect = gdstk.offset(top_pad_L_rect1, -2*offset)

        ##VIA_CL_4 HZO opening VlA to channel contact
        hzo_via = gdstk.offset(top_pad_L_rect1, -4*offset)


        #VIA_SDG_5 etch through passivation
        pass_via_oct = make_via(mesa, clearance = Clearance(offset))
        pass_via_rect = gdstk.offset(top_pad_L_rect1, -3*offset)

        # add info label
        label = make_label(f"{int(mesa_size)}", 25, origin=(0, 76.5))

        # add all polygons to the device cell
        device.add(
            *self.layer_map["MET_CH_1"].apply(box, self.bounds),
            *self.layer_map["MET_SD_2"].apply(cont_rect, self.bounds),
            *self.layer_map["MET_TE_3"].apply(mesa, self.bounds),
            *self.layer_map["VIA_CL_4"].apply(hzo_via, self.bounds),
            *self.layer_map["VIA_SDG_5"].apply([pass_via_oct, pass_via_rect], self.bounds),
            *self.layer_map["MET_M1_6"].apply([top_pad_oct, top_pad_fill, top_pad_gnd, top_pad_L], self.bounds),
            *self.layer_map["info"].apply(label, self.bounds)    
        )
        
        # provide access point to important features
        components = {"label_pos": (80, -23.5)}
        return device, components


# sort of fixed dimensions
UVL_CL = 2
EBL_CL = 0.05
dicing_kerf = 10
dicing_street = 100

# Clearance
uvl = Clearance(UVL_CL)
ebl = Clearance(EBL_CL)
# it would make working with the code much easier if these and layer_map were globabl

class FeCAP_small(Feature):    
    """Single ferroelectric element in the picosecond bow tie geometry, with small top metal pads
    """
    def __init__(self, layer_map: dict[str: Formatter], bounds: gdstk.Polygon=rectangle(300, 170)) -> None:
        super().__init__(
            FabString("FeCAP_smallBase"), 
            layer_map, 
            bounds
            )
        # design parts shared between versions
        # all integrated below as will take different layer maps
        self.components = {
            "pad": rectangle(100, 43, (90, 0))
        }
    
    def build(self, mesa_size: float, via_shape: None | gdstk.Polygon | gdstk.Cell=None) -> tuple[gdstk.Cell, dict]:
        """
        Parameters
        ----------
        mesa_size : float
            Dimension of the mesa. Is the shape of an octagon.
        via_shape : None or gdstk.Polygon or gdstk.Cell
            The shape to use for the passivation vias. If None, uses the same 
            shape as for the mesa. Defaults to None.
        
        Returns
        -------
        gdstk.Cell
            Cell of the generated device.
        dict
            A dict of components of the device that may need to be accessed 
            later. Note that modifying these will not modify the actual 
            polygons in the cell, as these are separate and should be accessed 
            using Formatter.filter.
        """
        name = FabString(f"FeCAP_small_{int(mesa_size*1e3)}")
        device = gdstk.Cell(name)
        device.add(
            gdstk.Reference(self.main_cell, (0, 0))
        )

        #MET_TE_3: mesa + trapezoid + filling????
        ## mesa
        mesa = octagon(mesa_size)
        
        #VIA_SDG_5 etch through passivation: Via over mesa (TE) + via to reach BE
        pass_via_mesa = make_via(mesa, uvl)

        ##MET_SD_2 Metal Contact to channel/bottom electrode, is the shape of a rectangle 
        cont_rect = uvl.apply_clearance(self.components["pad"], sign=-1)[0]

        #pass_via_BE = make_via(botelox, clearance=ebl+uvl) #multiple smaller vias instead of one continuous rectangle
        pass_via_rect = uvl.apply_clearance(cont_rect, sign=-1)[0]


        ##MET_TE_3: trapezoid, passive element to point towards mesa in SEM
        trapezoid = gdstk.Polygon(
            connect_rectangles(
                Clearance(2*UVL_CL, 0).get_clearance_bbox(mesa), 
                Clearance(2*UVL_CL, -UVL_CL).get_clearance_bbox(cont_rect),
            )
        )

        ##VIA_CL_4 HZO opening VlA to channel contact
        hzo_via = uvl.apply_clearance(pass_via_rect, sign=-1)[0]
        

        # MET_CH_1: island
        island = gdstk.boolean(
            [
                uvl.get_clearance_bbox(mesa), 
                connect_rectangles(
                    uvl.get_clearance_bbox(mesa), 
                    uvl.get_clearance_bbox(cont_rect),
                ),  
                uvl.get_clearance_bbox(cont_rect)
                ], [], "xor"
        )
        island = uvl.apply_clearances(*island)[0]

        # MET_M1_6: top pad
        top_pad = island.copy()
        top_pad.mirror((0,0), (0,1))
        top_pad = [
            uvl.apply_clearance(self.components["pad"])[0], # right side
            top_pad,  # left side
        ]
        # apply formatting and add to device
        # separate critical from non-critical parts of mesa:
        mesa_low_res = self.layer_map["MET_TE_3"].new({"separate_resolution": 0})
        mesa_parts = [trapezoid]
        formatted_mesa = self.layer_map["MET_TE_3"].apply(mesa, self.bounds)
        if self.layer_map["MET_TE_3"].polarity:
            mesa_parts.append(*operations.invert(island, self.bounds))
            device.add(
                *formatted_mesa,
                *mesa_low_res.apply(mesa_parts, self.bounds),
            )
        else:
            coarse_mesa = self.layer_map["MET_TE_3"].filter(formatted_mesa)
            fine_mesa = []
            for polygon in formatted_mesa:
                if polygon not in coarse_mesa:
                    fine_mesa.append(polygon)
            m1 = gdstk.boolean(coarse_mesa, island, "xor")
            mesa_parts = operations.heal([*m1, *mesa_parts])
            device.add(
                *fine_mesa,
                *mesa_low_res.apply(mesa_parts, self.bounds),
            )
      
        # add all polygons to the device cell
        device.add(
            *self.layer_map["MET_CH_1"].apply(island, self.bounds),
            *self.layer_map["MET_SD_2"].apply(cont_rect, self.bounds),
            *self.layer_map["VIA_CL_4"].apply(hzo_via, self.bounds),
            *self.layer_map["VIA_SDG_5"].apply([pass_via_mesa, pass_via_rect], self.bounds),
            *self.layer_map["MET_M1_6"].apply(top_pad, self.bounds),
        )
        
        # provide access point export relevant features
        components = {
            "label_pos": (0, -60),
        }
        return device, components