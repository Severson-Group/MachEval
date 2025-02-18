import os, sys
import numpy as np
import femm

from ..tool_abc import toolabc as abc
from ..token_draw import TokenDraw
from ..token_make import TokenMake
from ...model_obj.dimensions import *

__all__ = []
__all__ += ["FEMMDesigner"]


class FEMMDesigner(
    abc.ToolBase, abc.DrawerBase, abc.MakerExtrudeBase, abc.MakerRevolveBase
):
    # FEMM Encapsulation.
    def __init__(self):
        """ FEMM init."""
        """Go to https://www.femm.info/wiki/pyFEMM for more details of femm methods."""

    def newdocument(
        self,
        hide_window=1,
        problem_type=0,
        ):
        """Create a new .fem document."""
        # magnetostatic problem: problem_type = 0
        femm.openfemm(hide_window)
        femm.newdocument(problem_type)

    def open(self, filename):
        """Open an existing document"""
        femm.opendocument(filename)

    def save(self, filepath):
        """Save document."""
        femm.mi_saveas(filepath)

    def save_as(self, filepath):
        """Save document."""

        femm.mi_saveas(filepath)
        # return attempts

    def close(self):
        """Close femm"""
        femm.mi_close()
        femm.closefemm()

    def draw_line(self, startxy: "Location2D", endxy: "Location2D") -> "TokenDraw":
        """Draw a line in FEMM.

        Args:
            startxy: Start point of line. Should be of type Location2D defined with eMach DimLinear.
            endxy: End point of the line. Should be of type Location2D defined with eMach DimLinear.

        Returns:
            TokenDraw: Wrapper object holding return values obtained upon drawing a line.
        """
        femm.mi_addnode(startxy[0], startxy[1])
        femm.mi_addnode(endxy[0], endxy[1])
        femm.mi_addsegment(startxy[0], startxy[1], endxy[0], endxy[1])

        line = 1
        return TokenDraw(line, 0)

    def draw_arc(
        self, centerxy: "Location2D", startxy: "Location2D", endxy: "Location2D"
    ) -> "TokenDraw":
        """Draw an arc in FEMM.

        Args:
            centerxy: Center point of arc. Should be of type Location2D defined with eMach Dimensions.
            startxy: Start point of arc. Should be of type Location2D defined with eMach Dimensions.
            endxy: End point of arc. Should be of type Location2D defined with eMach Dimensions.

        Returns:
            TokenDraw: Wrapper object holding return values obtained from tool upon drawing an arc.
        """
        
        alpha_s = np.arctan2(startxy[1] - centerxy[1], startxy[0] - centerxy[0])%(2*np.pi)
        alpha_e = np.arctan2(endxy[1] - centerxy[1], endxy[0] - centerxy[0])%(2*np.pi)
        
        if alpha_e < alpha_s:
            alpha_e = alpha_e + 2 * np.pi

        arc_angle = (alpha_e - alpha_s) / np.pi * 180    
        femm.mi_addnode(startxy[0], startxy[1])
        femm.mi_addnode(endxy[0], endxy[1])
        femm.mi_addarc(startxy[0], startxy[1], endxy[0], endxy[1], arc_angle, 1)
        
        arc = 1
        return TokenDraw(arc, 1)

    def draw_circle(self, centerxy, radius):
        """Draw a circle in FEMM."""
        startxy = np.array([0, 0])
        endxy = np.array([0, 0])
        startxy[0] = centerxy[0] + radius
        startxy[1] = centerxy[1]
        endxy[0] = centerxy[0] - radius
        endxy[1] = centerxy[1]

        femm.mi_drawarc(startxy[0], startxy[1], endxy[0], endxy[1], 180, 1)
        femm.mi_drawarc(endxy[0], endxy[1], startxy[0], startxy[1], 180, 1)
        return 1

    def probdef(
        self,
        freq=0,
        units='millimeters',
        type='planar',
        precision=1e-8,
        depth=1,
        minangle=30,
        acsolver=0):
        """Define a femm problem."""
        femm.mi_probdef(freq, units, type, precision, depth, minangle, acsolver)

    def add_material(self,mat_name):
        """Add a material that already exists in the femm library."""
        femm.mi_getmaterial(mat_name)
 
    def add_new_material(
        self,
        mat_name='NewMaterial', 
        mu_x=1, 
        mu_y=1, 
        H_c=0, 
        J=0, 
        Cduct=0, 
        Lam_d=0, 
        Phi_hmax=0, 
        lam_fill=1, 
        LamType=0, 
        Phi_hx=0, 
        Phi_hy=0, 
        nstr=0, 
        dwire=0,
        hdata=(0,0),
        bdata=(0,0)):
        """Add a new material to the project."""
        femm.mi_addmaterial(mat_name, mu_x, mu_y, H_c, J, Cduct, Lam_d, 
            Phi_hmax, lam_fill, LamType, Phi_hx, Phi_hy, nstr, dwire)
        if len(bdata) > 2:
            for n in range(0, len(bdata)):
                femm.mi_addbhpoint(mat_name, bdata[n], hdata[n])

    def set_block_prop(
        self,
        new_block=0,
        inner_coord=[0,0],        
        material_name='<None>',
        automesh=True,
        meshsize_if_no_automesh=0,
        incircuit=0,
        magdir=0,
        group_no=0,     
        turns=0,
        ):
        """This method selects a block label with coordinates (inner_coord[0], inner_coord[1])
        and a material name 'material_name', and sets component properties:
        automesh, meshsize (if no automesh), circuit name,
        magnet direction, group number, and number of turns.        
        """
        if new_block == 1:
            femm.mi_addblocklabel(inner_coord[0], inner_coord[1])

        femm.mi_selectlabel(inner_coord[0], inner_coord[1])
        femm.mi_setblockprop(material_name, automesh, meshsize_if_no_automesh,
            incircuit, magdir, group_no, turns)
        femm.mi_clearselected()

    def select_circle(self, centerxy=(0, 0), radius=0, editmode=4):
        """Select circle (used to create a motion component)
        editmode=4 selects all entity types (nodes, segments, arcs, block labels)"""
        femm.mi_selectcircle(centerxy[0], centerxy[1], radius, editmode)

    def set_group(self, groupID):
        """Sets groupID to the selected entities"""
        femm.mi_setgroup(groupID)
        femm.mi_clearselected

    def smartmesh(self, state):
        femm.mi_smartmesh(state)

    def create_boundary_condition(
        self,
        number_of_shells=10, # should be between 1 and 10
        radius=0,
        centerxy=(0, 0),
        bc = 1 # 0 for a Dirichlet outer edge or 1 for a Neumann outer edge
        ):
        femm.mi_makeABC(number_of_shells, radius, centerxy[0], centerxy[1], bc)

    def add_circuit(self, circuitname='Circuit', current=0, series_or_parallel=1):
        """Create circuit
        series_or_parallel: 0 parallel, 1 - series
        """
        femm.mi_addcircprop(circuitname, current, series_or_parallel) 

    def set_current(self, circuitname, current):
        current = str(np.real(current)) + '+I*' + str(np.imag(current))
        femm.mi_setcurrent(circuitname, current)

    def move_rotate(self, groupID, centerxy, angle):
        """Rotates objects having the same groupID 
        For example: rotor components"""
        femm.mi_clearselected
        femm.mi_selectgroup(groupID)
        femm.mi_moverotate(centerxy[0], centerxy[1], angle)
        femm.mi_clearselected

    def move_translate(self, groupID, dx, dy):
        """Translates objects having the same groupID 
        For example: linear motor mover components"""
        femm.mi_clearselected
        femm.mi_selectgroup(groupID)
        femm.mi_movetranslate(dx, dy)
        femm.mi_clearselected

    def mesh(self):
        """Mesh .fem problem. Note that this is not a necessary precursor of
        performing an analysis, as 'analyze' will make sure the mesh is 
        up to date before running an analysis.
        """
        femm.mi_createmesh

    def analyze(self):
        """Analyze .fem problem and load solution."""
        femm.mi_analyze(1)
        femm.mi_loadsolution

    def get_circuit_properties(self, circuitname):
        """Returns properties of a circuit with a name 'circuitname':
        - current,
        - voltage,
        - flux.
        """
        circuit_properties = femm.mo_getcircuitproperties(circuitname)
        return circuit_properties

    def get_probleminfo(self):
        probleminfo = femm.mo_getprobleminfo
        return probleminfo

    def blockintegral(self, groupID, type):
        """Calculate a block integral for the selected blocks.
        Used to calculate forces, torque, etc.
        See https://www.femm.info/wiki/pyFEMM for different integral types (specified by 'type').
        type: 18 - Fx, 19 - Fy, 22 - torque
        """
        femm.mo_groupselectblock(groupID)
        result = femm.mo_blockintegral(type)
        femm.mo_close
        return result

    def get_pointvalues(self, xy):
        """ Get the values associated with the point at (xy[0],xy[1]).
        Used to extract field components, etc.
        Refer to https://www.femm.info/wiki/pyFEMM to see the values that are returned.
        """
        results = femm.mo_getpointvalues(xy[0], xy[1])
        return results

    def get_vectorpotential(self, xy):
        """  Get the potential associated with the point at (xy[0],xy[1])."""
        A = femm.mo_geta(xy[0], xy[1])
        return A

    def get_fluxdensity(self, xy):
        """  Get the magnetic flux density associated with the point at (xy[0],xy[1]).
        Returns a list with two elements representing Bx and By for planar problems 
        or Br and Bz for axisymmetric problems.
        """
        B = femm.mo_getb(xy[0], xy[1])
        return B

    def get_numelements(self):
        """Returns the number of mesh elements"""
        numelements = femm.mo_numelements()
        return numelements

    def get_element(self, n):   
        """Returns the properties for the n-th element.
        Refer to https://www.femm.info/wiki/pyFEMM to see the properties that are returned.
        """
        element_properties = femm.mo_getelement(n)
        return element_properties

    def prepare_section(self, cs_token: "CrossSectToken") -> TokenMake:
        """ Not needed for FEMM.
        """
        return cs_token

    def extrude(self, name, material: str, depth: float, location: "Location3D", token=None) -> any:
        """ Assign material to a component. 
        Axial length has to be specified using "probdef" method.
        """
        inner_coord = token[0].inner_coord
        femm.mi_addblocklabel(inner_coord[0], inner_coord[1])
        femm.mi_selectlabel(inner_coord[0], inner_coord[1])
        femm.mi_setblockprop(material.name, True, 0, 0, 0, 0, 0)
        femm.mi_clearselected()

        return 1

    def revolve(self, name, material: str, center, axis, angle: float, location: "Location3D") -> any:
        """ Not implemented in FEMM. 
        Axisymmetric problem has to be specified using "probdef" method.
        """
        
        return 1

    def select(self):
        pass   
