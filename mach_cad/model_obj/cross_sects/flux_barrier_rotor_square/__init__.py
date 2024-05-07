import numpy as np

from ...dimensions.dim_linear import DimLinear
from ...dimensions.dim_angular import DimAngular
from ...dimensions import DimRadian
from ..cross_sect_base import CrossSectBase, CrossSectToken

__all__ = ['CrossSectFluxBarrierRotorSquarePartial_Iron1','CrossSectFluxBarrierRotorSquarePartial_Iron2','CrossSectFluxBarrierRotorSquarePartial_Iron3','CrossSectFluxBarrierRotorSquarePartial_Barrier1','CrossSectFluxBarrierRotorSquarePartial_Barrier2']

class CrossSectFluxBarrierRotorSquarePartial_Iron1(CrossSectBase):
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
    def dim_r_ri(self):
        return self._dim_r_ri

    @property
    def dim_r_ro(self):
        return self._dim_r_ro

    @property
    def dim_d_r1(self):
        return self._dim_d_r1

    @property
    def dim_d_r2(self):
        return self._dim_d_r2
    
    @property
    def dim_w_b1(self):
        return self._dim_w_b1

    @property
    def dim_w_b2(self):
        return self._dim_w_b2
    
    @property
    def p(self):
        return self._p

    def draw(self, drawer):
        r_ri = float(self.dim_r_ri)
        r_ro = float(self.dim_r_ro)
        d_r1 = float(self.dim_d_r1)
        d_r2 = float(self.dim_d_r2)
        w_b1 = float(self.dim_w_b1)
        w_b2 = float(self.dim_w_b2)
        p = float(self.p)

        # Point on Shaft
        x0 = 0
        y0 = r_ri
        x1 = r_ri
        y1 = 0
        # Corner Points on Rotor Surface
        x2 = 0
        y2 = r_ro
        x3 = r_ro
        y3 = 0
        # Points on Rotor Surface
        x4 = (r_ri + d_r1 - np.sqrt(r_ro**2 - (r_ri + d_r1)**2))*np.cos(np.pi/(2*p))
        y4 = np.sqrt(r_ro**2 - x4**2)
        x5 = (r_ri + d_r1 + np.sqrt(r_ro**2 - (r_ri + d_r1)**2))*np.sin(np.pi/(2*p))
        y5 = np.sqrt(r_ro**2 - x5**2)

        x_arr = [x0,x1,x2,x3,x4,x5]
        y_arr = [y0,y1,y2,y3,y4,y5]

        # Shaft
        arc1 = []
        # Magnetic Section 1
        seg1 = []
        arc2 = []
        seg2 = []
        arc3 = []
        seg3 = []

        # transpose list
        coords = [x_arr, y_arr]
        coords = list(zip(*coords))
        coords = [list(sublist) for sublist in coords]

        for i in range(0, 1):
            po = self.location.transform_coords(coords, (np.pi / 2)* i)
            
            # Shaft
            arc1.append(drawer.draw_arc(self.location.anchor_xy, po[1], po[0]))
            
            # Magnetic Section 1
            seg1.append(drawer.draw_line(po[0], po[2]))
            arc2.append(drawer.draw_arc(self.location.anchor_xy, po[4], po[2]))
            seg2.append(drawer.draw_line(po[4], po[5]))
            arc3.append(drawer.draw_arc(self.location.anchor_xy, po[3], po[5]))
            seg3.append(drawer.draw_line(po[3],po[1]))
                        
        rad = (r_ri + d_r1/2) # <---- SOURCE OF ERROR?
        inner_coord = self.location.transform_coords([[rad*np.cos(np.pi/(2*p)),rad*np.sin(np.pi/(2*p))]])
        segments = [arc1,seg1,arc2,seg2,seg3,arc3]
        segs = [x for segment in segments for x in segment]
        cs_token = CrossSectToken(inner_coord[0], segs)  # create CrossSectToken object
        return cs_token

    def _validate_attr(self):

        if not isinstance(self._dim_r_ri, DimLinear):
            raise TypeError('dim_r_ri is not of DimLinear')

        if not isinstance(self._dim_r_ro, DimLinear):
            raise TypeError('dim_r_ro is not of DimLinear')

        if not isinstance(self._dim_d_r1, DimLinear):
            raise TypeError('dim_d_r1 is not of DimLinear')

        if not isinstance(self._dim_d_r2, DimLinear):
            raise TypeError('dim_d_r2 is not of DimLinear')

        if not isinstance(self._dim_w_b1, DimLinear):
            raise TypeError('dim_w_b1 is not of DimLinear')

        if not isinstance(self._dim_w_b2, DimLinear):
            raise TypeError('dim_w_b2 is not of DimLinear')

        if not isinstance(self._p, int):
            raise TypeError('p is not of int')
        

