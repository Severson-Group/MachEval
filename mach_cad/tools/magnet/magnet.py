from win32com.client import DispatchEx

from ..tool_abc import toolabc as abc
from ..token_draw import TokenDraw
from . import document
from .document import *
from ...model_obj.dimensions import *

__all__ = []
__all__ += ["MagNet"]


class MagNet(abc.ToolBase, abc.DrawerBase, abc.MakerExtrudeBase, abc.MakerRevolveBase):
    """ eMach MAGNET tool class to interface between Python scripts and the MAGNET application.
    """

    def __init__(self, visible=False):
        self.mn = DispatchEx("MagNet.Application")
        self.mn.visible = visible
        self.doc = None
        self.view = None
        self.sol = None
        self.consts = None
        self.default_length = None
        self.default_angle = None
        self.filename = None

    def __del__(self):
        self.mn.close(False)

    def open(self, filename=None, length_unit='DimMillimeter', angle_unit='DimDegree'):
        """ Open a new MAGNET session.

        Launches the MAGNET application by opening an already created file if or by creating a new file. Assigns other
        attributes to MAGNET application handles for future operations.

        Args:
            filename: Name of the MAGNET file which is to be opened. If no value is passed, a new file is created.
            length_unit: String input of the eMach linear dimension unit to be employed to construct designs.
                DimMillimeter and DimInch are natively supported in eMach.
            angle_unit: String input of the eMach angular dimension unit to be employed to construct designs. DimDegree
                and DimRadian are natively supported in eMach.
        """
        self.default_length = length_unit
        self.default_angle = angle_unit

        if filename is str:
            self.doc = self.mn.openDocument(filename)
            self.filename = filename
        else:
            self.doc = self.mn.newDocument()
        self.view = self.doc.getView()
        self.sol = self.doc.getSolution()
        self.consts = self.mn.getConstants()  # Get MAGNET Constants

        self.set_default_length(length_unit, False)

    def close(self):
        """Close currently open MAGNET application without saving."""
        self.doc.close(False)

    def save_as(self, filename):
        self.filename = filename
        self.save()

    def save(self):
        if self.filename is str:
            self.doc.save(self.filename)
        else:
            raise AttributeError('Unable to save file. Use the save_as() function')

    def draw_line(self, startxy, endxy):
        """Draw a line in MAGNET.

        Args:
            startxy: Start point of line. Should be of type Location2D defined with eMach DimLinear.
            endxy: End point of the. Should be of type Location2D defined with eMach DimLinear.

        Returns:
            TokenDraw: Wrapper object holding return values obtained from MAGNET upon drawing a line.
        """
        start_x = eval(self.default_length)(startxy[0])
        start_y = eval(self.default_length)(startxy[1])
        end_x = eval(self.default_length)(endxy[0])
        end_y = eval(self.default_length)(endxy[1])
        ret = self.view.newLine(start_x, start_y, end_x, end_y)

        self.mn.setVariant(0, 'line', 'python')
        line = self.mn.getVariant(0, 'python');

        return TokenDraw(line, 0)

    def draw_arc(self, centerxy, startxy, endxy):
        """Draw an arc in MAGNET.

        Args:
            centerxy: Centre point of arc. Should be of type Location2D defined with eMach Dimensions.
            startxy: Start point of arc. Should be of type Location2D defined with eMach Dimensions.
            endxy: End point of arc. Should be of type Location2D defined with eMach Dimensions.

        Returns:
            TokenDraw: Wrapper object holding return values obtained from tool upon drawing an arc.
        """
        center_x = eval(self.default_length)(centerxy[0])
        center_y = eval(self.default_length)(centerxy[1])
        start_x = eval(self.default_length)(startxy[0])
        start_y = eval(self.default_length)(startxy[1])
        end_x = eval(self.default_length)(endxy[0])
        end_y = eval(self.default_length)(endxy[1])

        ret = self.view.newArc(center_x, center_y, start_x, start_y, end_x, end_y)

        self.mn.setVariant(0, 'arc', 'python')
        arc = self.mn.getVariant(0, 'python')

        return TokenDraw(arc, 1)

    def select(self):
        pass

    def prepare_section(self, cs_token):
        """Select a section in MAGNET.

        Args:
            cs_token: Wrapper object of type CrossSectToken. Holds information on inner coordinate of section to be
                selected.
        """
        inner_coord_x = eval(self.default_length)(cs_token.inner_coord[0])
        inner_coord_y = eval(self.default_length)(cs_token.inner_coord[1])

        self.view.selectAt(
            inner_coord_x,
            inner_coord_y,
            self.consts.infoSetSelection,
            [self.consts.infoSliceSurface],
        )
        return 1

    def extrude(self, name, material, depth, location, token=None):
        """Extrude, assign a material and name a selected section in MAGNET.

        Args:
            name: Name assigned to extruded component.
            material: Name of material from tool library whose properties are assigned to component.
            depth: Length of extrusion. Should be of type DimLinear.
            location: Not used currently.
            token: Not used currently.

        Returns:
            ret: 1 if extrusion was successful, 0 otherwise.
        """
        depth_actual = eval(self.default_length)(depth)
        name = [name]
        ret = self.view.makeComponentInALine(
            depth_actual,
            name,
            "Name=" + material,
            self.consts.infoMakeComponentRemoveVertices
        )

        return ret

    def revolve(self, name, material, center, axis, angle, location, token=None):
        """Revolve, assign a material and name a selected section in MAGNET.

        Args:
            name: Name assigned to extruded component.
            material: Name of material from tool library whose properties are assigned to component.
            center: Center point about which the cross-section is revolved. Should be of type Location2D defined with
                eMach Dimensions.
            axis: Axis about which the cross-section is revolved. Should be of type Location2D defined with eMach
                Dimensions.
            angle: Angle of revolution. Should be of type DimAngular.
            location: Not used currently.
            token: Not used currently.

        Returns:
            ret: 1 if extrusion was successful, 0 otherwise.
        """
        center_x = eval(self.default_length)(center[0])
        center_y = eval(self.default_length)(center[1])
        axis_x = eval(self.default_length)(axis[0])
        axis_y = eval(self.default_length)(axis[1])
        angle_actual = eval(self.default_length)(angle)

        ret = self.view.makeComponentInAnArc(
            center_x,
            center_y,
            axis_x,
            axis_y,
            angle_actual,
            name,
            "Name=" + material,
            self.consts.infoMakeComponentRemoveVertices,
        )

        return ret

    def view_all(self):
        """View entire cross-section of drawing made in MAGNET"""
        self.view.viewAll()

    def set_default_length(self, user_unit, make_app_default):
        """Set the default length unit in MAGNET. Supports millimeters and inches.

        Args:
            user_unit: String representing the unit the user wishes to set as default.
            make_app_default: Boolean with which user can set a unit as the default unit employed in MagNet

        Raises:
            TypeError: Incorrect dimension passed
        """

        if user_unit == 'DimMillimeter':
            app_unit = 'millimeter'
        elif user_unit == 'DimInch':
            app_unit = 'inches'
        else:
            raise TypeError("Dimension not supported")
        self.default_length = user_unit
        self.doc.setDefaultLengthUnit(app_unit, make_app_default)

    def set_visibility(self, visible):
        self.mn.visible = visible
