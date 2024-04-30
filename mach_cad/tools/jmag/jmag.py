from win32com.client import DispatchEx
import os
import string

from ..tool_abc import toolabc as abc
from ..token_draw import TokenDraw
from ..token_make import TokenMake
from ...model_obj.dimensions import *

__all__ = []
__all__ += ["JmagDesigner"]


class JmagDesigner(
    abc.ToolBase, abc.DrawerBase, abc.MakerExtrudeBase, abc.MakerRevolveBase
):
    def __init__(self, jmag_version=None):
        if jmag_version is None:
            self.jd_instance = DispatchEx("designerstarter.InstanceManager")
        else:
            jmag_version = jmag_version.translate(str.maketrans('', '', string.punctuation))
            self.jd_instance = DispatchEx("designerstarter.InstanceManager.%s" % jmag_version)
        self.jd = None  # JMAG-Designer Application object
        self.geometry_editor = None  # The Geometry Editor object
        self.doc = None  # The document object in Geometry Editor
        self.assembly = None  # The assembly object in Geometry Editor
        self.sketch = None  # The sketch object in Geometry Editor
        self.part = None  # The part object in Geometry Editor
        self.model = None  # The model object in JMAG Designer
        self.study = None  # The study object in JMAG Designer
        self.view = None  # The view object in JMAG Designer
        self.filepath = None  # string that specifies the complete path to JMAG file
        self.study_type = None  # The study type in JMAG Designer
        self.default_length = None  # Default length unit is m
        self.default_angle = None  # Default angle unit is degrees
        self.visible = True  # Application visibility

    # def __del__(self):
    #     self.jd.Quit()

    def open(
        self,
        comp_filepath,
        length_unit="DimMeter",
        angle_unit="DimDegree",
        study_type="Transient",
    ):
        """Open an existing JMAG file or a create new one if file does not exist.

        Launches the JMAG application by opening an already created file if or by creating a new file. Assigns JMAG
        application handles to object attributes for future operations. If intended file path does not exist and could
        not be created, an error is raised.

        Args:
            comp_filepath: Path of the JMAG file which is to be opened. If no such file exist, a new one is created.
            length_unit: String input of the eMach linear dimension unit to be employed to construct designs. JMAG tool
                only supports DimMeter
            angle_unit: String input of the eMach angular dimension unit to be employed to construct designs. JMAG tool
                only supports DimDegree
            study_type: Specifies type of study launched in JMAG. Commonly used types are Static2D, Transient2D,
                Frequency2D, Static, Transient, Frequency

        Returns:
            file_found: 1 if file exists; 0 if new file was created.
        """
        self.default_length = length_unit
        self.default_angle = angle_unit
        self.study_type = study_type

        file_found = 0
        # convert relative paths to absolute paths
        if not os.path.isabs(comp_filepath):
            comp_filepath = os.path.abspath(".") + "\\" + comp_filepath

        # parse out path and extension of file
        file_name_path, file_extension = os.path.splitext(comp_filepath)
        file_contents = file_name_path.split("\\")

        # check if extension is of right type
        if file_extension != ".jproj":
            raise TypeError("Incorrect file extension")
        # extract folder where file resides or is meant to reside
        file_path = ""
        for i in range(len(file_contents) - 1):
            file_path = file_path + file_contents[i] + "\\"

        # Obtains a JMAG-Designer Application object. If the specified JMAG-Designer key does not exist, a new instance
        # of JMAG-Designer is started. Used when independently operating multiple instances of JMAG-Designer
        self.jd = self.jd_instance.GetNamedInstance(comp_filepath, 0)

        # set visibility for JMAG
        self.set_visibility(self.visible)

        # check if file exists
        if os.path.exists(comp_filepath):
            file_found = 1
            self.jd.Load(comp_filepath)
            self.filepath = comp_filepath
        # if not, check if folder exists
        else:
            if os.path.exists(file_path):
                self.filepath = comp_filepath
            # if folder does not exist first try creating the folder. If that fails, create file in current working dir
            else:
                try:
                    os.mkdir(file_path)
                    self.filepath = comp_filepath
                except FileNotFoundError:
                    raise FileNotFoundError(
                        "Path was not found and could not be created"
                    )

            self.jd.NewProject(self.filepath)  # create a new JMAG project
            self.save_as(
                self.filepath
            )  # JMAG requires project to be saved before creating geometry

        self.view = self.jd.View()
        self.jd.GetCurrentModel().RestoreCadLink(
            True
        )  # Restores the link to a CAD system to draw stuff
        self.geometry_editor = self.jd.CreateGeometryEditor(
            True
        )  # creates new geometry or edits the geometry.
        self.doc = self.geometry_editor.GetDocument()
        self.assembly = self.doc.GetAssembly()
        return file_found

    def save(self):
        """Save JMAG designer file at previously defined path"""
        if type(self.filepath) is str:
            self.jd.SaveAs(self.filepath)
        else:
            raise AttributeError("Unable to save file. Use the save_as() function")

    def save_as(self, filepath):
        """Save JMAG designer file at defined path"""
        self.filepath = filepath
        self.save()

    def close(self):
        """Close JMAG designer file and all associated applications"""
        del self

    def set_visibility(self, visible):
        """Set JMAG designer file visibility by passing True or False to visible"""
        self.visible = visible
        if self.visible:
            self.jd.Show()
        else:
            self.jd.Hide()

    def draw_line(self, startxy: "Location2D", endxy: "Location2D") -> "TokenDraw":
        """Draw a line in JMAG Geometry Editor.

        Args:
            startxy: Start point of line. Should be of type Location2D defined with eMach DimLinear.
            endxy: End point of the. Should be of type Location2D defined with eMach DimLinear.

        Returns:
            TokenDraw: Wrapper object holding return values obtained upon drawing a line.
        """
        if self.sketch is None:
            self.sketch = self.create_sketch()

        start_x = eval(self.default_length)(startxy[0])
        start_y = eval(self.default_length)(startxy[1])
        end_x = eval(self.default_length)(endxy[0])
        end_y = eval(self.default_length)(endxy[1])

        line = self.sketch.CreateLine(start_x, start_y, end_x, end_y)
        return TokenDraw(line, 0)

    def draw_arc(
        self, centerxy: "Location2D", startxy: "Location2D", endxy: "Location2D"
    ) -> "TokenDraw":
        """Draw an arc in JMAG Geometry Editor.

        Args:
            centerxy: Centre point of arc. Should be of type Location2D defined with eMach Dimensions.
            startxy: Start point of arc. Should be of type Location2D defined with eMach Dimensions.
            endxy: End point of arc. Should be of type Location2D defined with eMach Dimensions.

        Returns:
            TokenDraw: Wrapper object holding return values obtained from tool upon drawing an arc.
        """
        if self.sketch is None:
            self.sketch = self.create_sketch()

        center_x = eval(self.default_length)(centerxy[0])
        center_y = eval(self.default_length)(centerxy[1])
        start_x = eval(self.default_length)(startxy[0])
        start_y = eval(self.default_length)(startxy[1])
        end_x = eval(self.default_length)(endxy[0])
        end_y = eval(self.default_length)(endxy[1])
        arc = self.sketch.CreateArc(center_x, center_y, start_x, start_y, end_x, end_y)
        return TokenDraw(arc, 1)

    def create_sketch(self):
        """Create and open a new sketch in JMAG geometry editor"""
        # create sketch in XY plane
        ref1 = self.assembly.GetItem(
            "XY Plane"
        )  # Obtains an item displayed in the [Model Manager] tree.
        ref2 = self.doc.CreateReferenceFromItem(
            ref1
        )  # Creates JMAG ReferenceObject from JMAG ItemObject.
        sketch = self.assembly.CreateSketch(
            ref2
        )  # Creates a 2D sketch under the assembly.

        # set name for sketch
        sketch_name = "sketch_drawing"
        sketch.SetProperty("Name", sketch_name)
        sketch.OpenSketch()  # Starts editing a sketch

        return sketch

    def create_part(self):
        """Create a new part in JMAG geometry editor"""

        sketch_name = "sketch_drawing"
        self.sketch.OpenSketch()  # Start editing sketch
        ref1 = self.assembly.GetItem(sketch_name)
        ref2 = self.doc.CreateReferenceFromItem(ref1)
        self.assembly.MoveToPart(
            ref2
        )  # Moves a 2D sketch that is under [assembly] under a new part.
        part = self.assembly.GetItem(sketch_name)
        self.sketch.CloseSketch()

        return part

    def create_model(self, model_name):
        num_models = self.jd.NumModels()
        if num_models == 1:
            model = self.jd.GetCurrentModel()
            model.setName(model_name)
        else:
            for i in range(num_models - 1):
                self.jd.DeleteModel(i)
            model = self.jd.GetCurrentModel()
            model.setName(model_name)

        return model

    def select(self):
        pass

    def prepare_section(self, cs_token: "CrossSectToken", num_copy_rotate=0) -> TokenMake:
        """ Creates JMAG geometry region using lines and arcs.
        """
        # self.validate_attr(cs_token, 'CrossSectToken')
        self.geometry_editor.View().Xy()
        self.doc.GetSelection().Clear()
        for i in range(len(cs_token.token)):
            self.doc.GetSelection().Add(
                self.sketch.GetItem(cs_token.token[i].draw_token.GetName())
            )

        id = self.sketch.NumItems()
        self.sketch.CreateRegions()
        id2 = self.sketch.NumItems()
        visItem = 1
        itemType = 64
        innerCoord1 = cs_token.inner_coord[0]
        innerCoord2 = cs_token.inner_coord[1]

        innerCoord1 = eval(self.default_length)(innerCoord1)
        innerCoord2 = eval(self.default_length)(innerCoord2)

        self.geometry_editor.View().SelectAtCoordinateDlg(
            innerCoord1, innerCoord2, 0, visItem, itemType
        )
        region = self.doc.GetSelection().Item(0)
        regionName = region.GetName()

        regionList = ["Region"]
        for idx in range(1, id2 - id):
            regionList.append("Region." + str(idx + 1))

        for idx in range((id2 - id)):
            if regionList[idx] != regionName:
                self.doc.GetSelection().Clear()
                self.doc.GetSelection().Add(self.sketch.GetItem(regionList[idx]))
                self.doc.GetSelection().Delete()

        # RotateCopy
        if num_copy_rotate != 0:
            bMerge = True
            # print('Copy', num_copy_rotate)
            Q_float = float(num_copy_rotate)  # don't ask me, ask JSOL
            circular_pattern = self.sketch.CreateRegionCircularPattern()
            circular_pattern.SetProperty("Merge", bMerge)

            ref2 = self.doc.CreateReferenceFromItem(region)
            circular_pattern.SetPropertyByReference("Region", ref2)
            face_region_string = circular_pattern.GetProperty("Region")

            circular_pattern.SetProperty("CenterType", 2)  # origin I guess

            # print('Copy', Q_float)
            circular_pattern.SetProperty("Angle", "360/%d" % Q_float)
            circular_pattern.SetProperty("Instance", str(Q_float))

        self.sketch.CloseSketch()

        return region

    def create_study(self, study_name, study_type, model) -> any:
        """Creates a JMAG study
        """
        self.study_type = study_type
        num_studies = self.jd.NumStudies()
        if num_studies == 0:
            study = model.CreateStudy(study_type, study_name)
        else:
            for i in range(num_studies - 2):
                model.DeleteStudy(i)
            study = self.jd.GetCurrentStudy()
            study.SetName(study_name)

        return study

    def extrude(self, name, material: str, depth: float, token=None) -> any:
        """ Extrudes a cross-section to a 3D component

        Args:
            name: name of the newly extruded component.
            depth: Depth of extrusion. Should be defined with eMach Dimensions.
            material : Material applied to the extruded component.

        Returns:
            Function will return the handle to the new extruded part
        """

        depth = eval(self.default_length)(depth)

        self.part = self.create_part()
        ref1 = self.sketch

        extrude_part = self.part.CreateExtrudeSolid(ref1, depth)
        self.part.SetProperty("Name", name)
        self.part.SetProperty("Color", material.color)

        sketch_name = name + "_sketch"
        self.sketch.SetProperty("Name", sketch_name)

        self.part = None
        self.sketch = None
        self.doc.SaveModel(True)
        model_name = name + "_model"
        self.model = self.create_model(model_name)

        study_name = name + "_study"
        self.study = self.create_study(study_name, self.study_type, self.model)

        self.set_default_length_unit(self.default_length)
        self.set_default_angle_unit(self.default_angle)

        self.study.SetMaterialByName(name, material.name)
        return extrude_part

    def revolve(self, name, material: str, center, axis, angle: float,) -> any:
        """ Revolves cross-section along an arc

        Args:
            name: Name of the newly revolved component.
            material: Material applied to the component.
            center: center point of rotation. Should be of type Location2d defined with eMach Dimensions.
            axis: Axis of rotation. Should be of type Location2d defined with eMach Dimensions.
                  Specifying negative value reverses the axis of rotation.

        Returns:
             This function will return the handle of the newly revolved part.
        """
        center = eval(self.default_length, center)
        axis = eval(self.default_length, axis)
        angle = eval(self.default_angle, angle)

        self.part = self.create_part()
        ref1 = self.sketch
        revolve_part = self.part.CreateRevolveSolid(ref1)
        self.part.GetItem("Revolve").setProperty("SpecificRatio", 1)
        self.part.GetItem("Revolve").setProperty("AxisType", "1")
        self.part.GetItem("Revolve").setProperty("AxisPosX", center[0])
        self.part.GetItem("Revolve").setProperty("AxisPosY", center[1])
        self.part.GetItem("Revolve").setProperty("AxisVecX", axis[0])
        self.part.GetItem("Revolve").setProperty("AxisVecY", axis[1])
        self.part.GetItem("Revolve").setProperty("AxisVecZ", 0)
        self.part.GetItem("Revolve").setProperty("Angle", angle)
        self.part.SetProperty("Name", name)
        sketch_name = name + "_sketch"
        self.sketch.SetProperty("Name", sketch_name)

        self.part = None
        self.doc.SaveModel(True)
        model_name = name + "_model"
        self.model = self.create_model(model_name)

        study_name = name + "_study"
        self.study = self.create_study(study_name, self.study_type, self.model)

        self.set_default_length_unit(self.default_length)
        self.set_default_angle_unit(self.default_angle)

        self.study.SetMaterialByName(name, material.name)
        return revolve_part

    def set_default_length_unit(self, user_unit):
        """Set the default length unit in JMAG. Only DimMeter supported.

        Args:
            user_unit: String representing the unit the user wishes to set as default.

        Raises:
            TypeError: Incorrect dimension passed
        """
        if user_unit == "DimMeter":
            self.default_length = user_unit
            self.model.SetUnitCollection("SI_units")
        else:
            raise Exception("Unsupported length unit")

    def set_default_angle_unit(self, user_unit):
        """Set the default angular unit in JMAG. Only DimDegree supported.

        Args:
            user_unit: String representing the unit the user wishes to set as default.

        Raises:
            TypeError: Incorrect dimension passed
        """
        if user_unit == "DimDegree":
            self.default_angle = user_unit
            self.model.SetUnitCollection("SI_units")
        else:
            raise Exception("Unsupported angle unit")
        