class CrossSectFluxBarrierRotorSquarePartial_Barrier1(CrossSectBase):
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
    def dim_r_ri(self):
        return self._dim_r_ri

    @property
    def dim_r_ro(self):
        return self._dim_r_ro

    @property
    def dim_d_r1(self):
        return self._dim_d_r1

    @property
    def dim_d_r2(self):
        return self._dim_d_r2
    
    @property
    def dim_w_b1(self):
        return self._dim_w_b1

    @property
    def dim_w_b2(self):
        return self._dim_w_b2
    
    @property
    def p(self):
        return self._p

    def draw(self, drawer):
        r_ri = float(self.dim_r_ri)
        r_ro = float(self.dim_r_ro)
        d_r1 = float(self.dim_d_r1)
        d_r2 = float(self.dim_d_r2)
        w_b1 = float(self.dim_w_b1)
        w_b2 = float(self.dim_w_b2)
        p = float(self.p)

        # First Magnetic Segment

        # Point on Shaft
        x0 = 0
        y0 = r_ri
        x1 = r_ri
        y1 = 0
        # Corner Points on Rotor Surface
        x2 = 0
        y2 = r_ro
        x3 = r_ro
        y3 = 0
        # Points on Rotor Surface
        x4 = (r_ri + d_r1 - np.sqrt(r_ro**2 - (r_ri + d_r1)**2))*np.cos(np.pi/(2*p))
        y4 = np.sqrt(r_ro**2 - x4**2)
        x5 = (r_ri + d_r1 + np.sqrt(r_ro**2 - (r_ri + d_r1)**2))*np.sin(np.pi/(2*p))
        y5 = np.sqrt(r_ro**2 - x5**2)
        x6 = x4 + w_b1/np.cos(np.pi/(2*p))
        y6 = np.sqrt(r_ro**2 - x6**2)
        y7 = y5 + w_b1/np.sin(np.pi/(2*p))
        x7 = np.sqrt(r_ro**2 - y7**2)

        x_arr = [x0,x1,x2,x3,x4,x5,x6,x7]
        y_arr = [y0,y1,y2,y3,y4,y5,y6,y7]

        # Barrier Section 1
        seg1 = []
        arc1 = []
        seg2 = []
        arc2 = []

        # transpose list
        coords = [x_arr, y_arr]
        coords = list(zip(*coords))
        coords = [list(sublist) for sublist in coords]

        for i in range(0, 1):
            po = self.location.transform_coords(coords, (np.pi / 2)* i)
            
            # Barrier section 1
            arc1.append(drawer.draw_arc(self.location.anchor_xy, po[6], po[4]))
            seg1.append(drawer.draw_line(po[4], po[5]))
            arc2.append(drawer.draw_arc(self.location.anchor_xy, po[5], po[7]))
            seg2.append(drawer.draw_line(po[7], po[6]))
                        
        rad = (r_ri + d_r1 + w_b1/2) # <---- SOURCE OF ERROR?
        inner_coord = self.location.transform_coords([[rad*np.cos(np.pi/(2*p)),rad*np.sin(np.pi/(2*p))]])
        segments = [arc1,seg1,arc2,seg2]
        segs = [x for segment in segments for x in segment]
        cs_token = CrossSectToken(inner_coord[0], segs)  # create CrossSectToken object
        return cs_token

    def _validate_attr(self):

        if not isinstance(self._dim_r_ri, DimLinear):
            raise TypeError('dim_r_ri is not of DimLinear')

        if not isinstance(self._dim_r_ro, DimLinear):
            raise TypeError('dim_r_ro is not of DimLinear')

        if not isinstance(self._dim_d_r1, DimLinear):
            raise TypeError('dim_d_r1 is not of DimLinear')

        if not isinstance(self._dim_d_r2, DimLinear):
            raise TypeError('dim_d_r2 is not of DimLinear')

        if not isinstance(self._dim_w_b1, DimLinear):
            raise TypeError('dim_w_b1 is not of DimLinear')

        if not isinstance(self._dim_w_b2, DimLinear):
            raise TypeError('dim_w_b2 is not of DimLinear')

        if not isinstance(self._p, int):
            raise TypeError('p is not of int')
        

