import os
import numpy as np
import pandas as pd
import sys
from time import time as clock_time
from scipy.optimize import curve_fit
import math

from mach_cad import model_obj as mo
from mach_opt import InvalidDesign
from mach_eval.analyzers.electromagnetic.stator_wdg_res import(
    StatorWindingResistanceProblem, StatorWindingResistanceAnalyzer
)
from mach_cad.tools import jmag as JMAG

class SynR_Opt_Problem:
    def __init__(self, machine, operating_point):
        self.machine = machine
        self.operating_point = operating_point
        self._validate_attr()
        self._check_geom()

    def _validate_attr(self):
        if 'SynR_Machine' in str(type(self.machine)):
            pass
        else:
            raise TypeError("Invalid machine type")

        if 'SynR_Machine_Oper_Pt' in str(type(self.operating_point)):
            pass
        else:
            raise TypeError("Invalid settings type")

    def _check_geom(self):
        x1 = (self.machine.r_ri + self.machine.d_r1 + self.machine.w_b1/2 - self.machine.l_b4/2)*np.cos(np.pi/4)
        y1 = self.machine.l_b1 + self.machine.w_b1/2 + (self.machine.l_b4/2 + self.machine.d_r1 + self.machine.r_ri)*np.cos(np.pi/4)
        r_ro_compare1 = np.sqrt(x1**2 + y1**2)
        x2 = (self.machine.r_ri + self.machine.d_r1 + self.machine.w_b1 + self.machine.d_r2 + self.machine.w_b2/2 - self.machine.l_b5/2)*np.cos(np.pi/4)
        y2 = self.machine.l_b2 + self.machine.w_b2/2 + (self.machine.r_ri + self.machine.d_r1 + self.machine.w_b1 + self.machine.d_r2 + self.machine.l_b5/2)*np.cos(np.pi/4)
        r_ro_compare2 = np.sqrt(x2**2 + y2**2)
        in_rad = (self.machine.r_ri + self.machine.d_r1) * np.cos(np.pi/4)
        out_rad = self.machine.l_b4 / 2 * np.cos(np.pi/4) + self.machine.w_b1/2
        if r_ro_compare1 < 0.975*self.machine.r_ro and r_ro_compare2 < 0.975*self.machine.r_ro and self.machine.l_b4 > 1.25*self.machine.w_b1 and self.machine.l_b5 > 1.25*self.machine.w_b2 and 0.975*in_rad > out_rad:
            print("\nGeometry is valid!")
            print("\n")
        else:
            raise InvalidDesign("Invalid Geometry - Flux Barriers Don't Fit")
        

