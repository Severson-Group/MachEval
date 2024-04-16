import numpy as np

from ...dimensions.dim_linear import DimLinear
from ...dimensions.dim_angular import DimAngular
from ...dimensions import DimRadian
from ..cross_sect_base import CrossSectBase, CrossSectToken

__all__ = ['CrossSectFluxBarrierRotor','CrossSectFluxBarrierRotorPartial','CrossSectFluxBarrierRotorPartialBarrier1','CrossSectFluxBarrierRotorPartialBarrier2']

class CrossSectFluxBarrierRotor(CrossSectBase):
    def __init__(self, **kwargs: any) -> None:
        '''
        Initialization function for Flux Barrier Rotor class. This function takes in
        arguments and saves the information passed to private variable to make
        them read-only
        Parameters
        ----------
        **kwargs : any
            DESCRIPTION. Keyword arguments provided to the initialization function.
            The following argument names have to be included in order for the code
            to execute: name, dim_l, dim_t, dim_theta, location.
        Returns
        -------
        None
        '''
        self._create_attr(kwargs)

        super()._validate_attr()
        self._validate_attr()

    @property
    def dim_alpha_b(self):
        return self._dim_alpha_b
    
    @property
    def dim_r_ri(self):
        return self._dim_r_ri

    @property
    def dim_r_ro(self):
        return self._dim_r_ro

    @property
    def dim_r_f1(self):
        return self._dim_r_f1

    @property
    def dim_r_f2(self):
        return self._dim_r_f2

    @property
    def dim_r_f3(self):
        return self._dim_r_f3

    @property
    def dim_d_r1(self):
        return self._dim_d_r1

    @property
    def dim_d_r2(self):
        return self._dim_d_r2

    @property
    def dim_d_r3(self):
        return self._dim_d_r3

    @property
    def dim_w_b1(self):
        return self._dim_w_b1

    @property
    def dim_w_b2(self):
        return self._dim_w_b2

    @property
    def dim_w_b3(self):
        return self._dim_w_b3

    @property
    def dim_l_b1(self):
        return self._dim_l_b1

    @property
    def dim_l_b2(self):
        return self._dim_l_b2

    @property
    def dim_l_b3(self):
        return self._dim_l_b3

    @property
    def dim_l_b4(self):
        return self._dim_l_b4

    @property
    def dim_l_b5(self):
        return self._dim_l_b5

    @property
    def dim_l_b6(self):
        return self._dim_l_b6

    @property
    def p(self):
        return self._p

    def draw(self, drawer):
        alpha_b = DimRadian(self.dim_alpha_b)
        r_ri = self.dim_r_ri
        r_ro = self.dim_r_ro
        r_f1 = self.dim_r_f1
        r_f2 = self.dim_r_f2
        r_f3 = self.dim_r_f3
        d_r1 = self.dim_d_r1
        d_r2 = self.dim_d_r2
        d_r3 = self.dim_d_r3
        w_b1 = self.dim_w_b1
        w_b2 = self.dim_w_b2
        w_b3 = self.dim_w_b3
        l_b1 = self.dim_l_b1
        l_b2 = self.dim_l_b2
        l_b3 = self.dim_l_b3
        l_b4 = self.dim_l_b4
        l_b5 = self.dim_l_b5
        l_b6 = self.dim_l_b6
        p = self.p

        alpha_total = DimRadian(2* np.pi / (2*p))

        # Shaft
        x1 = r_ri * np.cos(alpha_total / 2)
        y1 = r_ri * np.sin(alpha_total / 2)

        # First Flux Barrier from Center (Flux Barrier 1)

        # Bottom Point of Top Left Fillet
        x2 = r_ri + d_r1 
        y2 = (l_b4/2) - (r_f1/np.sqrt(2))
        # Top Point of Top Left Fillet
        x4 = r_ri + d_r1 + (((r_f1/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f1*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.cos(alpha_b - DimRadian(np.pi/2))
        y4 = (l_b4/2) + (((r_f1/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f1*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.sin(alpha_b - DimRadian(np.pi/2))
        # Center of Top Left Fillet 
        x3 = x2 + (r_f1/np.sqrt(2))
        y3 = (l_b4/2)
        # Top Left Point of Flux Barrier 1
        x5 = r_ri + d_r1 + l_b1 * np.cos(alpha_b - DimRadian(np.pi/2))
        y5 = (l_b4/2) + l_b1 * np.sin(alpha_b - DimRadian(np.pi/2))
        # Top Right Point of Flux Barrier 1
        x6 = r_ri + d_r1 + w_b1 + (l_b1 * np.cos(alpha_b - DimRadian(np.pi/2)))
        y6 = (l_b4/2) + l_b1 * np.sin(alpha_b - DimRadian(np.pi/2)) - (w_b1 / np.tan(alpha_b / 2))
        # Bottom Point of Top Right Fillet
        x9 = x2 + w_b1
        y9 = y2 - (w_b1 / np.tan(alpha_b / 2))
        # Cetre of Top Right Fillet
        x8 = x2 + w_b1 + (r_f1/np.sqrt(2))
        y8 = (l_b4/2) - (w_b1 / np.tan(alpha_b / 2))
        # Top Point of Top Right Fillet
        x7 = x4 + w_b1 
        y7 = y4  - (w_b1 / np.tan(alpha_b / 2))

        # Second Flux Barrier from Center (Flux Barrier 2)

        # Bottom Point of Top Left Fillet
        x10 = r_ri + d_r1 + w_b1 + d_r2
        y10 = (l_b5/2) - (r_f2/np.sqrt(2))
        # Top Point of Top Left Fillet
        x12 = r_ri + d_r1 + w_b1 + d_r2 + (((r_f2/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f2*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.cos(alpha_b - DimRadian(np.pi/2))
        y12 = (l_b5/2) + (((r_f2/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f2*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.sin(alpha_b - DimRadian(np.pi/2))
        # Center of Top Left fillet
        x11 = x10 + (r_f2/np.sqrt(2))
        y11 = (l_b5/2)
        # Top Left Point of Flux Barrier 2
        x13 = r_ri + d_r1 + w_b1 + d_r2 + l_b2 * np.cos(alpha_b - DimRadian(np.pi/2))
        y13 = (l_b5/2) + l_b2 * np.sin(alpha_b - DimRadian(np.pi/2))
        # Top Right Point of Flux Barrier 2
        x14 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + (l_b2 * np.cos(alpha_b - DimRadian(np.pi/2)))
        y14 = (l_b5/2) + l_b2 * np.sin(alpha_b - DimRadian(np.pi/2)) - (w_b2 / np.tan(alpha_b / 2))
        # Bottom Point of Top Right Fillet
        x17 = x10 + w_b2
        y17 = y10 - (w_b2 / np.tan(alpha_b / 2))
        # Cetre of Top Right Fillet
        x16 = x10 + w_b2 + (r_f2/np.sqrt(2))
        y16 = (l_b5/2) - (w_b2 / np.tan(alpha_b / 2))
        # Top Point of Top Right Fillet
        x15 = x12 + w_b2 
        y15 = y12  - (w_b2 / np.tan(alpha_b / 2))

        # Third Flux Barrier from Center (Flux Barrier 3)

        # Bottom Point of Top Left Fillet
        x18 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 
        y18 = (l_b6/2) - (r_f3/np.sqrt(2)) 
        # Top Point of Top Left Fillet
        x20 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 + (((r_f3/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f3*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.cos(alpha_b - DimRadian(np.pi/2))
        y20 = (l_b6/2) + (((r_f3/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f3*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.sin(alpha_b - DimRadian(np.pi/2))
        # Center of Top Left Fillet
        x19 = x18 + (r_f3/np.sqrt(2))
        y19 = (l_b6/2)
        # Top Left Point of Flux Barrier 3
        x21 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 + l_b3 * np.cos(alpha_b - DimRadian(np.pi/2))
        y21 = (l_b6/2) + l_b3 * np.sin(alpha_b - DimRadian(np.pi/2))
        # Top Right Point of Flux Barrier 3
        x22 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 + w_b3 + (l_b3 * np.cos(alpha_b - DimRadian(np.pi/2)))
        y22 = (l_b6/2) + l_b3 * np.sin(alpha_b - DimRadian(np.pi/2)) - (w_b3 / np.tan(alpha_b / 2))
        # Bottom Point of Top Right Fillet
        x25 = x18 + w_b3
        y25 = y18 - (w_b3 / np.tan(alpha_b / 2))
        # Cetre of Top Right Fillet
        x24 = x18 + w_b3 + (r_f3/np.sqrt(2))
        y24 = (l_b6/2) - (w_b3 / np.tan(alpha_b / 2))
        # Top Point of Top Right Fillet
        x23 = x20 + w_b3 
        y23 = y20  - (w_b3 / np.tan(alpha_b / 2))

        # Rotor Outer Surface
        x26 = r_ro * np.cos(alpha_total / 2)
        y26 = r_ro * np.sin(alpha_total / 2)

        # Arc Center for Flux Barriers
        x27 = (x5+x6)/2 #1st
        y27 = (y5+y6)/2
        x28 = (x13+x14)/2 #2nd
        y28 = (y13+y14)/2
        x29 = (x21+x22)/2 #3rd
        y29 = (y21+y22)/2

        x_arr = [x1,x1,x2,x2,x3,x3,x4,x4,x5,x5,x6,x6,x7,x7,x8,x8,x9,x9,x27,x27,x26,x26,x10,x10,x11,x11,x12,x12,x13,x13,x14,x14,x15,x15,x16,x16,x17,x17,x28,x28,x18,x18,x19,x19,x20,x20,x21,x21,x22,x22,x23,x23,x24,x24,x25,x25,x29,x29]
        y_arr = [-y1,y1,-y2,y2,-y3,y3,-y4,y4,-y5,y5,-y6,y6,-y7,y7,-y8,y8,-y9,y9,-y27,y27,-y26,y26,-y10,y10,-y11,y11,-y12,y12,-y13,y13,-y14,y14,-y15,y15,-y16,y16,-y17,y17,-y28,y28,-y18,y18,-y19,y19,-y20,y20,-y21,y21,-y22,y22,-y23,y23,-y24,y24,-y25,y25,-y29,y29]

        arc1 = []
        arc2 = []
        arc3 = []
        arc4 = []
        arc5 = []
        arc6 = []
        arc7 = []
        arc8 = []
        arc9 = []
        arc10 = []
        arc11 = []
        arc12 = []
        arc13 = []
        arc14 = []
        arc15 = []
        arc16 = []
        arc17 = []
        arc18 = []
        arc19 = []
        arc20 = []
        seg1 = []
        seg2 = []
        seg3 = []
        seg4 = []
        seg5 = []
        seg6 = []
        seg7 = []
        seg8 = []
        seg9 = []
        seg10 = []
        seg11 = []
        seg12 = []
        seg13 = []
        seg14 = []
        seg15 = []
        seg16 = []
        seg17 = []
        seg18 = []

        # transpose list
        coords = [x_arr, y_arr]
        coords = list(zip(*coords))
        coords = [list(sublist) for sublist in coords]

        for i in range(0, (2*p)):
            po = self.location.transform_coords(coords, alpha_total * i)
            
            # Shaft
            arc1.append(drawer.draw_arc(self.location.anchor_xy, po[0], po[1]))
            
            # Flux Barrier 1
            seg1.append(drawer.draw_line(po[2], po[3]))
            arc2.append(drawer.draw_arc(po[5], po[7], po[3]))
            seg2.append(drawer.draw_line(po[7], po[9]))
            arc3.append(drawer.draw_arc(po[19], po[11], po[9]))
            seg3.append(drawer.draw_line(po[11], po[13]))
            arc4.append(drawer.draw_arc(po[15], po[13], po[17]))
            seg4.append(drawer.draw_line(po[17], po[16]))
            arc5.append(drawer.draw_arc(po[14], po[16], po[12]))
            seg5.append(drawer.draw_line(po[12], po[10]))
            arc6.append(drawer.draw_arc(po[18], po[8], po[10]))
            seg6.append(drawer.draw_line(po[8], po[6]))
            arc7.append(drawer.draw_arc(po[4], po[2], po[6]))

            # Flux Barrier 2
            seg7.append(drawer.draw_line(po[22], po[23]))
            arc9.append(drawer.draw_arc(po[25], po[27], po[23]))
            seg8.append(drawer.draw_line(po[27], po[29]))
            arc10.append(drawer.draw_arc(po[39], po[31], po[29]))
            seg9.append(drawer.draw_line(po[31], po[33]))
            arc11.append(drawer.draw_arc(po[35], po[33], po[37]))
            seg10.append(drawer.draw_line(po[37], po[36]))
            arc12.append(drawer.draw_arc(po[34], po[36], po[32]))
            seg11.append(drawer.draw_line(po[32], po[30]))
            arc13.append(drawer.draw_arc(po[38], po[28], po[30]))
            seg12.append(drawer.draw_line(po[28], po[26]))
            arc14.append(drawer.draw_arc(po[24], po[22], po[26]))

            # Flux Barrier 3
            seg13.append(drawer.draw_line(po[40], po[41]))
            arc15.append(drawer.draw_arc(po[43], po[45], po[41]))
            seg14.append(drawer.draw_line(po[45], po[47]))
            arc16.append(drawer.draw_arc(po[57], po[49], po[47]))
            seg15.append(drawer.draw_line(po[49], po[51]))
            arc17.append(drawer.draw_arc(po[53], po[51], po[55]))
            seg16.append(drawer.draw_line(po[55], po[54]))
            arc18.append(drawer.draw_arc(po[52], po[54], po[50]))
            seg17.append(drawer.draw_line(po[50], po[48]))
            arc19.append(drawer.draw_arc(po[56], po[46], po[48]))
            seg18.append(drawer.draw_line(po[46], po[44]))
            arc20.append(drawer.draw_arc(po[42], po[40], po[44]))
            
            # Rotor Outer Surface
            arc8.append(drawer.draw_arc(self.location.anchor_xy, po[20], po[21]))
                        
        rad = (r_ri + d_r1/2)
        inner_coord = self.location.transform_coords([[rad, 0]])
        segments = [arc1,seg1,arc2,seg2,arc3,seg3,arc4,seg4,arc5,seg5,arc6,seg6,arc7,arc8,seg7,seg8,seg9,seg10,seg11,seg12,arc9,arc10,arc11,arc12,arc13,arc14,arc15,arc16,arc17,arc18,arc19,arc20,seg13,seg14,seg15,seg16,seg17,seg18]
        segs = [x for segment in segments for x in segment]
        cs_token = CrossSectToken(inner_coord[0], segs)  # create CrossSectToken object
        return cs_token

    def _validate_attr(self):

        if not isinstance(self._dim_alpha_b, DimAngular):
            raise TypeError('dim_alpha_b is not of DimAngular')

        if not isinstance(self._dim_r_ri, DimLinear):
            raise TypeError('dim_r_ri is not of DimLinear')

        if not isinstance(self._dim_r_ro, DimLinear):
            raise TypeError('dim_r_ro is not of DimLinear')

        if not isinstance(self._dim_r_f1, DimLinear):
            raise TypeError('dim_r_f1 is not of DimLinear')

        if not isinstance(self._dim_r_f2, DimLinear):
            raise TypeError('dim_r_f2 is not of DimLinear')

        if not isinstance(self._dim_r_f3, DimLinear):
            raise TypeError('dim_r_f3 is not of DimLinear')

        if not isinstance(self._dim_d_r1, DimLinear):
            raise TypeError('dim_d_r1 is not of DimLinear')

        if not isinstance(self._dim_d_r2, DimLinear):
            raise TypeError('dim_d_r2 is not of DimLinear')

        if not isinstance(self._dim_d_r3, DimLinear):
            raise TypeError('dim_d_r3 is not of DimLinear')

        if not isinstance(self._dim_w_b1, DimLinear):
            raise TypeError('dim_w_b1 is not of DimLinear')

        if not isinstance(self._dim_w_b2, DimLinear):
            raise TypeError('dim_w_b2 is not of DimLinear')

        if not isinstance(self._dim_w_b3, DimLinear):
            raise TypeError('dim_w_b3 is not of DimLinear')

        if not isinstance(self._dim_l_b1, DimLinear):
            raise TypeError('dim_l_b1 is not of DimLinear')

        if not isinstance(self._dim_l_b2, DimLinear):
            raise TypeError('dim_l_b2 is not of DimLinear')

        if not isinstance(self._dim_l_b3, DimLinear):
            raise TypeError('dim_l_b3 is not of DimLinear')

        if not isinstance(self._dim_l_b4, DimLinear):
            raise TypeError('dim_l_b4 is not of DimLinear')

        if not isinstance(self._dim_l_b5, DimLinear):
            raise TypeError('dim_l_b5 is not of DimLinear')

        if not isinstance(self._dim_l_b6, DimLinear):
            raise TypeError('dim_l_b6 is not of DimLinear')

        if not isinstance(self._p, int):
            raise TypeError('p is not of int')

class CrossSectFluxBarrierRotorPartial(CrossSectBase):
    def __init__(self, **kwargs: any) -> None:
        '''
        Initialization function for Flux Barrier Rotor class. This function takes in
        arguments and saves the information passed to private variable to make
        them read-only
        Parameters
        ----------
        **kwargs : any
            DESCRIPTION. Keyword arguments provided to the initialization function.
            The following argument names have to be included in order for the code
            to execute: name, dim_l, dim_t, dim_theta, location.
        Returns
        -------
        None
        '''
        self._create_attr(kwargs)

        super()._validate_attr()
        self._validate_attr()

    @property
    def dim_alpha_b(self):
        return self._dim_alpha_b
    
    @property
    def dim_r_ri(self):
        return self._dim_r_ri

    @property
    def dim_r_ro(self):
        return self._dim_r_ro

    @property
    def dim_r_f1(self):
        return self._dim_r_f1

    @property
    def dim_r_f2(self):
        return self._dim_r_f2

    @property
    def dim_r_f3(self):
        return self._dim_r_f3

    @property
    def dim_d_r1(self):
        return self._dim_d_r1

    @property
    def dim_d_r2(self):
        return self._dim_d_r2

    @property
    def dim_d_r3(self):
        return self._dim_d_r3

    @property
    def dim_w_b1(self):
        return self._dim_w_b1

    @property
    def dim_w_b2(self):
        return self._dim_w_b2

    @property
    def dim_w_b3(self):
        return self._dim_w_b3

    @property
    def dim_l_b1(self):
        return self._dim_l_b1

    @property
    def dim_l_b2(self):
        return self._dim_l_b2

    @property
    def dim_l_b3(self):
        return self._dim_l_b3

    @property
    def dim_l_b4(self):
        return self._dim_l_b4

    @property
    def dim_l_b5(self):
        return self._dim_l_b5

    @property
    def dim_l_b6(self):
        return self._dim_l_b6

    @property
    def p(self):
        return self._p

    def draw(self, drawer):
        alpha_b = DimRadian(self.dim_alpha_b)
        r_ri = self.dim_r_ri
        r_ro = self.dim_r_ro
        r_f1 = self.dim_r_f1
        r_f2 = self.dim_r_f2
        r_f3 = self.dim_r_f3
        d_r1 = self.dim_d_r1
        d_r2 = self.dim_d_r2
        d_r3 = self.dim_d_r3
        w_b1 = self.dim_w_b1
        w_b2 = self.dim_w_b2
        w_b3 = self.dim_w_b3
        l_b1 = self.dim_l_b1
        l_b2 = self.dim_l_b2
        l_b3 = self.dim_l_b3
        l_b4 = self.dim_l_b4
        l_b5 = self.dim_l_b5
        l_b6 = self.dim_l_b6
        p = self.p

        alpha_total = DimRadian(2* np.pi / (2*p))

        # Shaft
        x1 = r_ri * np.cos(alpha_total / 2)
        y1 = r_ri * np.sin(alpha_total / 2)

        # First Flux Barrier from Center (Flux Barrier 1)

        # Bottom Point of Top Left Fillet
        x2 = r_ri + d_r1 
        y2 = (l_b4/2) - (r_f1/np.sqrt(2))
        # Top Point of Top Left Fillet
        x4 = r_ri + d_r1 + (((r_f1/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f1*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.cos(alpha_b - DimRadian(np.pi/2))
        y4 = (l_b4/2) + (((r_f1/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f1*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.sin(alpha_b - DimRadian(np.pi/2))
        # Center of Top Left Fillet 
        x3 = x2 + (r_f1/np.sqrt(2))
        y3 = (l_b4/2)
        # Top Left Point of Flux Barrier 1
        x5 = r_ri + d_r1 + l_b1 * np.cos(alpha_b - DimRadian(np.pi/2))
        y5 = (l_b4/2) + l_b1 * np.sin(alpha_b - DimRadian(np.pi/2))
        # Top Right Point of Flux Barrier 1
        x6 = r_ri + d_r1 + w_b1 + (l_b1 * np.cos(alpha_b - DimRadian(np.pi/2)))
        y6 = (l_b4/2) + l_b1 * np.sin(alpha_b - DimRadian(np.pi/2)) - (w_b1 / np.tan(alpha_b / 2))
        # Bottom Point of Top Right Fillet
        x9 = x2 + w_b1
        y9 = y2 - (w_b1 / np.tan(alpha_b / 2))
        # Cetre of Top Right Fillet
        x8 = x2 + w_b1 + (r_f1/np.sqrt(2))
        y8 = (l_b4/2) - (w_b1 / np.tan(alpha_b / 2))
        # Top Point of Top Right Fillet
        x7 = x4 + w_b1 
        y7 = y4  - (w_b1 / np.tan(alpha_b / 2))

        # Second Flux Barrier from Center (Flux Barrier 2)

        # Bottom Point of Top Left Fillet
        x10 = r_ri + d_r1 + w_b1 + d_r2
        y10 = (l_b5/2) - (r_f2/np.sqrt(2))
        # Top Point of Top Left Fillet
        x12 = r_ri + d_r1 + w_b1 + d_r2 + (((r_f2/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f2*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.cos(alpha_b - DimRadian(np.pi/2))
        y12 = (l_b5/2) + (((r_f2/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f2*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.sin(alpha_b - DimRadian(np.pi/2))
        # Center of Top Left fillet
        x11 = x10 + (r_f2/np.sqrt(2))
        y11 = (l_b5/2)
        # Top Left Point of Flux Barrier 2
        x13 = r_ri + d_r1 + w_b1 + d_r2 + l_b2 * np.cos(alpha_b - DimRadian(np.pi/2))
        y13 = (l_b5/2) + l_b2 * np.sin(alpha_b - DimRadian(np.pi/2))
        # Top Right Point of Flux Barrier 2
        x14 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + (l_b2 * np.cos(alpha_b - DimRadian(np.pi/2)))
        y14 = (l_b5/2) + l_b2 * np.sin(alpha_b - DimRadian(np.pi/2)) - (w_b2 / np.tan(alpha_b / 2))
        # Bottom Point of Top Right Fillet
        x17 = x10 + w_b2
        y17 = y10 - (w_b2 / np.tan(alpha_b / 2))
        # Cetre of Top Right Fillet
        x16 = x10 + w_b2 + (r_f2/np.sqrt(2))
        y16 = (l_b5/2) - (w_b2 / np.tan(alpha_b / 2))
        # Top Point of Top Right Fillet
        x15 = x12 + w_b2 
        y15 = y12  - (w_b2 / np.tan(alpha_b / 2))

        # Third Flux Barrier from Center (Flux Barrier 3)

        # Bottom Point of Top Left Fillet
        x18 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 
        y18 = (l_b6/2) - (r_f3/np.sqrt(2)) 
        # Top Point of Top Left Fillet
        x20 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 + (((r_f3/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f3*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.cos(alpha_b - DimRadian(np.pi/2))
        y20 = (l_b6/2) + (((r_f3/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f3*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.sin(alpha_b - DimRadian(np.pi/2))
        # Center of Top Left Fillet
        x19 = x18 + (r_f3/np.sqrt(2))
        y19 = (l_b6/2)
        # Top Left Point of Flux Barrier 3
        x21 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 + l_b3 * np.cos(alpha_b - DimRadian(np.pi/2))
        y21 = (l_b6/2) + l_b3 * np.sin(alpha_b - DimRadian(np.pi/2))
        # Top Right Point of Flux Barrier 3
        x22 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 + w_b3 + (l_b3 * np.cos(alpha_b - DimRadian(np.pi/2)))
        y22 = (l_b6/2) + l_b3 * np.sin(alpha_b - DimRadian(np.pi/2)) - (w_b3 / np.tan(alpha_b / 2))
        # Bottom Point of Top Right Fillet
        x25 = x18 + w_b3
        y25 = y18 - (w_b3 / np.tan(alpha_b / 2))
        # Cetre of Top Right Fillet
        x24 = x18 + w_b3 + (r_f3/np.sqrt(2))
        y24 = (l_b6/2) - (w_b3 / np.tan(alpha_b / 2))
        # Top Point of Top Right Fillet
        x23 = x20 + w_b3 
        y23 = y20  - (w_b3 / np.tan(alpha_b / 2))

        # Rotor Outer Surface
        x26 = r_ro * np.cos(alpha_total / 2)
        y26 = r_ro * np.sin(alpha_total / 2)

        # Arc Center for Flux Barriers
        x27 = (x5+x6)/2 #1st
        y27 = (y5+y6)/2
        x28 = (x13+x14)/2 #2nd
        y28 = (y13+y14)/2
        x29 = (x21+x22)/2 #3rd
        y29 = (y21+y22)/2

        x_arr = [x1,x1,x2,x2,x3,x3,x4,x4,x5,x5,x6,x6,x7,x7,x8,x8,x9,x9,x27,x27,x26,x26,x10,x10,x11,x11,x12,x12,x13,x13,x14,x14,x15,x15,x16,x16,x17,x17,x28,x28,x18,x18,x19,x19,x20,x20,x21,x21,x22,x22,x23,x23,x24,x24,x25,x25,x29,x29]
        y_arr = [-y1,y1,-y2,y2,-y3,y3,-y4,y4,-y5,y5,-y6,y6,-y7,y7,-y8,y8,-y9,y9,-y27,y27,-y26,y26,-y10,y10,-y11,y11,-y12,y12,-y13,y13,-y14,y14,-y15,y15,-y16,y16,-y17,y17,-y28,y28,-y18,y18,-y19,y19,-y20,y20,-y21,y21,-y22,y22,-y23,y23,-y24,y24,-y25,y25,-y29,y29]

        arc1 = []
        arc2 = []
        arc3 = []
        arc4 = []
        arc5 = []
        arc6 = []
        arc7 = []
        arc8 = []
        arc9 = []
        arc10 = []
        arc11 = []
        arc12 = []
        arc13 = []
        arc14 = []
        arc15 = []
        arc16 = []
        arc17 = []
        arc18 = []
        arc19 = []
        arc20 = []
        seg1 = []
        seg2 = []
        seg3 = []
        seg4 = []
        seg5 = []
        seg6 = []
        seg7 = []
        seg8 = []
        seg9 = []
        seg10 = []
        seg11 = []
        seg12 = []
        seg13 = []
        seg14 = []
        seg15 = []
        seg16 = []
        seg17 = []
        seg18 = []
        seg19 = []
        seg20 = []

        # transpose list
        coords = [x_arr, y_arr]
        coords = list(zip(*coords))
        coords = [list(sublist) for sublist in coords]

        for i in range(0, 1):
            po = self.location.transform_coords(coords, alpha_total * i)
            
            # Shaft
            arc1.append(drawer.draw_arc(self.location.anchor_xy, po[0], po[1]))
            
            # Flux Barrier 1
            seg1.append(drawer.draw_line(po[2], po[3]))
            arc2.append(drawer.draw_arc(po[5], po[7], po[3]))
            seg2.append(drawer.draw_line(po[7], po[9]))
            arc3.append(drawer.draw_arc(po[19], po[11], po[9]))
            seg3.append(drawer.draw_line(po[11], po[13]))
            arc4.append(drawer.draw_arc(po[15], po[13], po[17]))
            seg4.append(drawer.draw_line(po[17], po[16]))
            arc5.append(drawer.draw_arc(po[14], po[16], po[12]))
            seg5.append(drawer.draw_line(po[12], po[10]))
            arc6.append(drawer.draw_arc(po[18], po[8], po[10]))
            seg6.append(drawer.draw_line(po[8], po[6]))
            arc7.append(drawer.draw_arc(po[4], po[2], po[6]))

            # Flux Barrier 2
            seg7.append(drawer.draw_line(po[22], po[23]))
            arc9.append(drawer.draw_arc(po[25], po[27], po[23]))
            seg8.append(drawer.draw_line(po[27], po[29]))
            arc10.append(drawer.draw_arc(po[39], po[31], po[29]))
            seg9.append(drawer.draw_line(po[31], po[33]))
            arc11.append(drawer.draw_arc(po[35], po[33], po[37]))
            seg10.append(drawer.draw_line(po[37], po[36]))
            arc12.append(drawer.draw_arc(po[34], po[36], po[32]))
            seg11.append(drawer.draw_line(po[32], po[30]))
            arc13.append(drawer.draw_arc(po[38], po[28], po[30]))
            seg12.append(drawer.draw_line(po[28], po[26]))
            arc14.append(drawer.draw_arc(po[24], po[22], po[26]))

            # Flux Barrier 3
            seg13.append(drawer.draw_line(po[40], po[41]))
            arc15.append(drawer.draw_arc(po[43], po[45], po[41]))
            seg14.append(drawer.draw_line(po[45], po[47]))
            arc16.append(drawer.draw_arc(po[57], po[49], po[47]))
            seg15.append(drawer.draw_line(po[49], po[51]))
            arc17.append(drawer.draw_arc(po[53], po[51], po[55]))
            seg16.append(drawer.draw_line(po[55], po[54]))
            arc18.append(drawer.draw_arc(po[52], po[54], po[50]))
            seg17.append(drawer.draw_line(po[50], po[48]))
            arc19.append(drawer.draw_arc(po[56], po[46], po[48]))
            seg18.append(drawer.draw_line(po[46], po[44]))
            arc20.append(drawer.draw_arc(po[42], po[40], po[44]))
            
            # Rotor Outer Surface
            arc8.append(drawer.draw_arc(self.location.anchor_xy, po[20], po[21]))

            # Close Shaft and Rotor Outer Surface
            seg19.append(drawer.draw_line(po[0], po[20]))
            seg20.append(drawer.draw_line(po[1], po[21]))
                        
        rad = (r_ri + d_r1/2)
        inner_coord = self.location.transform_coords([[rad, 0]])
        segments = [arc1,seg1,arc2,seg2,arc3,seg3,arc4,seg4,arc5,seg5,arc6,seg6,arc7,arc8,seg7,seg8,seg9,seg10,seg11,seg12,arc9,arc10,arc11,arc12,arc13,arc14,arc15,arc16,arc17,arc18,arc19,arc20,seg13,seg14,seg15,seg16,seg17,seg18,seg19,seg20]
        segs = [x for segment in segments for x in segment]
        cs_token = CrossSectToken(inner_coord[0], segs)  # create CrossSectToken object
        return cs_token

    def _validate_attr(self):

        if not isinstance(self._dim_alpha_b, DimAngular):
            raise TypeError('dim_alpha_b is not of DimAngular')

        if not isinstance(self._dim_r_ri, DimLinear):
            raise TypeError('dim_r_ri is not of DimLinear')

        if not isinstance(self._dim_r_ro, DimLinear):
            raise TypeError('dim_r_ro is not of DimLinear')

        if not isinstance(self._dim_r_f1, DimLinear):
            raise TypeError('dim_r_f1 is not of DimLinear')

        if not isinstance(self._dim_r_f2, DimLinear):
            raise TypeError('dim_r_f2 is not of DimLinear')

        if not isinstance(self._dim_r_f3, DimLinear):
            raise TypeError('dim_r_f3 is not of DimLinear')

        if not isinstance(self._dim_d_r1, DimLinear):
            raise TypeError('dim_d_r1 is not of DimLinear')

        if not isinstance(self._dim_d_r2, DimLinear):
            raise TypeError('dim_d_r2 is not of DimLinear')

        if not isinstance(self._dim_d_r3, DimLinear):
            raise TypeError('dim_d_r3 is not of DimLinear')

        if not isinstance(self._dim_w_b1, DimLinear):
            raise TypeError('dim_w_b1 is not of DimLinear')

        if not isinstance(self._dim_w_b2, DimLinear):
            raise TypeError('dim_w_b2 is not of DimLinear')

        if not isinstance(self._dim_w_b3, DimLinear):
            raise TypeError('dim_w_b3 is not of DimLinear')

        if not isinstance(self._dim_l_b1, DimLinear):
            raise TypeError('dim_l_b1 is not of DimLinear')

        if not isinstance(self._dim_l_b2, DimLinear):
            raise TypeError('dim_l_b2 is not of DimLinear')

        if not isinstance(self._dim_l_b3, DimLinear):
            raise TypeError('dim_l_b3 is not of DimLinear')

        if not isinstance(self._dim_l_b4, DimLinear):
            raise TypeError('dim_l_b4 is not of DimLinear')

        if not isinstance(self._dim_l_b5, DimLinear):
            raise TypeError('dim_l_b5 is not of DimLinear')

        if not isinstance(self._dim_l_b6, DimLinear):
            raise TypeError('dim_l_b6 is not of DimLinear')

        if not isinstance(self._p, int):
            raise TypeError('p is not of int')
        

class CrossSectFluxBarrierRotorPartialBarrier1(CrossSectBase):
    def __init__(self, **kwargs: any) -> None:
        '''
        Initialization function for Flux Barrier Rotor class. This function takes in
        arguments and saves the information passed to private variable to make
        them read-only
        Parameters
        ----------
        **kwargs : any
            DESCRIPTION. Keyword arguments provided to the initialization function.
            The following argument names have to be included in order for the code
            to execute: name, dim_l, dim_t, dim_theta, location.
        Returns
        -------
        None
        '''
        self._create_attr(kwargs)

        super()._validate_attr()
        self._validate_attr()

    @property
    def dim_alpha_b(self):
        return self._dim_alpha_b
    
    @property
    def dim_r_ri(self):
        return self._dim_r_ri

    @property
    def dim_r_ro(self):
        return self._dim_r_ro

    @property
    def dim_r_f1(self):
        return self._dim_r_f1

    @property
    def dim_r_f2(self):
        return self._dim_r_f2

    @property
    def dim_r_f3(self):
        return self._dim_r_f3

    @property
    def dim_d_r1(self):
        return self._dim_d_r1

    @property
    def dim_d_r2(self):
        return self._dim_d_r2

    @property
    def dim_d_r3(self):
        return self._dim_d_r3

    @property
    def dim_w_b1(self):
        return self._dim_w_b1

    @property
    def dim_w_b2(self):
        return self._dim_w_b2

    @property
    def dim_w_b3(self):
        return self._dim_w_b3

    @property
    def dim_l_b1(self):
        return self._dim_l_b1

    @property
    def dim_l_b2(self):
        return self._dim_l_b2

    @property
    def dim_l_b3(self):
        return self._dim_l_b3

    @property
    def dim_l_b4(self):
        return self._dim_l_b4

    @property
    def dim_l_b5(self):
        return self._dim_l_b5

    @property
    def dim_l_b6(self):
        return self._dim_l_b6

    @property
    def p(self):
        return self._p

    def draw(self, drawer):
        alpha_b = DimRadian(self.dim_alpha_b)
        r_ri = self.dim_r_ri
        r_ro = self.dim_r_ro
        r_f1 = self.dim_r_f1
        r_f2 = self.dim_r_f2
        r_f3 = self.dim_r_f3
        d_r1 = self.dim_d_r1
        d_r2 = self.dim_d_r2
        d_r3 = self.dim_d_r3
        w_b1 = self.dim_w_b1
        w_b2 = self.dim_w_b2
        w_b3 = self.dim_w_b3
        l_b1 = self.dim_l_b1
        l_b2 = self.dim_l_b2
        l_b3 = self.dim_l_b3
        l_b4 = self.dim_l_b4
        l_b5 = self.dim_l_b5
        l_b6 = self.dim_l_b6
        p = self.p

        alpha_total = DimRadian(2* np.pi / (2*p))

        # Shaft
        x1 = r_ri * np.cos(alpha_total / 2)
        y1 = r_ri * np.sin(alpha_total / 2)

        # First Flux Barrier from Center (Flux Barrier 1)

        # Bottom Point of Top Left Fillet
        x2 = r_ri + d_r1 
        y2 = (l_b4/2) - (r_f1/np.sqrt(2))
        # Top Point of Top Left Fillet
        x4 = r_ri + d_r1 + (((r_f1/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f1*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.cos(alpha_b - DimRadian(np.pi/2))
        y4 = (l_b4/2) + (((r_f1/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f1*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.sin(alpha_b - DimRadian(np.pi/2))
        # Center of Top Left Fillet 
        x3 = x2 + (r_f1/np.sqrt(2))
        y3 = (l_b4/2)
        # Top Left Point of Flux Barrier 1
        x5 = r_ri + d_r1 + l_b1 * np.cos(alpha_b - DimRadian(np.pi/2))
        y5 = (l_b4/2) + l_b1 * np.sin(alpha_b - DimRadian(np.pi/2))
        # Top Right Point of Flux Barrier 1
        x6 = r_ri + d_r1 + w_b1 + (l_b1 * np.cos(alpha_b - DimRadian(np.pi/2)))
        y6 = (l_b4/2) + l_b1 * np.sin(alpha_b - DimRadian(np.pi/2)) - (w_b1 / np.tan(alpha_b / 2))
        # Bottom Point of Top Right Fillet
        x9 = x2 + w_b1
        y9 = y2 - (w_b1 / np.tan(alpha_b / 2))
        # Cetre of Top Right Fillet
        x8 = x2 + w_b1 + (r_f1/np.sqrt(2))
        y8 = (l_b4/2) - (w_b1 / np.tan(alpha_b / 2))
        # Top Point of Top Right Fillet
        x7 = x4 + w_b1 
        y7 = y4  - (w_b1 / np.tan(alpha_b / 2))

        # Second Flux Barrier from Center (Flux Barrier 2)

        # Bottom Point of Top Left Fillet
        x10 = r_ri + d_r1 + w_b1 + d_r2
        y10 = (l_b5/2) - (r_f2/np.sqrt(2))
        # Top Point of Top Left Fillet
        x12 = r_ri + d_r1 + w_b1 + d_r2 + (((r_f2/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f2*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.cos(alpha_b - DimRadian(np.pi/2))
        y12 = (l_b5/2) + (((r_f2/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f2*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.sin(alpha_b - DimRadian(np.pi/2))
        # Center of Top Left fillet
        x11 = x10 + (r_f2/np.sqrt(2))
        y11 = (l_b5/2)
        # Top Left Point of Flux Barrier 2
        x13 = r_ri + d_r1 + w_b1 + d_r2 + l_b2 * np.cos(alpha_b - DimRadian(np.pi/2))
        y13 = (l_b5/2) + l_b2 * np.sin(alpha_b - DimRadian(np.pi/2))
        # Top Right Point of Flux Barrier 2
        x14 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + (l_b2 * np.cos(alpha_b - DimRadian(np.pi/2)))
        y14 = (l_b5/2) + l_b2 * np.sin(alpha_b - DimRadian(np.pi/2)) - (w_b2 / np.tan(alpha_b / 2))
        # Bottom Point of Top Right Fillet
        x17 = x10 + w_b2
        y17 = y10 - (w_b2 / np.tan(alpha_b / 2))
        # Cetre of Top Right Fillet
        x16 = x10 + w_b2 + (r_f2/np.sqrt(2))
        y16 = (l_b5/2) - (w_b2 / np.tan(alpha_b / 2))
        # Top Point of Top Right Fillet
        x15 = x12 + w_b2 
        y15 = y12  - (w_b2 / np.tan(alpha_b / 2))

        # Third Flux Barrier from Center (Flux Barrier 3)

        # Bottom Point of Top Left Fillet
        x18 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 
        y18 = (l_b6/2) - (r_f3/np.sqrt(2)) 
        # Top Point of Top Left Fillet
        x20 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 + (((r_f3/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f3*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.cos(alpha_b - DimRadian(np.pi/2))
        y20 = (l_b6/2) + (((r_f3/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f3*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.sin(alpha_b - DimRadian(np.pi/2))
        # Center of Top Left Fillet
        x19 = x18 + (r_f3/np.sqrt(2))
        y19 = (l_b6/2)
        # Top Left Point of Flux Barrier 3
        x21 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 + l_b3 * np.cos(alpha_b - DimRadian(np.pi/2))
        y21 = (l_b6/2) + l_b3 * np.sin(alpha_b - DimRadian(np.pi/2))
        # Top Right Point of Flux Barrier 3
        x22 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 + w_b3 + (l_b3 * np.cos(alpha_b - DimRadian(np.pi/2)))
        y22 = (l_b6/2) + l_b3 * np.sin(alpha_b - DimRadian(np.pi/2)) - (w_b3 / np.tan(alpha_b / 2))
        # Bottom Point of Top Right Fillet
        x25 = x18 + w_b3
        y25 = y18 - (w_b3 / np.tan(alpha_b / 2))
        # Cetre of Top Right Fillet
        x24 = x18 + w_b3 + (r_f3/np.sqrt(2))
        y24 = (l_b6/2) - (w_b3 / np.tan(alpha_b / 2))
        # Top Point of Top Right Fillet
        x23 = x20 + w_b3 
        y23 = y20  - (w_b3 / np.tan(alpha_b / 2))

        # Rotor Outer Surface
        x26 = r_ro * np.cos(alpha_total / 2)
        y26 = r_ro * np.sin(alpha_total / 2)

        # Arc Center for Flux Barriers
        x27 = (x5+x6)/2 #1st
        y27 = (y5+y6)/2
        x28 = (x13+x14)/2 #2nd
        y28 = (y13+y14)/2
        x29 = (x21+x22)/2 #3rd
        y29 = (y21+y22)/2

        x_arr = [x1,x1,x2,x2,x3,x3,x4,x4,x5,x5,x6,x6,x7,x7,x8,x8,x9,x9,x27,x27,x26,x26,x10,x10,x11,x11,x12,x12,x13,x13,x14,x14,x15,x15,x16,x16,x17,x17,x28,x28,x18,x18,x19,x19,x20,x20,x21,x21,x22,x22,x23,x23,x24,x24,x25,x25,x29,x29]
        y_arr = [-y1,y1,-y2,y2,-y3,y3,-y4,y4,-y5,y5,-y6,y6,-y7,y7,-y8,y8,-y9,y9,-y27,y27,-y26,y26,-y10,y10,-y11,y11,-y12,y12,-y13,y13,-y14,y14,-y15,y15,-y16,y16,-y17,y17,-y28,y28,-y18,y18,-y19,y19,-y20,y20,-y21,y21,-y22,y22,-y23,y23,-y24,y24,-y25,y25,-y29,y29]

        arc1 = []
        arc2 = []
        arc3 = []
        arc4 = []
        arc5 = []
        arc6 = []
        arc7 = []
        arc8 = []
        arc9 = []
        arc10 = []
        arc11 = []
        arc12 = []
        arc13 = []
        arc14 = []
        arc15 = []
        arc16 = []
        arc17 = []
        arc18 = []
        arc19 = []
        arc20 = []
        seg1 = []
        seg2 = []
        seg3 = []
        seg4 = []
        seg5 = []
        seg6 = []
        seg7 = []
        seg8 = []
        seg9 = []
        seg10 = []
        seg11 = []
        seg12 = []
        seg13 = []
        seg14 = []
        seg15 = []
        seg16 = []
        seg17 = []
        seg18 = []
        seg19 = []
        seg20 = []

        # transpose list
        coords = [x_arr, y_arr]
        coords = list(zip(*coords))
        coords = [list(sublist) for sublist in coords]

        for i in range(0, 1):
            po = self.location.transform_coords(coords, alpha_total * i)
            
            # Shaft
            # arc1.append(drawer.draw_arc(self.location.anchor_xy, po[0], po[1]))
            
            # Flux Barrier 1
            seg1.append(drawer.draw_line(po[2], po[3]))
            arc2.append(drawer.draw_arc(po[5], po[7], po[3]))
            seg2.append(drawer.draw_line(po[7], po[9]))
            arc3.append(drawer.draw_arc(po[19], po[11], po[9]))
            seg3.append(drawer.draw_line(po[11], po[13]))
            arc4.append(drawer.draw_arc(po[15], po[13], po[17]))
            seg4.append(drawer.draw_line(po[17], po[16]))
            arc5.append(drawer.draw_arc(po[14], po[16], po[12]))
            seg5.append(drawer.draw_line(po[12], po[10]))
            arc6.append(drawer.draw_arc(po[18], po[8], po[10]))
            seg6.append(drawer.draw_line(po[8], po[6]))
            arc7.append(drawer.draw_arc(po[4], po[2], po[6]))

            # Flux Barrier 2
            #seg7.append(drawer.draw_line(po[22], po[23]))
            #arc9.append(drawer.draw_arc(po[25], po[27], po[23]))
            #seg8.append(drawer.draw_line(po[27], po[29]))
            #arc10.append(drawer.draw_arc(po[39], po[31], po[29]))
            #seg9.append(drawer.draw_line(po[31], po[33]))
            #arc11.append(drawer.draw_arc(po[35], po[33], po[37]))
            #seg10.append(drawer.draw_line(po[37], po[36]))
            #arc12.append(drawer.draw_arc(po[34], po[36], po[32]))
            #seg11.append(drawer.draw_line(po[32], po[30]))
            #arc13.append(drawer.draw_arc(po[38], po[28], po[30]))
            #seg12.append(drawer.draw_line(po[28], po[26]))
            #arc14.append(drawer.draw_arc(po[24], po[22], po[26]))

            # Flux Barrier 3
            #seg13.append(drawer.draw_line(po[40], po[41]))
            #arc15.append(drawer.draw_arc(po[43], po[45], po[41]))
            #seg14.append(drawer.draw_line(po[45], po[47]))
            #arc16.append(drawer.draw_arc(po[57], po[49], po[47]))
            #seg15.append(drawer.draw_line(po[49], po[51]))
            #arc17.append(drawer.draw_arc(po[53], po[51], po[55]))
            #seg16.append(drawer.draw_line(po[55], po[54]))
            #arc18.append(drawer.draw_arc(po[52], po[54], po[50]))
            #seg17.append(drawer.draw_line(po[50], po[48]))
            #arc19.append(drawer.draw_arc(po[56], po[46], po[48]))
            #seg18.append(drawer.draw_line(po[46], po[44]))
            #arc20.append(drawer.draw_arc(po[42], po[40], po[44]))
            
            # Rotor Outer Surface
            #arc8.append(drawer.draw_arc(self.location.anchor_xy, po[20], po[21]))

            # Close Shaft and Rotor Outer Surface
            #seg19.append(drawer.draw_line(po[0], po[20]))
            #seg20.append(drawer.draw_line(po[1], po[21]))
                        
        rad = (r_ri + d_r1 + w_b1/2)
        inner_coord = self.location.transform_coords([[rad, 0]])
        segments = [arc1,seg1,arc2,seg2,arc3,seg3,arc4,seg4,arc5,seg5,arc6,seg6,arc7,arc8,seg7,seg8,seg9,seg10,seg11,seg12,arc9,arc10,arc11,arc12,arc13,arc14,arc15,arc16,arc17,arc18,arc19,arc20,seg13,seg14,seg15,seg16,seg17,seg18,seg19,seg20]
        segs = [x for segment in segments for x in segment]
        cs_token = CrossSectToken(inner_coord[0], segs)  # create CrossSectToken object
        return cs_token

    def _validate_attr(self):

        if not isinstance(self._dim_alpha_b, DimAngular):
            raise TypeError('dim_alpha_b is not of DimAngular')

        if not isinstance(self._dim_r_ri, DimLinear):
            raise TypeError('dim_r_ri is not of DimLinear')

        if not isinstance(self._dim_r_ro, DimLinear):
            raise TypeError('dim_r_ro is not of DimLinear')

        if not isinstance(self._dim_r_f1, DimLinear):
            raise TypeError('dim_r_f1 is not of DimLinear')

        if not isinstance(self._dim_r_f2, DimLinear):
            raise TypeError('dim_r_f2 is not of DimLinear')

        if not isinstance(self._dim_r_f3, DimLinear):
            raise TypeError('dim_r_f3 is not of DimLinear')

        if not isinstance(self._dim_d_r1, DimLinear):
            raise TypeError('dim_d_r1 is not of DimLinear')

        if not isinstance(self._dim_d_r2, DimLinear):
            raise TypeError('dim_d_r2 is not of DimLinear')

        if not isinstance(self._dim_d_r3, DimLinear):
            raise TypeError('dim_d_r3 is not of DimLinear')

        if not isinstance(self._dim_w_b1, DimLinear):
            raise TypeError('dim_w_b1 is not of DimLinear')

        if not isinstance(self._dim_w_b2, DimLinear):
            raise TypeError('dim_w_b2 is not of DimLinear')

        if not isinstance(self._dim_w_b3, DimLinear):
            raise TypeError('dim_w_b3 is not of DimLinear')

        if not isinstance(self._dim_l_b1, DimLinear):
            raise TypeError('dim_l_b1 is not of DimLinear')

        if not isinstance(self._dim_l_b2, DimLinear):
            raise TypeError('dim_l_b2 is not of DimLinear')

        if not isinstance(self._dim_l_b3, DimLinear):
            raise TypeError('dim_l_b3 is not of DimLinear')

        if not isinstance(self._dim_l_b4, DimLinear):
            raise TypeError('dim_l_b4 is not of DimLinear')

        if not isinstance(self._dim_l_b5, DimLinear):
            raise TypeError('dim_l_b5 is not of DimLinear')

        if not isinstance(self._dim_l_b6, DimLinear):
            raise TypeError('dim_l_b6 is not of DimLinear')

        if not isinstance(self._p, int):
            raise TypeError('p is not of int')
        

class CrossSectFluxBarrierRotorPartialBarrier2(CrossSectBase):
    def __init__(self, **kwargs: any) -> None:
        '''
        Initialization function for Flux Barrier Rotor class. This function takes in
        arguments and saves the information passed to private variable to make
        them read-only
        Parameters
        ----------
        **kwargs : any
            DESCRIPTION. Keyword arguments provided to the initialization function.
            The following argument names have to be included in order for the code
            to execute: name, dim_l, dim_t, dim_theta, location.
        Returns
        -------
        None
        '''
        self._create_attr(kwargs)

        super()._validate_attr()
        self._validate_attr()

    @property
    def dim_alpha_b(self):
        return self._dim_alpha_b
    
    @property
    def dim_r_ri(self):
        return self._dim_r_ri

    @property
    def dim_r_ro(self):
        return self._dim_r_ro

    @property
    def dim_r_f1(self):
        return self._dim_r_f1

    @property
    def dim_r_f2(self):
        return self._dim_r_f2

    @property
    def dim_r_f3(self):
        return self._dim_r_f3

    @property
    def dim_d_r1(self):
        return self._dim_d_r1

    @property
    def dim_d_r2(self):
        return self._dim_d_r2

    @property
    def dim_d_r3(self):
        return self._dim_d_r3

    @property
    def dim_w_b1(self):
        return self._dim_w_b1

    @property
    def dim_w_b2(self):
        return self._dim_w_b2

    @property
    def dim_w_b3(self):
        return self._dim_w_b3

    @property
    def dim_l_b1(self):
        return self._dim_l_b1

    @property
    def dim_l_b2(self):
        return self._dim_l_b2

    @property
    def dim_l_b3(self):
        return self._dim_l_b3

    @property
    def dim_l_b4(self):
        return self._dim_l_b4

    @property
    def dim_l_b5(self):
        return self._dim_l_b5

    @property
    def dim_l_b6(self):
        return self._dim_l_b6

    @property
    def p(self):
        return self._p

    def draw(self, drawer):
        alpha_b = DimRadian(self.dim_alpha_b)
        r_ri = self.dim_r_ri
        r_ro = self.dim_r_ro
        r_f1 = self.dim_r_f1
        r_f2 = self.dim_r_f2
        r_f3 = self.dim_r_f3
        d_r1 = self.dim_d_r1
        d_r2 = self.dim_d_r2
        d_r3 = self.dim_d_r3
        w_b1 = self.dim_w_b1
        w_b2 = self.dim_w_b2
        w_b3 = self.dim_w_b3
        l_b1 = self.dim_l_b1
        l_b2 = self.dim_l_b2
        l_b3 = self.dim_l_b3
        l_b4 = self.dim_l_b4
        l_b5 = self.dim_l_b5
        l_b6 = self.dim_l_b6
        p = self.p

        alpha_total = DimRadian(2* np.pi / (2*p))

        # Shaft
        x1 = r_ri * np.cos(alpha_total / 2)
        y1 = r_ri * np.sin(alpha_total / 2)

        # First Flux Barrier from Center (Flux Barrier 1)

        # Bottom Point of Top Left Fillet
        x2 = r_ri + d_r1 
        y2 = (l_b4/2) - (r_f1/np.sqrt(2))
        # Top Point of Top Left Fillet
        x4 = r_ri + d_r1 + (((r_f1/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f1*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.cos(alpha_b - DimRadian(np.pi/2))
        y4 = (l_b4/2) + (((r_f1/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f1*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.sin(alpha_b - DimRadian(np.pi/2))
        # Center of Top Left Fillet 
        x3 = x2 + (r_f1/np.sqrt(2))
        y3 = (l_b4/2)
        # Top Left Point of Flux Barrier 1
        x5 = r_ri + d_r1 + l_b1 * np.cos(alpha_b - DimRadian(np.pi/2))
        y5 = (l_b4/2) + l_b1 * np.sin(alpha_b - DimRadian(np.pi/2))
        # Top Right Point of Flux Barrier 1
        x6 = r_ri + d_r1 + w_b1 + (l_b1 * np.cos(alpha_b - DimRadian(np.pi/2)))
        y6 = (l_b4/2) + l_b1 * np.sin(alpha_b - DimRadian(np.pi/2)) - (w_b1 / np.tan(alpha_b / 2))
        # Bottom Point of Top Right Fillet
        x9 = x2 + w_b1
        y9 = y2 - (w_b1 / np.tan(alpha_b / 2))
        # Cetre of Top Right Fillet
        x8 = x2 + w_b1 + (r_f1/np.sqrt(2))
        y8 = (l_b4/2) - (w_b1 / np.tan(alpha_b / 2))
        # Top Point of Top Right Fillet
        x7 = x4 + w_b1 
        y7 = y4  - (w_b1 / np.tan(alpha_b / 2))

        # Second Flux Barrier from Center (Flux Barrier 2)

        # Bottom Point of Top Left Fillet
        x10 = r_ri + d_r1 + w_b1 + d_r2
        y10 = (l_b5/2) - (r_f2/np.sqrt(2))
        # Top Point of Top Left Fillet
        x12 = r_ri + d_r1 + w_b1 + d_r2 + (((r_f2/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f2*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.cos(alpha_b - DimRadian(np.pi/2))
        y12 = (l_b5/2) + (((r_f2/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f2*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.sin(alpha_b - DimRadian(np.pi/2))
        # Center of Top Left fillet
        x11 = x10 + (r_f2/np.sqrt(2))
        y11 = (l_b5/2)
        # Top Left Point of Flux Barrier 2
        x13 = r_ri + d_r1 + w_b1 + d_r2 + l_b2 * np.cos(alpha_b - DimRadian(np.pi/2))
        y13 = (l_b5/2) + l_b2 * np.sin(alpha_b - DimRadian(np.pi/2))
        # Top Right Point of Flux Barrier 2
        x14 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + (l_b2 * np.cos(alpha_b - DimRadian(np.pi/2)))
        y14 = (l_b5/2) + l_b2 * np.sin(alpha_b - DimRadian(np.pi/2)) - (w_b2 / np.tan(alpha_b / 2))
        # Bottom Point of Top Right Fillet
        x17 = x10 + w_b2
        y17 = y10 - (w_b2 / np.tan(alpha_b / 2))
        # Cetre of Top Right Fillet
        x16 = x10 + w_b2 + (r_f2/np.sqrt(2))
        y16 = (l_b5/2) - (w_b2 / np.tan(alpha_b / 2))
        # Top Point of Top Right Fillet
        x15 = x12 + w_b2 
        y15 = y12  - (w_b2 / np.tan(alpha_b / 2))

        # Third Flux Barrier from Center (Flux Barrier 3)

        # Bottom Point of Top Left Fillet
        x18 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 
        y18 = (l_b6/2) - (r_f3/np.sqrt(2)) 
        # Top Point of Top Left Fillet
        x20 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 + (((r_f3/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f3*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.cos(alpha_b - DimRadian(np.pi/2))
        y20 = (l_b6/2) + (((r_f3/np.sqrt(2))*np.cos(alpha_b - DimRadian(np.pi/2))) + (r_f3*np.sqrt(1 - 0.5*np.square(np.sin(alpha_b - DimRadian(np.pi/2))))))*np.sin(alpha_b - DimRadian(np.pi/2))
        # Center of Top Left Fillet
        x19 = x18 + (r_f3/np.sqrt(2))
        y19 = (l_b6/2)
        # Top Left Point of Flux Barrier 3
        x21 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 + l_b3 * np.cos(alpha_b - DimRadian(np.pi/2))
        y21 = (l_b6/2) + l_b3 * np.sin(alpha_b - DimRadian(np.pi/2))
        # Top Right Point of Flux Barrier 3
        x22 = r_ri + d_r1 + w_b1 + d_r2 + w_b2 + d_r3 + w_b3 + (l_b3 * np.cos(alpha_b - DimRadian(np.pi/2)))
        y22 = (l_b6/2) + l_b3 * np.sin(alpha_b - DimRadian(np.pi/2)) - (w_b3 / np.tan(alpha_b / 2))
        # Bottom Point of Top Right Fillet
        x25 = x18 + w_b3
        y25 = y18 - (w_b3 / np.tan(alpha_b / 2))
        # Cetre of Top Right Fillet
        x24 = x18 + w_b3 + (r_f3/np.sqrt(2))
        y24 = (l_b6/2) - (w_b3 / np.tan(alpha_b / 2))
        # Top Point of Top Right Fillet
        x23 = x20 + w_b3 
        y23 = y20  - (w_b3 / np.tan(alpha_b / 2))

        # Rotor Outer Surface
        x26 = r_ro * np.cos(alpha_total / 2)
        y26 = r_ro * np.sin(alpha_total / 2)

        # Arc Center for Flux Barriers
        x27 = (x5+x6)/2 #1st
        y27 = (y5+y6)/2
        x28 = (x13+x14)/2 #2nd
        y28 = (y13+y14)/2
        x29 = (x21+x22)/2 #3rd
        y29 = (y21+y22)/2

        x_arr = [x1,x1,x2,x2,x3,x3,x4,x4,x5,x5,x6,x6,x7,x7,x8,x8,x9,x9,x27,x27,x26,x26,x10,x10,x11,x11,x12,x12,x13,x13,x14,x14,x15,x15,x16,x16,x17,x17,x28,x28,x18,x18,x19,x19,x20,x20,x21,x21,x22,x22,x23,x23,x24,x24,x25,x25,x29,x29]
        y_arr = [-y1,y1,-y2,y2,-y3,y3,-y4,y4,-y5,y5,-y6,y6,-y7,y7,-y8,y8,-y9,y9,-y27,y27,-y26,y26,-y10,y10,-y11,y11,-y12,y12,-y13,y13,-y14,y14,-y15,y15,-y16,y16,-y17,y17,-y28,y28,-y18,y18,-y19,y19,-y20,y20,-y21,y21,-y22,y22,-y23,y23,-y24,y24,-y25,y25,-y29,y29]

        arc1 = []
        arc2 = []
        arc3 = []
        arc4 = []
        arc5 = []
        arc6 = []
        arc7 = []
        arc8 = []
        arc9 = []
        arc10 = []
        arc11 = []
        arc12 = []
        arc13 = []
        arc14 = []
        arc15 = []
        arc16 = []
        arc17 = []
        arc18 = []
        arc19 = []
        arc20 = []
        seg1 = []
        seg2 = []
        seg3 = []
        seg4 = []
        seg5 = []
        seg6 = []
        seg7 = []
        seg8 = []
        seg9 = []
        seg10 = []
        seg11 = []
        seg12 = []
        seg13 = []
        seg14 = []
        seg15 = []
        seg16 = []
        seg17 = []
        seg18 = []
        seg19 = []
        seg20 = []

        # transpose list
        coords = [x_arr, y_arr]
        coords = list(zip(*coords))
        coords = [list(sublist) for sublist in coords]

        for i in range(0, 1):
            po = self.location.transform_coords(coords, alpha_total * i)
            
            # Shaft
            #arc1.append(drawer.draw_arc(self.location.anchor_xy, po[0], po[1]))
            
            # Flux Barrier 1
            #seg1.append(drawer.draw_line(po[2], po[3]))
            #arc2.append(drawer.draw_arc(po[5], po[7], po[3]))
            #seg2.append(drawer.draw_line(po[7], po[9]))
            #seg3.append(drawer.draw_line(po[11], po[13]))
            #arc4.append(drawer.draw_arc(po[15], po[13], po[17]))
            #seg4.append(drawer.draw_line(po[17], po[16]))
            #arc5.append(drawer.draw_arc(po[14], po[16], po[12]))
            #seg5.append(drawer.draw_line(po[12], po[10]))
            #arc6.append(drawer.draw_arc(po[18], po[8], po[10]))
            #seg6.append(drawer.draw_line(po[8], po[6]))
            #arc7.append(drawer.draw_arc(po[4], po[2], po[6]))

            # Flux Barrier 2
            seg7.append(drawer.draw_line(po[22], po[23]))
            arc9.append(drawer.draw_arc(po[25], po[27], po[23]))
            seg8.append(drawer.draw_line(po[27], po[29]))
            arc10.append(drawer.draw_arc(po[39], po[31], po[29]))
            seg9.append(drawer.draw_line(po[31], po[33]))
            arc11.append(drawer.draw_arc(po[35], po[33], po[37]))
            seg10.append(drawer.draw_line(po[37], po[36]))
            arc12.append(drawer.draw_arc(po[34], po[36], po[32]))
            seg11.append(drawer.draw_line(po[32], po[30]))
            arc13.append(drawer.draw_arc(po[38], po[28], po[30]))
            seg12.append(drawer.draw_line(po[28], po[26]))
            arc14.append(drawer.draw_arc(po[24], po[22], po[26]))

            # Flux Barrier 3
            #seg13.append(drawer.draw_line(po[40], po[41]))
            #arc15.append(drawer.draw_arc(po[43], po[45], po[41]))
            #seg14.append(drawer.draw_line(po[45], po[47]))
            #arc16.append(drawer.draw_arc(po[57], po[49], po[47]))
            #seg15.append(drawer.draw_line(po[49], po[51]))
            #arc17.append(drawer.draw_arc(po[53], po[51], po[55]))
            #seg16.append(drawer.draw_line(po[55], po[54]))
            #arc18.append(drawer.draw_arc(po[52], po[54], po[50]))
            #seg17.append(drawer.draw_line(po[50], po[48]))
            #arc19.append(drawer.draw_arc(po[56], po[46], po[48]))
            #seg18.append(drawer.draw_line(po[46], po[44]))
            #arc20.append(drawer.draw_arc(po[42], po[40], po[44]))
            
            # Rotor Outer Surface
            #arc8.append(drawer.draw_arc(self.location.anchor_xy, po[20], po[21]))

            # Close Shaft and Rotor Outer Surface
            #seg19.append(drawer.draw_line(po[0], po[20]))
            #seg20.append(drawer.draw_line(po[1], po[21]))
                        
        rad = (r_ri + d_r1 + w_b1 + d_r2 + w_b2/2)
        inner_coord = self.location.transform_coords([[rad, 0]])
        segments = [arc1,seg1,arc2,seg2,arc3,seg3,arc4,seg4,arc5,seg5,arc6,seg6,arc7,arc8,seg7,seg8,seg9,seg10,seg11,seg12,arc9,arc10,arc11,arc12,arc13,arc14,arc15,arc16,arc17,arc18,arc19,arc20,seg13,seg14,seg15,seg16,seg17,seg18,seg19,seg20]
        segs = [x for segment in segments for x in segment]
        cs_token = CrossSectToken(inner_coord[0], segs)  # create CrossSectToken object
        return cs_token

    def _validate_attr(self):

        if not isinstance(self._dim_alpha_b, DimAngular):
            raise TypeError('dim_alpha_b is not of DimAngular')

        if not isinstance(self._dim_r_ri, DimLinear):
            raise TypeError('dim_r_ri is not of DimLinear')

        if not isinstance(self._dim_r_ro, DimLinear):
            raise TypeError('dim_r_ro is not of DimLinear')

        if not isinstance(self._dim_r_f1, DimLinear):
            raise TypeError('dim_r_f1 is not of DimLinear')

        if not isinstance(self._dim_r_f2, DimLinear):
            raise TypeError('dim_r_f2 is not of DimLinear')

        if not isinstance(self._dim_r_f3, DimLinear):
            raise TypeError('dim_r_f3 is not of DimLinear')

        if not isinstance(self._dim_d_r1, DimLinear):
            raise TypeError('dim_d_r1 is not of DimLinear')

        if not isinstance(self._dim_d_r2, DimLinear):
            raise TypeError('dim_d_r2 is not of DimLinear')

        if not isinstance(self._dim_d_r3, DimLinear):
            raise TypeError('dim_d_r3 is not of DimLinear')

        if not isinstance(self._dim_w_b1, DimLinear):
            raise TypeError('dim_w_b1 is not of DimLinear')

        if not isinstance(self._dim_w_b2, DimLinear):
            raise TypeError('dim_w_b2 is not of DimLinear')

        if not isinstance(self._dim_w_b3, DimLinear):
            raise TypeError('dim_w_b3 is not of DimLinear')

        if not isinstance(self._dim_l_b1, DimLinear):
            raise TypeError('dim_l_b1 is not of DimLinear')

        if not isinstance(self._dim_l_b2, DimLinear):
            raise TypeError('dim_l_b2 is not of DimLinear')

        if not isinstance(self._dim_l_b3, DimLinear):
            raise TypeError('dim_l_b3 is not of DimLinear')

        if not isinstance(self._dim_l_b4, DimLinear):
            raise TypeError('dim_l_b4 is not of DimLinear')

        if not isinstance(self._dim_l_b5, DimLinear):
            raise TypeError('dim_l_b5 is not of DimLinear')

        if not isinstance(self._dim_l_b6, DimLinear):
            raise TypeError('dim_l_b6 is not of DimLinear')

        if not isinstance(self._p, int):
            raise TypeError('p is not of int')