class CrossSectFluxBarrierRotorSquarePartial_Iron2(CrossSectBase):
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
    def dim_r_ri(self):
        return self._dim_r_ri

    @property
    def dim_r_ro(self):
        return self._dim_r_ro

    @property
    def dim_d_r1(self):
        return self._dim_d_r1

    @property
    def dim_d_r2(self):
        return self._dim_d_r2
    
    @property
    def dim_w_b1(self):
        return self._dim_w_b1

    @property
    def dim_w_b2(self):
        return self._dim_w_b2
    
    @property
    def p(self):
        return self._p

    def draw(self, drawer):
        r_ri = float(self.dim_r_ri)
        r_ro = float(self.dim_r_ro)
        d_r1 = float(self.dim_d_r1)
        d_r2 = float(self.dim_d_r2)
        w_b1 = float(self.dim_w_b1)
        w_b2 = float(self.dim_w_b2)
        p = float(self.p)

        # First Magnetic Segment

        # Point on Shaft
        x0 = 0
        y0 = r_ri
        x1 = r_ri
        y1 = 0
        # Corner Points on Rotor Surface
        x2 = 0
        y2 = r_ro
        x3 = r_ro
        y3 = 0
        # Points on Rotor Surface
        x4 = (r_ri + d_r1 - np.sqrt(r_ro**2 - (r_ri + d_r1)**2))*np.cos(np.pi/(2*p))
        y4 = np.sqrt(r_ro**2 - x4**2)
        x5 = (r_ri + d_r1 + np.sqrt(r_ro**2 - (r_ri + d_r1)**2))*np.sin(np.pi/(2*p))
        y5 = np.sqrt(r_ro**2 - x5**2)
        x6 = x4 + w_b1/np.cos(np.pi/(2*p))
        y6 = np.sqrt(r_ro**2 - x6**2)
        y7 = y5 + w_b1/np.sin(np.pi/(2*p))
        x7 = np.sqrt(r_ro**2 - y7**2)
        x8 = (r_ri + d_r1 + w_b1 + d_r2 - np.sqrt(r_ro**2 - (r_ri + d_r1 + w_b1 + d_r2)**2))*np.cos(np.pi/(2*p))
        y8 = np.sqrt(r_ro**2 - x8**2)
        x9 = (r_ri + d_r1 + w_b1 + d_r2 + np.sqrt(r_ro**2 - (r_ri + d_r1 + w_b1 + d_r2)**2))*np.cos(np.pi/(2*p))
        y9 = np.sqrt(r_ro**2 - x9**2)

        x_arr = [x0,x1,x2,x3,x4,x5,x6,x7,x8,x9]
        y_arr = [y0,y1,y2,y3,y4,y5,y6,y7,y8,y9]

        # Barrier Section 1
        seg1 = []
        arc1 = []
        seg2 = []
        arc2 = []

        # transpose list
        coords = [x_arr, y_arr]
        coords = list(zip(*coords))
        coords = [list(sublist) for sublist in coords]

        for i in range(0, 1):
            po = self.location.transform_coords(coords, (np.pi / 2)* i)
            
            # Barrier section 1
            arc1.append(drawer.draw_arc(self.location.anchor_xy, po[8], po[6]))
            seg1.append(drawer.draw_line(po[6], po[7]))
            arc2.append(drawer.draw_arc(self.location.anchor_xy, po[7], po[9]))
            seg2.append(drawer.draw_line(po[9], po[8]))
                        
        rad = (r_ri + d_r1 + w_b1 + d_r2/2) # <---- SOURCE OF ERROR?
        inner_coord = self.location.transform_coords([[rad*np.cos(np.pi/(2*p)),rad*np.sin(np.pi/(2*p))]])
        segments = [arc1,seg1,arc2,seg2]
        segs = [x for segment in segments for x in segment]
        cs_token = CrossSectToken(inner_coord[0], segs)  # create CrossSectToken object
        return cs_token

    def _validate_attr(self):

        if not isinstance(self._dim_r_ri, DimLinear):
            raise TypeError('dim_r_ri is not of DimLinear')

        if not isinstance(self._dim_r_ro, DimLinear):
            raise TypeError('dim_r_ro is not of DimLinear')

        if not isinstance(self._dim_d_r1, DimLinear):
            raise TypeError('dim_d_r1 is not of DimLinear')

        if not isinstance(self._dim_d_r2, DimLinear):
            raise TypeError('dim_d_r2 is not of DimLinear')

        if not isinstance(self._dim_w_b1, DimLinear):
            raise TypeError('dim_w_b1 is not of DimLinear')

        if not isinstance(self._dim_w_b2, DimLinear):
            raise TypeError('dim_w_b2 is not of DimLinear')

        if not isinstance(self._p, int):
            raise TypeError('p is not of int')
        