class SynR_Opt_Analyzer:
    def __init__(self, configuration):
        self.config = configuration

    def analyze(self, problem):
        self.machine_variant = problem.machine
        self.operating_point = problem.operating_point
        self.machine_variant.yield_stress = 300 * 10 ** 6
        
        ####################################################
        # 01 Setting project name and output folder
        ####################################################
        
        self.project_name = self.machine_variant.name
        expected_project_file = self.config.run_folder + "%s_Opt.jproj" % self.project_name
        # Create output folder
        if not os.path.isdir(self.config.jmag_csv_folder):
            os.makedirs(self.config.jmag_csv_folder)

        attempts = 1
        if os.path.exists(expected_project_file):
            print(
                "JMAG project exists already, I will not delete it but create a new one with a different name instead."
            )
            attempts = 2
            temp_path = expected_project_file[
                : -len(".jproj")
            ] + "_attempts_%d.jproj" % (attempts)
            while os.path.exists(temp_path):
                attempts += 1
                temp_path = expected_project_file[
                    : -len(".jproj")
                ] + "_attempts_%d.jproj" % (attempts)

            expected_project_file = temp_path

        if attempts > 1:
            self.project_name = self.project_name + "_attempts_%d" % (attempts)

        toolJmag = JMAG.JmagDesigner()

        toolJmag.visible = self.config.jmag_visible
        toolJmag.open(comp_filepath=expected_project_file, length_unit="DimMillimeter", study_type="StructuralStatic2D")
        toolJmag.save()

        self.study_name = self.project_name + "_Stat_SynR"
        self.design_results_folder = (
            self.config.run_folder + "%s_results/" % self.project_name
        )
        if not os.path.isdir(self.design_results_folder):
            os.makedirs(self.design_results_folder)

        ################################################################
        # 02 Run Structural analysis
        ################################################################

        # Draw cross_section
        draw_success = self.draw_machine(toolJmag)
    
        if not draw_success:
            raise InvalidDesign

        toolJmag.doc.SaveModel(False)
        app = toolJmag.jd
        model = app.GetCurrentModel()

        # Pre-processing
        model.SetName(self.project_name)
        model.SetDescription(self.show(self.project_name, toString=True))

        valid_design = self.pre_process(model)

        if not valid_design:
            raise InvalidDesign

        # Create static study 1
        study1 = self.add_struct_study_1(app, model, self.config.jmag_csv_folder, self.study_name + "_1")
        self.create_custom_material(
            app, self.machine_variant.stator_iron_mat["core_material"]
        )
        app.SetCurrentStudy(self.study_name + "_1")

        # Mesh study
        self.mesh_study(app, model, study1)

        # Run study
        self.run_study(app, study1, clock_time())

        # Create static study 2
        study2 = self.add_struct_study_2(app, model, self.config.jmag_csv_folder, self.study_name + "_2")
        #self.create_custom_material(
        #    app, self.machine_variant.stator_iron_mat["core_material"]
        #)
        app.SetCurrentStudy(self.study_name + "_2")

        # Mesh study
        self.mesh_study(app, model, study2)

        # Run study
        self.run_study(app, study2, clock_time())

        # Create static study 3
        study3 = self.add_struct_study_3(app, model, self.config.jmag_csv_folder, self.study_name + "_3")
        #self.create_custom_material(
        #    app, self.machine_variant.stator_iron_mat["core_material"]
        #)
        app.SetCurrentStudy(self.study_name + "_3")

        # Mesh study
        self.mesh_study(app, model, study3)

        # Run study
        self.run_study(app, study3, clock_time())

        # Create static study 4
        study4 = self.add_struct_study_4(app, model, self.config.jmag_csv_folder, self.study_name + "_4")
        #self.create_custom_material(
        #    app, self.machine_variant.stator_iron_mat["core_material"]
        #)
        app.SetCurrentStudy(self.study_name + "_4")

        # Mesh study
        self.mesh_study(app, model, study4)

        # Run study
        self.run_study(app, study4, clock_time())

        ####################################################
        # 03 Load FEA Struct output
        ####################################################

        fea_rated_output_1 = self.extract_JMAG_results(
            self.config.jmag_csv_folder, self.study_name + "_1"
        )

        fea_rated_output_2 = self.extract_JMAG_results(
            self.config.jmag_csv_folder, self.study_name + "_2"
        )

        fea_rated_output_3 = self.extract_JMAG_results(
            self.config.jmag_csv_folder, self.study_name + "_3"
        )

        fea_rated_output_4 = self.extract_JMAG_results(
            self.config.jmag_csv_folder, self.study_name + "_4"
        )

        struct1 = fea_rated_output_1["max_stress"]
        s1 = struct1['Maximum Value']
        max_stress1 = s1[0]

        struct2 = fea_rated_output_2["max_stress"]
        s2 = struct2['Maximum Value']
        max_stress2 = s2[0]

        struct3 = fea_rated_output_3["max_stress"]
        s3 = struct3['Maximum Value']
        max_stress3 = s3[0]

        struct4 = fea_rated_output_4["max_stress"]
        s4 = struct4['Maximum Value']
        max_stress4 = s4[0]

        def objective(x, a, b):
            return x ** a + b
        
        x = [0, 0.25 * self.operating_point.speed, 0.5 * self.operating_point.speed, 0.75 * self.operating_point.speed, self.operating_point.speed]
        y = [0, max_stress1, max_stress2, max_stress3, max_stress4]

        try:
            popt, _ = curve_fit(objective, x, y)
        except RuntimeError:
            print("RuntimeError - curve_fit failed")
            max_speed = 5000

        a, b = popt
        max_speed = (self.machine_variant.yield_stress - b) ** (1 / a)

        if math.isnan(max_speed) is True:
            print('CURVE FIT FAILURE - CHANGING SPEED TO 5000 RPM')
            max_speed = 5000
        else:
            print('No Error or Warning')
            
        
        self.operating_point.new_speed = max_speed
        max_stress = max_speed ** a + b
        self.machine_variant.max_stress = max_stress

        print("Operating Speed = ", self.operating_point.speed, " RPM",)
        print("Maximum Speed = ", self.operating_point.new_speed, " RPM",)

        ################################################################
        # 04 Run Electromagnetic analysis
        ################################################################

        # Create transient study with two time step sections
        study = self.add_em_study(app, model, self.config.jmag_csv_folder, self.study_name)
        app.SetCurrentStudy(self.study_name)

        # Mesh study
        self.mesh_study(app, model, study)

        self.breakdown_torque = None
        self.stator_slot_area = None

        # Set current excitation
        I = self.I_hat
        phi_0 = self.operating_point.phi_0
        self.set_currents_sequence(I, self.drive_freq,
                phi_0, app, study)
        
        # Add time step settings
        no_of_steps = self.config.no_of_steps
        no_of_rev = self.config.no_of_rev
        time_interval = no_of_rev / (self.drive_freq)
        self.add_time_step_settings(time_interval, no_of_steps, app, study)

        self.run_study(app, study, clock_time())

        toolJmag.save()
        app.Quit()

        ####################################################
        # 05 Load EM FEA output
        ####################################################

        fea_rated_output = self.extract_JMAG_EM_results(
            self.config.jmag_csv_folder, self.study_name
        )

        return fea_rated_output
    
    @property
    def drive_freq(self):
        speed_in_elec_ang = 2 * np.pi * self.operating_point.new_speed / 60 * self.machine_variant.p
        drive_freq = speed_in_elec_ang
        return drive_freq

    @property
    def speed(self):
        return self.operating_point.speed
    
    @property
    def new_speed(self):
        return self.operating_point.new_speed
    
    @property
    def elec_omega(self):
        return 2 * np.pi * self.drive_freq

    @property
    def I_hat(self):
        I_hat = self.machine_variant.rated_current * self.operating_point.current_ratio
        return I_hat

    @property
    def phi_0(self):
        return self.operating_point.phi_0

    @property
    def z_C(self):
        if len(self.machine_variant.layer_phases) == 1:
            z_C = self.machine_variant.Q / 3
        elif len(self.machine_variant.layer_phases) == 2:
            z_C = self.machine_variant.Q / 3

        return z_C

    @property
    def stator_resistance(self):
        res_prob = StatorWindingResistanceProblem(
            r_si=self.machine_variant.r_si/1000,
            d_sp=self.machine_variant.d_sp/1000,
            d_st=self.machine_variant.d_st/1000,
            w_st=self.machine_variant.w_st/1000,
            l_st=self.machine_variant.l_st/1000,
            Q=self.machine_variant.Q,
            y=self.machine_variant.pitch,
            z_Q=self.machine_variant.Z_q,
            z_C=self.z_C,
            Kcu=self.machine_variant.Kcu,
            Kov=self.machine_variant.Kov,
            sigma_cond=self.machine_variant.coil_mat["copper_elec_conductivity"],
            slot_area=self.machine_variant.s_slot*1e-6,
        )
        res_analyzer = StatorWindingResistanceAnalyzer()
        stator_resistance = res_analyzer.analyze(res_prob)
        return stator_resistance

    @property
    def R_wdg(self):
        return self.stator_resistance[0]

    @property
    def R_wdg_coil_ends(self):
        return self.stator_resistance[1]

    @property
    def R_wdg_coil_sides(self):
        return self.stator_resistance[2]


    def draw_machine(self, tool):
        ####################################################
        # Adding parts objects
        ####################################################

        rotor_rotation = mo.DimDegree(-180 / (2 * self.machine_variant.p))
        stator_rotation = mo.DimDegree(-(180+720) / self.machine_variant.Q)

        self.stator_core = mo.CrossSectInnerRotorStatorPartial(
            name="StatorCore",
            dim_alpha_st=mo.DimDegree(self.machine_variant.alpha_st),
            dim_alpha_so=mo.DimDegree(self.machine_variant.alpha_so),
            dim_r_si=mo.DimMillimeter(self.machine_variant.r_si),
            dim_d_so=mo.DimMillimeter(self.machine_variant.d_so),
            dim_d_sp=mo.DimMillimeter(self.machine_variant.d_sp),
            dim_d_st=mo.DimMillimeter(self.machine_variant.d_st),
            dim_d_sy=mo.DimMillimeter(self.machine_variant.d_sy),
            dim_w_st=mo.DimMillimeter(self.machine_variant.w_st),
            dim_r_st=mo.DimMillimeter(0),
            dim_r_sf=mo.DimMillimeter(0),
            dim_r_sb=mo.DimMillimeter(0),
            Q=self.machine_variant.Q,
            location=mo.Location2D(anchor_xy=[mo.DimMillimeter(0), mo.DimMillimeter(0)],
            theta=stator_rotation),
            )

        self.winding_layer1 = mo.CrossSectInnerRotorStatorRightSlot(
            name="WindingLayer1",
            stator_core=self.stator_core,
            location=mo.Location2D(anchor_xy=[mo.DimMillimeter(0), mo.DimMillimeter(0)],
            theta=stator_rotation),
            )

        self.winding_layer2 = mo.CrossSectInnerRotorStatorLeftSlot(
            name="WindingLayer2",
            stator_core=self.stator_core,
            location=mo.Location2D(anchor_xy=[mo.DimMillimeter(0), mo.DimMillimeter(0)],
            theta=stator_rotation),
            )

        self.rotor_core = mo.CrossSectFluxBarrierRotorPartial(
            name="RotorCore",
            dim_alpha_b=mo.DimDegree(self.machine_variant.alpha_b),
            dim_r_ri=mo.DimMillimeter(self.machine_variant.r_ri),
            dim_r_ro=mo.DimMillimeter(self.machine_variant.r_ro),
            dim_r_f1=mo.DimMillimeter(self.machine_variant.r_f1),
            dim_r_f2=mo.DimMillimeter(self.machine_variant.r_f2),
            dim_r_f3=mo.DimMillimeter(self.machine_variant.r_f3),
            dim_d_r1=mo.DimMillimeter(self.machine_variant.d_r1),
            dim_d_r2=mo.DimMillimeter(self.machine_variant.d_r2),
            dim_d_r3=mo.DimMillimeter(self.machine_variant.d_r3),
            dim_w_b1=mo.DimMillimeter(self.machine_variant.w_b1),
            dim_w_b2=mo.DimMillimeter(self.machine_variant.w_b2),
            dim_w_b3=mo.DimMillimeter(self.machine_variant.w_b3),
            dim_l_b1=mo.DimMillimeter(self.machine_variant.l_b1),
            dim_l_b2=mo.DimMillimeter(self.machine_variant.l_b2),
            dim_l_b3=mo.DimMillimeter(self.machine_variant.l_b3),
            dim_l_b4=mo.DimMillimeter(self.machine_variant.l_b4),
            dim_l_b5=mo.DimMillimeter(self.machine_variant.l_b5),
            dim_l_b6=mo.DimMillimeter(self.machine_variant.l_b6),
            p=2,
            location=mo.Location2D(anchor_xy=[mo.DimMillimeter(0), mo.DimMillimeter(0)], 
            theta=rotor_rotation),
            )

        self.shaft = mo.CrossSectHollowCylinder(
            name="Shaft",
            dim_t=mo.DimMillimeter(self.machine_variant.r_ri),
            dim_r_o=mo.DimMillimeter(self.machine_variant.r_ri),
            location=mo.Location2D(anchor_xy=[mo.DimMillimeter(0), mo.DimMillimeter(0)]),
            )


        self.comp_stator_core = mo.Component(
            name="StatorCore",
            cross_sections=[self.stator_core],
            material=mo.MaterialGeneric(name=self.machine_variant.stator_iron_mat["core_material"], color=r"#808080"),
            make_solid=mo.MakeExtrude(location=mo.Location3D(), 
                    dim_depth=mo.DimMillimeter(self.machine_variant.l_st)),
            )

        self.comp_winding_layer1 = mo.Component(
            name="WindingLayer1",
            cross_sections=[self.winding_layer1],
            material=mo.MaterialGeneric(name=self.machine_variant.coil_mat["coil_material"]),
            make_solid=mo.MakeExtrude(location=mo.Location3D(), 
            dim_depth=mo.DimMillimeter(self.machine_variant.l_st)),
            )

        self.comp_winding_layer2 = mo.Component(
            name="WindingLayer2",
            cross_sections=[self.winding_layer2],
            material=mo.MaterialGeneric(name=self.machine_variant.coil_mat["coil_material"]),
            make_solid=mo.MakeExtrude(location=mo.Location3D(), 
            dim_depth=mo.DimMillimeter(self.machine_variant.l_st)),
            )

        self.comp_rotor_core = mo.Component(
            name="RotorCore",
            cross_sections=[self.rotor_core],
            material=mo.MaterialGeneric(name=self.machine_variant.rotor_iron_mat["core_material"], color=r"#808080"),
            make_solid=mo.MakeExtrude(location=mo.Location3D(), 
                    dim_depth=mo.DimMillimeter(self.machine_variant.l_st)),
            )
        
        self.comp_shaft = mo.Component(
            name="Shaft",
            cross_sections=[self.shaft],
            material=mo.MaterialGeneric(name=self.machine_variant.shaft_mat["shaft_material"], color=r"#71797E"),
            make_solid=mo.MakeExtrude(location=mo.Location3D(), 
                    dim_depth=mo.DimMillimeter(self.machine_variant.l_st)),
            )

        tool.bMirror = False

        tool.sketch = tool.create_sketch()
        tool.sketch.SetProperty("Name", self.stator_core.name)
        tool.sketch.SetProperty("Color", r"#808080")
        cs_stator = self.stator_core.draw(tool)
        stator_tool = tool.prepare_section(cs_stator, self.machine_variant.Q)

        tool.sketch = tool.create_sketch()
        tool.sketch.SetProperty("Name", self.winding_layer1.name)
        tool.sketch.SetProperty("Color", r"#B87333")
        cs_winding_layer1 = self.winding_layer1.draw(tool)
        winding_tool1 = tool.prepare_section(cs_winding_layer1, self.machine_variant.Q)
        self.winding_layer1_inner_coord = cs_winding_layer1.inner_coord

        tool.sketch = tool.create_sketch()
        tool.sketch.SetProperty("Name", self.winding_layer2.name)
        tool.sketch.SetProperty("Color", r"#B87333")
        cs_winding_layer2 = self.winding_layer2.draw(tool)
        winding_tool2 = tool.prepare_section(cs_winding_layer2, self.machine_variant.Q)
        self.winding_layer2_inner_coord = cs_winding_layer2.inner_coord

        tool.sketch = tool.create_sketch()
        tool.sketch.SetProperty("Name", self.rotor_core.name)
        tool.sketch.SetProperty("Color", r"#808080")
        cs_rotor_core = self.rotor_core.draw(tool)
        rotor_tool = tool.prepare_section(cs_rotor_core, 2*self.machine_variant.p)

        tool.sketch = tool.create_sketch()
        tool.sketch.SetProperty("Name", self.shaft.name)
        tool.sketch.SetProperty("Color", r"#71797E")
        cs_shaft = self.shaft.draw(tool)
        shaft_tool = tool.prepare_section(cs_shaft)

        return True


    def show(self, name, toString=False):
        attrs = list(vars(self).items())
        key_list = [el[0] for el in attrs]
        val_list = [el[1] for el in attrs]
        the_dict = dict(list(zip(key_list, val_list)))
        sorted_key = sorted(
            key_list,
            key=lambda item: (
                int(item.partition(" ")[0]) if item[0].isdigit() else float("inf"),
                item,
            ),
        )  # this is also useful for string beginning with digiterations '15 Steel'.
        tuple_list = [(key, the_dict[key]) for key in sorted_key]
        if not toString:
            print("- SynR Individual #%s\n\t" % name, end=" ")
            print(", \n\t".join("%s = %s" % item for item in tuple_list))
            return ""
        else:
            return "\n- SynR Individual #%s\n\t" % name + ", \n\t".join(
                "%s = %s" % item for item in tuple_list
            )

    def pre_process(self, model):
        # pre-process : you can select part by coordinate!
        """Group"""

        def group(name, id_list):
            model.GetGroupList().CreateGroup(name)
            for the_id in id_list:
                model.GetGroupList().AddPartToGroup(name, the_id)

        part_ID_list = model.GetPartIDs()

        if len(part_ID_list) != int(
            1 + 1 + self.machine_variant.Q * 2 + 1
        ):
            print("Parts are missing in this machine")
            return False

        self.id_statorCore = id_statorCore = part_ID_list[0]
        partIDRange_Coil = part_ID_list[1 : int(2 * self.machine_variant.Q + 1)]
        self.id_rotorCore = id_rotorCore = part_ID_list[int(2 * self.machine_variant.Q + 1)]
        id_shaft = part_ID_list[-1]   

        group("Coils", partIDRange_Coil)

        """ Add Part to Set for later references """

        def add_part_to_set(name, x, y, ID=None):
            model.GetSetList().CreatePartSet(name)
            model.GetSetList().GetSet(name).SetMatcherType("Selection")
            model.GetSetList().GetSet(name).ClearParts()
            sel = model.GetSetList().GetSet(name).GetSelection()
            if ID is None:
                # print x,y
                sel.SelectPartByPosition(x, y, 0)  # z=0 for 2D
            else:
                sel.SelectPart(ID)
            model.GetSetList().GetSet(name).AddSelected(sel)

        # RotorSet
        add_part_to_set("RotorSet", 0.0, 0.0, ID=id_shaft)

        # Create Set for right layer
        Angle_StatorSlotSpan = 360 / self.machine_variant.Q
        R = np.sqrt(self.winding_layer1_inner_coord[0] ** 2 + self.winding_layer1_inner_coord[1] ** 2)
        THETA = np.arctan(self.winding_layer1_inner_coord[1] / self.winding_layer1_inner_coord[0])
        X = R * np.cos(THETA)
        Y = R * np.sin(THETA)
        count = 0
        for UVW, UpDown in zip(
            self.machine_variant.layer_phases[0], self.machine_variant.layer_polarity[0]
        ):
            count += 1
            add_part_to_set("coil_right_%s%s %d" % (UVW, UpDown, count), X, Y)

            THETA += Angle_StatorSlotSpan / 180.0 * np.pi
            X = R * np.cos(THETA)
            Y = R * np.sin(THETA)

        # Create Set for left layer
        THETA = np.arctan(self.winding_layer2_inner_coord[1] / self.winding_layer2_inner_coord[0])
        X = R * np.cos(THETA)
        Y = R * np.sin(THETA)
        count = 0
        for UVW, UpDown in zip(
            self.machine_variant.layer_phases[1], self.machine_variant.layer_polarity[1]
        ):
            count += 1
            add_part_to_set("coil_left_%s%s %d" % (UVW, UpDown, count), X, Y)

            THETA += Angle_StatorSlotSpan / 180.0 * np.pi
            X = R * np.cos(THETA)
            Y = R * np.sin(THETA)

        # Create Set for Motion Region
        def part_list_set(name, list_part_id=None, prefix=None):
            model.GetSetList().CreatePartSet(name)
            model.GetSetList().GetSet(name).SetMatcherType("Selection")
            model.GetSetList().GetSet(name).ClearParts()
            sel = model.GetSetList().GetSet(name).GetSelection()

            if list_part_id is not None:
                for ID in list_part_id:
                    sel.SelectPart(ID)
            model.GetSetList().GetSet(name).AddSelected(sel)

        part_list_set(
            "Motion_Region", list_part_id=[id_rotorCore, id_shaft]
        )

        return True


    def create_custom_material(self, app, steel_name):

        app.GetMaterialLibrary().CreateCustomMaterial(
            self.machine_variant.stator_iron_mat["core_material"], "Custom Materials"
        )
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue(
            "Density", self.machine_variant.stator_iron_mat["core_material_density"] / 1000
        )
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue("MagneticSteelPermeabilityType", 2)
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue("CoerciveForce", 0)
        BH = np.loadtxt(
            self.machine_variant.stator_iron_mat["core_bh_file"],
            unpack=True,
            usecols=(0, 1),
        )  # values from Nishanth Magnet BH curve
        refarray = BH.T.tolist()
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).GetTable("BhTable").SetTable(refarray)
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue("DemagnetizationCoerciveForce", 0)
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue("MagnetizationSaturated", 0)
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue("MagnetizationSaturated2", 0)
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue("ExtrapolationMethod", 0)
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue("YoungModulus", self.machine_variant.stator_iron_mat["core_youngs_modulus"] / 1000000)
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue("PoissonRatio", self.machine_variant.stator_iron_mat["core_poission_ratio"])
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue("ShearModulus", self.machine_variant.stator_iron_mat["core_youngs_modulus"] / (1000000 * 2 * (1 + self.machine_variant.stator_iron_mat["core_poission_ratio"])))

        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue("Loss_Type", 1)
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue(
            "LossConstantKhX", self.machine_variant.stator_iron_mat["core_ironloss_Kh"]
        )
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue(
            "LossConstantKeX", self.machine_variant.stator_iron_mat["core_ironloss_Ke"]
        )
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue(
            "LossConstantAlphaX",
            self.machine_variant.stator_iron_mat["core_ironloss_a"],
        )
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue(
            "LossConstantBetaX", self.machine_variant.stator_iron_mat["core_ironloss_b"]
        )


    def add_struct_study_1(
        self, app, model, dir_csv_output_folder, study_name
    ):

        model.CreateStudy("StructuralStatic2D", study_name)
        app.SetCurrentStudy(study_name)
        study = model.GetStudy(study_name)

        # Study properties
        study.GetStudyProperties().SetValue(
            "ModelThickness", self.machine_variant.l_st
        )  # [mm] Stack Length

        # Material
        self.add_materials(study)

        # Conditions - Displacement Restraint
        study.CreateCondition("Displacement", "Containment")
        study.GetCondition("Containment").SetXYZPoint("Direction", 0, 0, 1)
        study.GetCondition("Containment").ClearParts()
        study.GetCondition("Containment").AddSet(
            model.GetSetList().GetSet("Motion_Region"), 1
        )

        # Conditions - Centrifugal Force
        study.CreateCondition("CentrifugalForce",
            "RotCon") 
        study.GetCondition("RotCon").SetXYZPoint("Axis", 0, 0, 1) # megbox warning
        study.GetCondition("RotCon").SetValue("AngularVelocity",
            int(self.speed) * 0.25)
        study.GetCondition("RotCon").ClearParts()
        study.GetCondition("RotCon").AddSet(
            model.GetSetList().GetSet("Motion_Region"), 0
        )

        # Conditions - Target Result
        app.SetCurrentStudy(study_name)
        model.GetStudy(study_name).CreateCalculationDefinition("MaxStress")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetResultType("MisesStress", "")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetResultCoordinate("Global Rectangular")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetCalculationType("max")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetDirectionAxis(0, 0, 1)
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").ClearParts()
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").AddSet(
            model.GetSetList().GetSet("Motion_Region"), 0
        )

        # Suppress Stator
        model.GetStudy(study_name).SuppressPart("StatorCore", 1)
        model.GetStudy(study_name).SuppressPart("Coils", 1)

        # True: no mesh or field results are needed
        study.GetStudyProperties().SetValue(
            "OnlyTableResults", self.config.only_table_results
        )

        study.GetStudyProperties().SetValue("DirectSolverType", 1)

        if self.config.multiple_cpus:
            # This SMP(shared memory process) is effective only if there are tons of elements. e.g., over 100,000.
            # too many threads will in turn make them compete with each other and slow down the solve. 2 is good enough
            # for eddy current solve. 6~8 is enough for transient solve.
            study.GetStudyProperties().SetValue("UseMultiCPU", True)
            study.GetStudyProperties().SetValue("MultiCPU", self.config.num_cpus)
            study.GetStudyProperties().SetValue("UseGPU", 1)

        # speed, freq
        # study.GetCondition("RotCon").SetValue("AngularVelocity", "speed")

        # Calculate CSV results
        study.GetStudyProperties().SetValue(
            "CsvOutputPath", dir_csv_output_folder
        )  # it's folder rather than file!
        study.GetStudyProperties().SetValue(self.config.csv_struct_results,1)
        study.GetStudyProperties().SetValue(
            "DeleteResultFiles", self.config.del_results_after_calc
        )

        return study
    

    def add_struct_study_2(
        self, app, model, dir_csv_output_folder, study_name
    ):

        model.CreateStudy("StructuralStatic2D", study_name)
        app.SetCurrentStudy(study_name)
        study = model.GetStudy(study_name)

        # Study properties
        study.GetStudyProperties().SetValue(
            "ModelThickness", self.machine_variant.l_st
        )  # [mm] Stack Length

        # Material
        self.add_materials(study)

        # Conditions - Displacement Restraint
        study.CreateCondition("Displacement", "Containment")
        study.GetCondition("Containment").SetXYZPoint("Direction", 0, 0, 1)
        study.GetCondition("Containment").ClearParts()
        study.GetCondition("Containment").AddSet(
            model.GetSetList().GetSet("Motion_Region"), 1
        )

        # Conditions - Centrifugal Force
        study.CreateCondition("CentrifugalForce",
            "RotCon") 
        study.GetCondition("RotCon").SetXYZPoint("Axis", 0, 0, 1) # megbox warning
        study.GetCondition("RotCon").SetValue("AngularVelocity",
            int(self.speed) * 0.5)
        study.GetCondition("RotCon").ClearParts()
        study.GetCondition("RotCon").AddSet(
            model.GetSetList().GetSet("Motion_Region"), 0
        )

        # Conditions - Target Result
        app.SetCurrentStudy(study_name)
        model.GetStudy(study_name).CreateCalculationDefinition("MaxStress")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetResultType("MisesStress", "")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetResultCoordinate("Global Rectangular")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetCalculationType("max")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetDirectionAxis(0, 0, 1)
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").ClearParts()
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").AddSet(
            model.GetSetList().GetSet("Motion_Region"), 0
        )

        # Suppress Stator
        model.GetStudy(study_name).SuppressPart("StatorCore", 1)
        model.GetStudy(study_name).SuppressPart("Coils", 1)

        # True: no mesh or field results are needed
        study.GetStudyProperties().SetValue(
            "OnlyTableResults", self.config.only_table_results
        )

        study.GetStudyProperties().SetValue("DirectSolverType", 1)

        if self.config.multiple_cpus:
            # This SMP(shared memory process) is effective only if there are tons of elements. e.g., over 100,000.
            # too many threads will in turn make them compete with each other and slow down the solve. 2 is good enough
            # for eddy current solve. 6~8 is enough for transient solve.
            study.GetStudyProperties().SetValue("UseMultiCPU", True)
            study.GetStudyProperties().SetValue("MultiCPU", self.config.num_cpus)

        # speed, freq
        # study.GetCondition("RotCon").SetValue("AngularVelocity", "speed")

        # Calculate CSV results
        study.GetStudyProperties().SetValue(
            "CsvOutputPath", dir_csv_output_folder
        )  # it's folder rather than file!
        study.GetStudyProperties().SetValue(self.config.csv_struct_results,1)
        study.GetStudyProperties().SetValue(
            "DeleteResultFiles", self.config.del_results_after_calc
        )

        return study
    

    def add_struct_study_3(
        self, app, model, dir_csv_output_folder, study_name
    ):

        model.CreateStudy("StructuralStatic2D", study_name)
        app.SetCurrentStudy(study_name)
        study = model.GetStudy(study_name)

        # Study properties
        study.GetStudyProperties().SetValue(
            "ModelThickness", self.machine_variant.l_st
        )  # [mm] Stack Length

        # Material
        self.add_materials(study)

        # Conditions - Displacement Restraint
        study.CreateCondition("Displacement", "Containment")
        study.GetCondition("Containment").SetXYZPoint("Direction", 0, 0, 1)
        study.GetCondition("Containment").ClearParts()
        study.GetCondition("Containment").AddSet(
            model.GetSetList().GetSet("Motion_Region"), 1
        )

        # Conditions - Centrifugal Force
        study.CreateCondition("CentrifugalForce",
            "RotCon") 
        study.GetCondition("RotCon").SetXYZPoint("Axis", 0, 0, 1) # megbox warning
        study.GetCondition("RotCon").SetValue("AngularVelocity",
            int(self.speed) * 0.75)
        study.GetCondition("RotCon").ClearParts()
        study.GetCondition("RotCon").AddSet(
            model.GetSetList().GetSet("Motion_Region"), 0
        )

        # Conditions - Target Result
        app.SetCurrentStudy(study_name)
        model.GetStudy(study_name).CreateCalculationDefinition("MaxStress")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetResultType("MisesStress", "")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetResultCoordinate("Global Rectangular")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetCalculationType("max")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetDirectionAxis(0, 0, 1)
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").ClearParts()
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").AddSet(
            model.GetSetList().GetSet("Motion_Region"), 0
        )

        # Suppress Stator
        model.GetStudy(study_name).SuppressPart("StatorCore", 1)
        model.GetStudy(study_name).SuppressPart("Coils", 1)

        # True: no mesh or field results are needed
        study.GetStudyProperties().SetValue(
            "OnlyTableResults", self.config.only_table_results
        )

        study.GetStudyProperties().SetValue("DirectSolverType", 1)

        if self.config.multiple_cpus:
            # This SMP(shared memory process) is effective only if there are tons of elements. e.g., over 100,000.
            # too many threads will in turn make them compete with each other and slow down the solve. 2 is good enough
            # for eddy current solve. 6~8 is enough for transient solve.
            study.GetStudyProperties().SetValue("UseMultiCPU", True)
            study.GetStudyProperties().SetValue("MultiCPU", self.config.num_cpus)

        # speed, freq
        # study.GetCondition("RotCon").SetValue("AngularVelocity", "speed")

        # Calculate CSV results
        study.GetStudyProperties().SetValue(
            "CsvOutputPath", dir_csv_output_folder
        )  # it's folder rather than file!
        study.GetStudyProperties().SetValue(self.config.csv_struct_results,1)
        study.GetStudyProperties().SetValue(
            "DeleteResultFiles", self.config.del_results_after_calc
        )

        return study
    

    def add_struct_study_4(
        self, app, model, dir_csv_output_folder, study_name
    ):

        model.CreateStudy("StructuralStatic2D", study_name)
        app.SetCurrentStudy(study_name)
        study = model.GetStudy(study_name)

        # Study properties
        study.GetStudyProperties().SetValue(
            "ModelThickness", self.machine_variant.l_st
        )  # [mm] Stack Length

        # Material
        self.add_materials(study)

        # Conditions - Displacement Restraint
        study.CreateCondition("Displacement", "Containment")
        study.GetCondition("Containment").SetXYZPoint("Direction", 0, 0, 1)
        study.GetCondition("Containment").ClearParts()
        study.GetCondition("Containment").AddSet(
            model.GetSetList().GetSet("Motion_Region"), 1
        )

        # Conditions - Centrifugal Force
        study.CreateCondition("CentrifugalForce",
            "RotCon") 
        study.GetCondition("RotCon").SetXYZPoint("Axis", 0, 0, 1) # megbox warning
        study.GetCondition("RotCon").SetValue("AngularVelocity",
            int(self.speed))
        study.GetCondition("RotCon").ClearParts()
        study.GetCondition("RotCon").AddSet(
            model.GetSetList().GetSet("Motion_Region"), 0
        )

        # Conditions - Target Result
        app.SetCurrentStudy(study_name)
        model.GetStudy(study_name).CreateCalculationDefinition("MaxStress")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetResultType("MisesStress", "")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetResultCoordinate("Global Rectangular")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetCalculationType("max")
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").SetDirectionAxis(0, 0, 1)
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").ClearParts()
        model.GetStudy(study_name).GetCalculationDefinition("MaxStress").AddSet(
            model.GetSetList().GetSet("Motion_Region"), 0
        )

        # Suppress Stator
        model.GetStudy(study_name).SuppressPart("StatorCore", 1)
        model.GetStudy(study_name).SuppressPart("Coils", 1)

        # True: no mesh or field results are needed
        study.GetStudyProperties().SetValue(
            "OnlyTableResults", self.config.only_table_results
        )

        study.GetStudyProperties().SetValue("DirectSolverType", 1)

        if self.config.multiple_cpus:
            # This SMP(shared memory process) is effective only if there are tons of elements. e.g., over 100,000.
            # too many threads will in turn make them compete with each other and slow down the solve. 2 is good enough
            # for eddy current solve. 6~8 is enough for transient solve.
            study.GetStudyProperties().SetValue("UseMultiCPU", True)
            study.GetStudyProperties().SetValue("MultiCPU", self.config.num_cpus)

        # speed, freq
        # study.GetCondition("RotCon").SetValue("AngularVelocity", "speed")

        # Calculate CSV results
        study.GetStudyProperties().SetValue(
            "CsvOutputPath", dir_csv_output_folder
        )  # it's folder rather than file!
        study.GetStudyProperties().SetValue(self.config.csv_struct_results,1)
        study.GetStudyProperties().SetValue(
            "DeleteResultFiles", self.config.del_results_after_calc
        )

        return study
    

    def add_em_study(
        self, app, model, dir_csv_output_folder, study_name
    ):

        model.CreateStudy("Transient2D", study_name)
        app.SetCurrentStudy(self.study_name)
        study = model.GetStudy(study_name)

        # Study properties
        study.GetStudyProperties().SetValue("ApproximateTransientAnalysis", 1) # psuedo steady state freq is for PWM drive to use
        study.GetStudyProperties().SetValue("OutputSteadyResultAs1stStep", 0)
        study.GetStudyProperties().SetValue("ConversionType", 0)
        study.GetStudyProperties().SetValue(
            "NonlinearMaxIteration", self.config.max_nonlinear_iterations
        )
        study.GetStudyProperties().SetValue(
            "ModelThickness", self.machine_variant.l_st
        )  # [mm] Stack Length

        # Material
        self.add_materials(study)

        # Conditions - Motion
        study.CreateCondition("RotationMotion",
            "RotCon")
        study.GetCondition("RotCon").SetValue("AngularVelocity",
            int(self.operating_point.new_speed))
        study.GetCondition("RotCon").ClearParts()
        study.GetCondition("RotCon").AddSet(
            model.GetSetList().GetSet("Motion_Region"), 0
        )

        study.CreateCondition(
            "Torque", "TorCon"
        )
        study.GetCondition("TorCon").SetValue("TargetType", 1)
        study.GetCondition("TorCon").SetLinkWithType("LinkedMotion", "RotCon")
        study.GetCondition("TorCon").ClearParts()

        study.CreateCondition("Force", "ForCon")
        study.GetCondition("ForCon").SetValue("TargetType", 1)
        study.GetCondition("ForCon").SetLinkWithType("LinkedMotion", "RotCon")
        study.GetCondition("ForCon").ClearParts()

        # Conditions - FEM Coils & Conductors (i.e. stator/rotor winding)
        self.add_circuit(app, model, study, bool_3PhaseCurrentSource=True)

        # True: no mesh or field results are needed
        study.GetStudyProperties().SetValue(
            "OnlyTableResults", self.config.only_table_results
        )

        study.GetStudyProperties().SetValue("DirectSolverType", 1)

        if self.config.multiple_cpus:
            # This SMP(shared memory process) is effective only if there are tons of elements. e.g., over 100,000.
            # too many threads will in turn make them compete with each other and slow down the solve. 2 is good enough
            # for eddy current solve. 6~8 is enough for transient solve.
            study.GetStudyProperties().SetValue("UseMultiCPU", True)
            study.GetStudyProperties().SetValue("MultiCPU", self.config.num_cpus)

        # two sections of different time step
        no_of_rev = self.config.no_of_rev
        no_of_steps = self.config.no_of_steps
        number_of_total_steps = (
            1 + no_of_steps
        )
        # add equations
        study.GetDesignTable().AddEquation("freq")
        study.GetDesignTable().GetEquation("freq").SetExpression("%g" % self.drive_freq)
        study.GetDesignTable().AddEquation("speed")
        study.GetDesignTable().GetEquation("freq").SetType(0)
        study.GetDesignTable().GetEquation("freq").SetDescription(
            "Excitation Frequency"
        )
        study.GetDesignTable().GetEquation("speed").SetType(1)
        study.GetDesignTable().GetEquation("speed").SetExpression("freq * %d"%(60/(self.machine_variant.p)))
        study.GetDesignTable().GetEquation("speed").SetDescription(
            "mechanical speed of rotor"
        )

        # speed, freq
        study.GetCondition("RotCon").SetValue("AngularVelocity", "speed")
        study.GetStudyProperties().SetValue("ApproximateTransientAnalysis", 1)
        study.GetStudyProperties().SetValue("OutputSteadyResultAs1stStep", 0)

        # Iron Loss Calculation Condition
        # Stator
        if True:
            cond = study.CreateCondition("Ironloss", "IronLossConStator")
            cond.SetValue("RevolutionSpeed", "freq*60/%d" % self.machine_variant.p)
            cond.ClearParts()
            sel = cond.GetSelection()
            sel.SelectPart(self.id_statorCore)
            cond.AddSelected(sel)
            # Use FFT for hysteresis to be consistent with FEMM's results and to have a FFT plot
            cond.SetValue("HysteresisLossCalcType", 1)
            cond.SetValue("PresetType", 3)  # 3:Custom
            # Specify the reference steps yourself because you don't really know what JMAG is doing behind you
            cond.SetValue(
                "StartReferenceStep",
                number_of_total_steps + 1 - no_of_steps / no_of_rev * 0.25,
            )  # 1/4 period in no of steps = no_of_steps / no_of_rev * 0.25
            cond.SetValue("EndReferenceStep", number_of_total_steps)
            cond.SetValue("UseStartReferenceStep", 1)
            cond.SetValue("UseEndReferenceStep", 1)
            cond.SetValue(
                "Cyclicity", 4
            )  # specify reference steps for 1/4 period and extend it to whole period
            cond.SetValue("UseFrequencyOrder", 1)
            cond.SetValue("FrequencyOrder", "1-50")  # Harmonics up to 50th orders
        # Check CSV results for iron loss (You cannot check this for Freq study) # CSV and save space
        study.GetStudyProperties().SetValue(
            "CsvOutputPath", dir_csv_output_folder
        )  # it's folder rather than file!
        study.GetStudyProperties().SetValue("CsvResultTypes", self.config.csv_em_results)
        study.GetStudyProperties().SetValue(
            "DeleteResultFiles", self.config.del_results_after_calc
        )
        study.GetMaterial("Shaft").SetValue("OutputResult", 0)
        study.GetMaterial("Coils").SetValue("OutputResult", 0)


        # Rotor
        if True:
            cond = study.CreateCondition("Ironloss", "IronLossConRotor")
            cond.SetValue("RevolutionSpeed", "freq*60/%d" % self.machine_variant.p)
            cond.ClearParts()
            sel = cond.GetSelection()
            sel.SelectPartByPosition(self.machine_variant.r_sh + 0.1 * self.machine_variant.d_r1, 1, 0)

            cond.AddSelected(sel)
            # Use FFT for hysteresis to be consistent with JMAG's results
            cond.SetValue("HysteresisLossCalcType", 1)
            cond.SetValue("PresetType", 3)
            # Specify the reference steps yourself because you don't really know what JMAG is doing behind you
            cond.SetValue(
                "StartReferenceStep",
                number_of_total_steps + 1 - no_of_steps / no_of_rev * 0.25,
            )  # 1/4 period in no of steps = no_of_steps / no_of_rev * 0.25
            cond.SetValue("EndReferenceStep", number_of_total_steps)
            cond.SetValue("UseStartReferenceStep", 1)
            cond.SetValue("UseEndReferenceStep", 1)
            cond.SetValue(
                "Cyclicity", 4
            )  # specify reference steps for 1/4 period and extend it to whole period
            cond.SetValue("UseFrequencyOrder", 1)
            cond.SetValue("FrequencyOrder", "1-50")  # Harmonics up to 50th orders
        self.study_name = study_name

        return study


    def add_materials(self, study):
        # if 'M19' in self.machine_variant.stator_iron_mat["core_material"]:
        # study.SetMaterialByName(self.comp_stator_core.name, "M-19 Steel Gauge-29")
        # study.GetMaterial(self.comp_stator_core.name).SetValue("Laminated", 1)
        # study.GetMaterial(self.comp_stator_core.name).SetValue("LaminationFactor",
        #     self.machine_variant.stator_iron_mat["core_stacking_factor"])

        # study.SetMaterialByName(self.comp_rotor_core.name, "M-19 Steel Gauge-29")
        # study.GetMaterial(self.comp_rotor_core.name).SetValue("Laminated", 1)
        # study.GetMaterial(self.comp_rotor_core.name).SetValue("LaminationFactor",
        #     self.machine_variant.rotor_iron_mat["core_stacking_factor"])

        study.SetMaterialByName(self.comp_stator_core.name,
            self.machine_variant.stator_iron_mat["core_material"])
        study.GetMaterial(self.comp_stator_core.name).SetValue("Laminated", 1)
        study.GetMaterial(self.comp_stator_core.name).SetValue("LaminationFactor",
            self.machine_variant.stator_iron_mat["core_stacking_factor"])

        study.SetMaterialByName(self.comp_rotor_core.name, 
            self.machine_variant.rotor_iron_mat["core_material"])
        study.GetMaterial(self.comp_rotor_core.name).SetValue("Laminated", 1)
        study.GetMaterial(self.comp_rotor_core.name).SetValue("LaminationFactor",
            self.machine_variant.rotor_iron_mat["core_stacking_factor"])

        study.SetMaterialByName(self.comp_shaft.name,
            self.machine_variant.shaft_mat["shaft_material"])
        study.GetMaterial(self.comp_shaft.name).SetValue("Laminated", 0)
        study.GetMaterial(self.comp_shaft.name).SetValue("EddyCurrentCalculation", 1)

        study.SetMaterialByName(self.comp_winding_layer1.name, 
            self.machine_variant.coil_mat["coil_material"])
        study.GetMaterial(self.comp_shaft.name).SetValue("UserConductivityType", 1)
        

    def add_circuit(self, app, model, study, bool_3PhaseCurrentSource=False):
        def add_mp_circuit(study, turns, Rs, x=10, y=10):
            # Placing coils/phase windings
            coil_name = []
            for i in range(0, 3):
                coil_name.append("coil_" + ['U', 'V', 'W'][i])
                study.GetCircuit().CreateComponent("Coil", 
                    coil_name[i])
                study.GetCircuit().CreateInstance(coil_name[i],
                    x + 4 * i, y)
                study.GetCircuit().GetComponent(coil_name[i]).SetValue("Turn", turns)
                study.GetCircuit().GetComponent(coil_name[i]).SetValue("Resistance", Rs)
                study.GetCircuit().GetInstance(coil_name[i], 0).RotateTo(90)

            self.coil_name = coil_name

            # Connecting all phase windings to a neutral point
            for i in range(0, 2):         
                study.GetCircuit().CreateWire(x + 4 * i, y - 2, x + 4 * (i + 1), y - 2)

            study.GetCircuit().CreateComponent("Ground", "Ground")
            study.GetCircuit().CreateInstance("Ground", x + 8, y - 4)
            
            # Placing current sources
            cs_name = []
            for i in range(0, 3):
                cs_name.append("cs_" + ['U', 'V', 'W'][i])
                study.GetCircuit().CreateComponent("CurrentSource", cs_name[i])
                study.GetCircuit().CreateInstance(cs_name[i], x + 4 * i, y + 4)
                study.GetCircuit().GetInstance(cs_name[i], 0).RotateTo(90)

            self.cs_name = cs_name

            # Terminal Voltage/Circuit Voltage: Check for outputting CSV results
            terminal_name = []
            for i in range(0, 3):
                terminal_name.append("vp_" + ['U', 'V', 'W'][i])
                study.GetCircuit().CreateTerminalLabel(terminal_name[i], x + 4 * i, y + 2)
                study.GetCircuit().CreateComponent("VoltageProbe", terminal_name[i])
                study.GetCircuit().CreateInstance(terminal_name[i], x + 2 + 4 * i, y + 2)
                study.GetCircuit().GetInstance(terminal_name[i], 0).RotateTo(90)

            self.terminal_name = terminal_name

        app.ShowCircuitGrid(True)
        study.CreateCircuit()

        add_mp_circuit(study, self.machine_variant.Z_q, Rs=self.R_wdg)

        for phase_name in ['U', 'V', 'W']:
            study.CreateCondition("FEMCoil", phase_name)
            # link between FEM Coil Condition and Circuit FEM Coil
            condition = study.GetCondition(phase_name)
            condition.SetLink("coil_%s" % (phase_name))
            condition.GetSubCondition("untitled").SetName("delete")

        count = 0  # count indicates which slot the current rightlayer is in.
        index = 0
        dict_dir = {"+": 1, "-": 0}
        coil_pitch = self.machine_variant.pitch  # self.dict_coil_connection[0]
        # select the part (via `Set') to assign the FEM Coil condition
        for UVW, UpDown in zip(
            self.machine_variant.layer_phases[0], self.machine_variant.layer_polarity[0]
        ):

            count += 1
            condition = study.GetCondition(UVW)

            # right layer
            condition.CreateSubCondition("FEMCoilData", "Coil Set Right %d" % count)
            subcondition = condition.GetSubCondition("Coil Set Right %d" % count)
            subcondition.ClearParts()
            subcondition.AddSet(
                model.GetSetList().GetSet(
                    "coil_%s%s%s %d" % ("right_", UVW, UpDown, count)
                ),
                0,
            )  # right layer
            subcondition.SetValue("Direction2D", dict_dir[UpDown])

            # left layer
            if coil_pitch > 0:
                if count + coil_pitch <= self.machine_variant.Q:
                    count_leftlayer = count + coil_pitch
                    index_leftlayer = index + coil_pitch
                else:
                    count_leftlayer = int(count + coil_pitch - self.machine_variant.Q)
                    index_leftlayer = int(index + coil_pitch - self.machine_variant.Q)
            else:
                if count + coil_pitch > 0:
                    count_leftlayer = count + coil_pitch
                    index_leftlayer = index + coil_pitch
                else:
                    count_leftlayer = int(count + coil_pitch + self.machine_variant.Q)
                    index_leftlayer = int(index + coil_pitch + self.machine_variant.Q)

            # Check if it is a distributed windg???
            if self.machine_variant.pitch == 1:
                UVW = self.machine_variant.layer_phases[1][index_leftlayer]
                UpDown = self.machine_variant.layer_polarity[1][index_leftlayer]
            else:
                if self.machine_variant.layer_phases[1][index_leftlayer] != UVW:
                    print("[Warn] Potential bug in your winding layout detected.")
                    raise Exception("Bug in winding layout detected.")
                if UpDown == "+":
                    UpDown = "-"
                else:
                    UpDown = "+"

            condition.CreateSubCondition(
                "FEMCoilData", "Coil Set Left %d" % count_leftlayer
            )
            subcondition = condition.GetSubCondition(
                "Coil Set Left %d" % count_leftlayer
            )
            subcondition.ClearParts()
            subcondition.AddSet(
                model.GetSetList().GetSet(
                    "coil_%s%s%s %d" % ("left_", UVW, UpDown, count_leftlayer)
                ),
                0,
            )  # left layer
            subcondition.SetValue("Direction2D", dict_dir[UpDown])
            index += 1
            # clean up
            for phase_name in ['U', 'V', 'W']:
                condition = study.GetCondition(phase_name)
                condition.RemoveSubCondition("delete")


    def set_currents_sequence(self, I, freq, phi_0, app, study):
        # Setting current values after creating a circuit using "add_mp_circuit" method
        # "freq" variable cannot be used here. So pay extra attention when you 
        # create new case of a different freq.
        for i in range(0, 3):
            func = app.FunctionFactory().Composite()
            f1 = app.FunctionFactory().Sin(I, freq,
                - 360 / 3 * i + phi_0 + 90)
            func.AddFunction(f1)
            study.GetCircuit().GetComponent(self.cs_name[i]).SetFunction(func)


    def add_time_step_settings(self, time_interval, no_of_steps, app, study):

        DM = app.GetDataManager()
        DM.CreatePointArray("point_array/timevsdivision", "SectionStepTable")
        refarray = [[0 for i in range(3)] for j in range(3)]
        refarray[0][0] = 0
        refarray[0][1] = 1
        refarray[0][2] = 50
        refarray[1][0] = time_interval
        refarray[1][1] = no_of_steps
        refarray[1][2] = 50
        DM.GetDataSet("SectionStepTable").SetTable(refarray)
        number_of_total_steps = (
            1 + no_of_steps
        )  # don't forget to modify here!
        study.GetStep().SetValue("Step", number_of_total_steps)
        study.GetStep().SetValue("StepType", 3)
        study.GetStep().SetTableProperty("Division", DM.GetDataSet("SectionStepTable"))


    def mesh_study(self, app, model, study):

        # mesh
        print("------------------Adding mesh")
        self.add_mesh(study, model)

        # Export Image
        app.View().ShowAllAirRegions()
        app.View().ShowMesh()
        app.View().Zoom(3)
        app.View().Pan(-self.machine_variant.r_si / 1000, 0)
        app.ExportImageWithSize(
            self.design_results_folder + self.project_name + "mesh.png", 2000, 2000
        )
        app.View().ShowModel()


    def add_mesh(self, study, model):
        # this is for multi slide planes, which we will not be usin
        refarray = [[0 for i in range(2)] for j in range(1)]
        refarray[0][0] = 3
        refarray[0][1] = 1
        study.GetMeshControl().GetTable("SlideTable2D").SetTable(refarray)

        study.GetMeshControl().SetValue("MeshType", 1)  # make sure this has been exe'd:
        study.GetMeshControl().SetValue(
            "RadialDivision", self.config.airgap_mesh_radial_div
        )  # for air region near which motion occurs
        study.GetMeshControl().SetValue(
            "CircumferentialDivision", self.config.airgap_mesh_circum_div
        )  # 1440) # for air region near which motion occurs
        study.GetMeshControl().SetValue(
            "AirRegionScale", self.config.mesh_air_region_scale
        )  # [Model Length]: Specify a value within (1.05 <= value < 1000)
        study.GetMeshControl().SetValue("MeshSize", self.config.mesh_size)
        study.GetMeshControl().SetValue("AutoAirMeshSize", 0)
        study.GetMeshControl().SetValue(
            "AirMeshSize", self.config.mesh_size_rotor
        )  # mm
        study.GetMeshControl().SetValue("Adaptive", 0)

        study.GetMeshControl().CreateCondition("RotationPeriodicMeshAutomatic", 
                "autoRotMesh") # with this you can choose to set CircumferentialDivision automatically

        study.GetMeshControl().CreateCondition("Part", "ShaftMeshCtrl")
        study.GetMeshControl().GetCondition("ShaftMeshCtrl").SetValue("Size", 1) # 10 mm
        study.GetMeshControl().GetCondition("ShaftMeshCtrl").ClearParts()
        study.GetMeshControl().GetCondition("ShaftMeshCtrl").AddSet(model.GetSetList().GetSet("Motion_Region"), 0)

        def mesh_all_cases(study):
            numCase = study.GetDesignTable().NumCases()
            for case in range(0, numCase):
                study.SetCurrentCase(case)
                if not study.HasMesh():
                    study.CreateMesh()

        mesh_all_cases(study)


    def run_study(self, app, study, toc):
        if not self.config.jmag_scheduler:
            print("-----------------------Running JMAG...")
            study.RunAllCases()
            msg = "Time spent on %s is %g s." % (study.GetName(), clock_time() - toc)
            print(msg)
        else:
            print("Submit to JMAG_Scheduler...")
            job = study.CreateJob()
            job.SetValue("Title", study.GetName())
            job.SetValue("Queued", True)
            job.Submit(False)  # False:CurrentCase, True:AllCases
            # wait and check
        
        app.Save()


    def prepare_section(
        self, list_regions, tool, bMirrorMerge=True, bRotateMerge=True
    ):  # csToken is a list of cross section's token

        def regionCircularPattern360Origin(region, tool, bMerge=True):
            # index is used to define name of region

            Q_float = float(tool.iRotateCopy)  # don't ask me, ask JSOL
            circular_pattern = tool.sketch.CreateRegionCircularPattern()
            circular_pattern.SetProperty("Merge", bMerge)

            ref2 = tool.doc.CreateReferenceFromItem(region)
            circular_pattern.SetPropertyByReference("Region", ref2)
            face_region_string = circular_pattern.GetProperty("Region")

            circular_pattern.SetProperty("CenterType", 2)  # origin I guess

            # print('Copy', Q_float)
            circular_pattern.SetProperty("Angle", "360/%d" % Q_float)
            circular_pattern.SetProperty("Instance", str(Q_float))

        list_region_objects = []
        for idx, list_segments in enumerate(list_regions):
            # Region
            tool.doc.GetSelection().Clear()
            for segment in list_segments:
                tool.doc.GetSelection().Add(tool.sketch.GetItem(segment.draw_token.GetName()))

            tool.sketch.CreateRegions()

            if idx == 0:
                region_object = tool.sketch.GetItem(
                    "Region"
                )  # This is how you get access to the region you create.
            else:
                region_object = tool.sketch.GetItem(
                    "Region.%d" % (idx + 1)
                )  # This is how you get access to the region you create.
            list_region_objects.append(region_object)
        # raise

        for idx, region_object in enumerate(list_region_objects):
            # Mirror
            if tool.bMirror == True:
                if tool.edge4Ref is None:
                    tool.regionMirrorCopy(
                        region_object,
                        edge4Ref=None,
                        symmetryType=2,
                        bMerge=bMirrorMerge,
                    )  # symmetryType=2 means x-axis as ref
                else:
                    tool.regionMirrorCopy(
                        region_object,
                        edge4Ref=tool.edge4ref,
                        symmetryType=None,
                        bMerge=bMirrorMerge,
                    )  # symmetryType=2 means x-axis as ref

            # RotateCopy
            if tool.iRotateCopy != 0:
                regionCircularPattern360Origin(
                    region_object, tool, bMerge=bRotateMerge
                )

        tool.sketch.CloseSketch()
        return list_region_objects

    def extract_JMAG_results(self, path, study_name):
        max_stress_csv_path = path + study_name + "_calculation_MaxStress.csv"
        print(max_stress_csv_path)
        max_stress_df = pd.read_csv(max_stress_csv_path, skiprows=5)
        
        fea_data = {
            "max_stress": max_stress_df,
        }

        return fea_data
    
    def extract_JMAG_EM_results(self, path, study_name):
        current_csv_path = path + study_name + "_circuit_current.csv"
        torque_csv_path = path + study_name + "_torque.csv"
        force_csv_path = path + study_name + "_force.csv"
        iron_loss_path = path + study_name + "_iron_loss_loss.csv"
        hysteresis_loss_path = path + study_name + "_hysteresis_loss_loss.csv"
        eddy_current_loss_path = path + study_name + "_joule_loss_loss.csv"
        ohmic_loss_path = path + study_name + "_joule_loss.csv"

        curr_df = pd.read_csv(current_csv_path, skiprows=6)
        tor_df = pd.read_csv(torque_csv_path, skiprows=6)
        force_df = pd.read_csv(force_csv_path, skiprows=6)
        iron_df = pd.read_csv(iron_loss_path, skiprows=6)
        hyst_df = pd.read_csv(hysteresis_loss_path, skiprows=6)
        eddy_df = pd.read_csv(eddy_current_loss_path, skiprows=6)
        ohmic_df = pd.read_csv(ohmic_loss_path, skiprows=6)

        curr_df = curr_df.set_index("Time(s)")
        tor_df = tor_df.set_index("Time(s)")
        force_df = force_df.set_index("Time(s)")
        eddy_df = eddy_df.set_index("Frequency(Hz)")
        hyst_df = hyst_df.set_index("Frequency(Hz)")
        iron_df = iron_df.set_index("Frequency(Hz)")
        ohmic_df = ohmic_df.set_index("Time(s)")

        fea_data = {
            "current": curr_df,
            "torque": tor_df,
            "force": force_df,
            "iron_loss": iron_df,
            "hysteresis_loss": hyst_df,
            "eddy_current_loss": eddy_df,
            "ohmic_loss": ohmic_df,
            "no_of_steps": self.config.no_of_steps,
            "no_of_rev": self.config.no_of_rev,
            "scale_axial_length": self.config.scale_axial_length,          
            "drive_freq": self.drive_freq,
            "stator_wdg_resistances": [self.R_wdg, self.R_wdg_coil_ends, self.R_wdg_coil_sides],
            "stator_slot_area": self.stator_slot_area,
            "new_speed": self.operating_point.new_speed,
            "max_stress": self.machine_variant.max_stress,
            "yield_stress": self.machine_variant.yield_stress
        }

        return fea_data