class CrossSectFluxBarrierRotorSquarePartial_Barrier2(CrossSectBase):
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
    def dim_r_ri(self):
        return self._dim_r_ri

    @property
    def dim_r_ro(self):
        return self._dim_r_ro

    @property
    def dim_d_r1(self):
        return self._dim_d_r1

    @property
    def dim_d_r2(self):
        return self._dim_d_r2
    
    @property
    def dim_w_b1(self):
        return self._dim_w_b1

    @property
    def dim_w_b2(self):
        return self._dim_w_b2
    
    @property
    def p(self):
        return self._p

    def draw(self, drawer):
        r_ri = float(self.dim_r_ri)
        r_ro = float(self.dim_r_ro)
        d_r1 = float(self.dim_d_r1)
        d_r2 = float(self.dim_d_r2)
        w_b1 = float(self.dim_w_b1)
        w_b2 = float(self.dim_w_b2)
        p = float(self.p)

        # First Magnetic Segment

        # Point on Shaft
        x0 = 0
        y0 = r_ri
        x1 = r_ri
        y1 = 0
        # Corner Points on Rotor Surface
        x2 = 0
        y2 = r_ro
        x3 = r_ro
        y3 = 0
        # Points on Rotor Surface
        x4 = (r_ri + d_r1 - np.sqrt(r_ro**2 - (r_ri + d_r1)**2))*np.cos(np.pi/(2*p))
        y4 = np.sqrt(r_ro**2 - x4**2)
        x5 = (r_ri + d_r1 + np.sqrt(r_ro**2 - (r_ri + d_r1)**2))*np.sin(np.pi/(2*p))
        y5 = np.sqrt(r_ro**2 - x5**2)
        x6 = x4 + w_b1/np.cos(np.pi/(2*p))
        y6 = np.sqrt(r_ro**2 - x6**2)
        y7 = y5 + w_b1/np.sin(np.pi/(2*p))
        x7 = np.sqrt(r_ro**2 - y7**2)
        x8 = (r_ri + d_r1 + w_b1 + d_r2 - np.sqrt(r_ro**2 - (r_ri + d_r1 + w_b1 + d_r2)**2))*np.cos(np.pi/(2*p))
        y8 = np.sqrt(r_ro**2 - x8**2)
        x9 = (r_ri + d_r1 + w_b1 + d_r2 + np.sqrt(r_ro**2 - (r_ri + d_r1 + w_b1 + d_r2)**2))*np.cos(np.pi/(2*p))
        y9 = np.sqrt(r_ro**2 - x9**2)
        x10 = x8 + w_b2/np.cos(np.pi/(2*p))
        y10 = np.sqrt(r_ro**2 - x10**2)
        y11 = y9 + w_b2/np.sin(np.pi/(2*p))
        x11 = np.sqrt(r_ro**2 - y11**2)        

        x_arr = [x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11]
        y_arr = [y0,y1,y2,y3,y4,y5,y6,y7,y8,y9,y10,y11]

        # Barrier Section 1
        seg1 = []
        arc1 = []
        seg2 = []
        arc2 = []

        # transpose list
        coords = [x_arr, y_arr]
        coords = list(zip(*coords))
        coords = [list(sublist) for sublist in coords]

        for i in range(0, 1):
            po = self.location.transform_coords(coords, (np.pi / 2)* i)
            
            # Barrier section 1
            arc1.append(drawer.draw_arc(self.location.anchor_xy, po[10], po[8]))
            seg1.append(drawer.draw_line(po[8], po[9]))
            arc2.append(drawer.draw_arc(self.location.anchor_xy, po[9], po[11]))
            seg2.append(drawer.draw_line(po[11], po[10]))
                        
        rad = (r_ri + d_r1 + w_b1 + d_r2 + w_b2/2) # <---- SOURCE OF ERROR?
        inner_coord = self.location.transform_coords([[rad*np.cos(np.pi/(2*p)),rad*np.sin(np.pi/(2*p))]])
        segments = [arc1,seg1,arc2,seg2]
        segs = [x for segment in segments for x in segment]
        cs_token = CrossSectToken(inner_coord[0], segs)  # create CrossSectToken object
        return cs_token

    def _validate_attr(self):

        if not isinstance(self._dim_r_ri, DimLinear):
            raise TypeError('dim_r_ri is not of DimLinear')

        if not isinstance(self._dim_r_ro, DimLinear):
            raise TypeError('dim_r_ro is not of DimLinear')

        if not isinstance(self._dim_d_r1, DimLinear):
            raise TypeError('dim_d_r1 is not of DimLinear')

        if not isinstance(self._dim_d_r2, DimLinear):
            raise TypeError('dim_d_r2 is not of DimLinear')

        if not isinstance(self._dim_w_b1, DimLinear):
            raise TypeError('dim_w_b1 is not of DimLinear')

        if not isinstance(self._dim_w_b2, DimLinear):
            raise TypeError('dim_w_b2 is not of DimLinear')

        if not isinstance(self._p, int):
            raise TypeError('p is not of int')
        

class CrossSectFluxBarrierRotorSquarePartial_Iron3(CrossSectBase):
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
    def dim_r_ri(self):
        return self._dim_r_ri

    @property
    def dim_r_ro(self):
        return self._dim_r_ro

    @property
    def dim_d_r1(self):
        return self._dim_d_r1

    @property
    def dim_d_r2(self):
        return self._dim_d_r2
    
    @property
    def dim_w_b1(self):
        return self._dim_w_b1

    @property
    def dim_w_b2(self):
        return self._dim_w_b2
    
    @property
    def p(self):
        return self._p

    def draw(self, drawer):
        r_ri = float(self.dim_r_ri)
        r_ro = float(self.dim_r_ro)
        d_r1 = float(self.dim_d_r1)
        d_r2 = float(self.dim_d_r2)
        w_b1 = float(self.dim_w_b1)
        w_b2 = float(self.dim_w_b2)
        p = float(self.p)

        # First Magnetic Segment

        # Point on Shaft
        x0 = 0
        y0 = r_ri
        x1 = r_ri
        y1 = 0
        # Corner Points on Rotor Surface
        x2 = 0
        y2 = r_ro
        x3 = r_ro
        y3 = 0
        # Points on Rotor Surface
        x4 = (r_ri + d_r1 - np.sqrt(r_ro**2 - (r_ri + d_r1)**2))*np.cos(np.pi/(2*p))
        y4 = np.sqrt(r_ro**2 - x4**2)
        x5 = (r_ri + d_r1 + np.sqrt(r_ro**2 - (r_ri + d_r1)**2))*np.sin(np.pi/(2*p))
        y5 = np.sqrt(r_ro**2 - x5**2)
        x6 = x4 + w_b1/np.cos(np.pi/(2*p))
        y6 = np.sqrt(r_ro**2 - x6**2)
        y7 = y5 + w_b1/np.sin(np.pi/(2*p))
        x7 = np.sqrt(r_ro**2 - y7**2)
        x8 = (r_ri + d_r1 + w_b1 + d_r2 - np.sqrt(r_ro**2 - (r_ri + d_r1 + w_b1 + d_r2)**2))*np.cos(np.pi/(2*p))
        y8 = np.sqrt(r_ro**2 - x8**2)
        x9 = (r_ri + d_r1 + w_b1 + d_r2 + np.sqrt(r_ro**2 - (r_ri + d_r1 + w_b1 + d_r2)**2))*np.cos(np.pi/(2*p))
        y9 = np.sqrt(r_ro**2 - x9**2)
        x10 = x8 + w_b2/np.cos(np.pi/(2*p))
        y10 = np.sqrt(r_ro**2 - x10**2)
        y11 = y9 + w_b2/np.sin(np.pi/(2*p))
        x11 = np.sqrt(r_ro**2 - y11**2)        

        x_arr = [x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11]
        y_arr = [y0,y1,y2,y3,y4,y5,y6,y7,y8,y9,y10,y11]

        # Barrier Section 1
        seg1 = []
        arc1 = []

        # transpose list
        coords = [x_arr, y_arr]
        coords = list(zip(*coords))
        coords = [list(sublist) for sublist in coords]

        for i in range(0, 1):
            po = self.location.transform_coords(coords, (np.pi / 2)* i)
            
            # Barrier section 1
            arc1.append(drawer.draw_arc(self.location.anchor_xy, po[11], po[10]))
            seg1.append(drawer.draw_line(po[10], po[11]))
                        
        rad = (r_ro - w_b2/2) # <---- SOURCE OF ERROR?
        inner_coord = self.location.transform_coords([[rad*np.cos(np.pi/(2*p)),rad*np.sin(np.pi/(2*p))]])
        segments = [arc1,seg1]
        segs = [x for segment in segments for x in segment]
        cs_token = CrossSectToken(inner_coord[0], segs)  # create CrossSectToken object
        return cs_token

    def _validate_attr(self):

        if not isinstance(self._dim_r_ri, DimLinear):
            raise TypeError('dim_r_ri is not of DimLinear')

        if not isinstance(self._dim_r_ro, DimLinear):
            raise TypeError('dim_r_ro is not of DimLinear')

        if not isinstance(self._dim_d_r1, DimLinear):
            raise TypeError('dim_d_r1 is not of DimLinear')

        if not isinstance(self._dim_d_r2, DimLinear):
            raise TypeError('dim_d_r2 is not of DimLinear')

        if not isinstance(self._dim_w_b1, DimLinear):
            raise TypeError('dim_w_b1 is not of DimLinear')

        if not isinstance(self._dim_w_b2, DimLinear):
            raise TypeError('dim_w_b2 is not of DimLinear')

        if not isinstance(self._p, int):
            raise TypeError('p is not of int')