from time import time as clock_time
import os
import numpy as np
import pandas as pd
import sys

from eMach.mach_eval.analyzers.electromagnetic.bspm.electrical_analysis import (
    CrossSectInnerNotchedRotor as CrossSectInnerNotchedRotor,
)
from eMach.mach_eval.analyzers.electromagnetic.bspm.electrical_analysis import CrossSectStator as CrossSectStator
from eMach.mach_eval.analyzers.electromagnetic.bspm.electrical_analysis.Location2D import Location2D

sys.path.append(os.path.dirname(__file__) + "/../../../..")
from mach_opt import InvalidDesign


class BSPM_EM_Problem:
    def __init__(self, machine, operating_point):
        self.machine = machine
        self.operating_point = operating_point
        self._validate_attr()

    def _validate_attr(self):
        if 'BSPM_Machine' in str(type(self.machine)):
            pass
        else:
            raise TypeError("Invalid machine type")

        if 'BSPM_Machine_Oper_Pt' in str(type(self.operating_point)):
            pass
        else:
            raise TypeError("Invalid settings type")


class BSPM_EM_Analyzer:
    def __init__(self, configuration):
        self.config = configuration

    def analyze(self, problem):
        self.machine_variant = problem.machine
        self.operating_point = problem.operating_point
        ####################################################
        # 01 Setting project name and output folder
        ####################################################
        self.project_name = self.machine_variant.name

        expected_project_file = self.config.run_folder + "%s.jproj" % self.project_name

        # Create output folder
        if not os.path.isdir(self.config.jmag_csv_folder):
            os.makedirs(self.config.jmag_csv_folder)

        from .electrical_analysis.JMAG import JMAG

        toolJd = JMAG(self.config)

        JMAG_exist = os.path.exists("C:/Program Files/JMAG-Designer%s" % self.config.jmag_version)
        if JMAG_exist is True:
            app, attempts = toolJd.open(expected_project_file, self.config.jmag_version)
        else:
            print('WARNING: The JMAG version does not exist, defaulting to newest JMAG version available!')
            app, attempts = toolJd.open(expected_project_file)

        if attempts > 1:
            self.project_name = self.project_name + "attempts_%d" % (attempts)

        self.study_name = self.project_name + "TranPMSM"
        self.design_results_folder = (
            self.config.run_folder + "%sresults/" % self.project_name
        )
        if not os.path.isdir(self.design_results_folder):
            os.makedirs(self.design_results_folder)
        ################################################################
        # 02 Run ElectroMagnetic analysis
        ################################################################
        self.create_custom_material(
            app, self.machine_variant.stator_iron_mat["core_material"]
        )
        # Draw cross_section
        draw_success = self.draw_machine(toolJd)
        if not draw_success:
            raise InvalidDesign
        # Import Model into Designer
        toolJd.doc.SaveModel(False)  # True: Project is also saved.
        model = toolJd.app.GetCurrentModel()
        model.SetName(self.project_name)
        model.SetDescription(self.show(self.project_name, toString=True))
        # Add study and run
        valid_design = self.pre_process(app, model)
        if not valid_design:
            raise InvalidDesign
        study = self.add_magnetic_transient_study(
            app, model, self.config.jmag_csv_folder, self.study_name
        )  # Change here and there
        self.mesh_study(app, model, study)
        self.run_study(app, study, clock_time())
        # export Voltage if field data exists.
        if not self.config.del_results_after_calc:
            # Export Circuit Voltage
            ref1 = app.GetDataManager().GetDataSet("Circuit Voltage")
            app.GetDataManager().CreateGraphModel(ref1)
            app.GetDataManager().GetGraphModel("Circuit Voltage").WriteTable(
                self.config.jmag_csv_folder
                + self.study_name
                + "_EXPORT_CIRCUIT_VOLTAGE.csv"
            )
        toolJd.close()
        ####################################################
        # 03 Load FEA output
        ####################################################

        fea_rated_output = self.extract_JMAG_results(
            self.config.jmag_csv_folder, self.study_name
        )

        return fea_rated_output

    def initial_excitation_bias_compensation_deg(self):
        return self.machine_variant.phase_current_offset

    @property
    def current_trms(self):
        return 2 * self.operating_point.Iq * self.machine_variant.Rated_current

    @property
    def current_srms(self):
        return self.operating_point.Iy * self.machine_variant.Rated_current

    @property
    def excitation_freq(self):
        return self.operating_point.speed * self.machine_variant.p / 60

    @property
    def l_coil(self):
        tau_u = (2 * np.pi / self.machine_variant.Q) * (
            self.machine_variant.r_si
            + self.machine_variant.d_sp
            + self.machine_variant.d_st / 2
        )
        l_ew = np.pi * 0.5 * (
            tau_u + self.machine_variant.w_st
        ) / 2 + tau_u * self.machine_variant.Kov * (self.machine_variant.pitch - 1)
        l_coil = 2 * (self.machine_variant.l_st + l_ew)  # length of one coil
        return l_coil

    @property
    def R_coil(self):
        a_wire = (self.machine_variant.s_slot * self.machine_variant.Kcu) / (
            self.machine_variant.no_of_layers * self.machine_variant.Z_q
        )
        return (self.l_coil * self.machine_variant.Z_q) / (
            self.machine_variant.coil_mat["copper_elec_conductivity"] * a_wire
        )

    @property
    def R_wdg(self):
        return (self.R_coil * self.z_C)

    @property
    def m(self):
        m = len(self.machine_variant.coil_groups)
        return m

    @property
    def z_C(self):
        if self.machine_variant.no_of_layers == 1:
            z_C = self.machine_variant.Q / (2 * self.m)
        elif self.machine_variant.no_of_layers == 2:
            z_C = self.machine_variant.Q / (self.m)
        else:
            raise InvalidDesign(message="The number of winding layers must be 1 or 2")
            
        return z_C

    @property
    def copper_loss(self):
        copper_loss_per_phase = (
            ((self.current_trms / 2) ** 2 + self.current_srms ** 2) * self.R_wdg
        )

        copper_loss = self.m * copper_loss_per_phase
        return copper_loss

    def draw_machine(self, toolJd):
        ####################################################
        # Adding parts object
        ####################################################
        self.rotorCore = CrossSectInnerNotchedRotor.CrossSectInnerNotchedRotor(
            name="NotchedRotor",
            mm_d_m=self.machine_variant.d_m * 1e3,
            deg_alpha_m=self.machine_variant.alpha_m,  # angular span of the pole: class type DimAngular
            deg_alpha_ms=self.machine_variant.alpha_ms,  # segment span: class type DimAngular
            mm_d_ri=self.machine_variant.d_ri
            * 1e3,  # inner radius of rotor: class type DimLinear
            mm_r_sh=self.machine_variant.r_sh
            * 1e3,  # rotor iron thickness: class type DimLinear
            mm_d_mp=self.machine_variant.d_mp
            * 1e3,  # inter polar iron thickness: class type DimLinear
            mm_d_ms=self.machine_variant.d_ms
            * 1e3,  # inter segment iron thickness: class type DimLinear
            p=self.machine_variant.p,  # Set pole-pairs to 2
            s=self.machine_variant.n_m,  # Set magnet segments/pole to 4
            location=Location2D(anchor_xy=[0, 0], deg_theta=0),
        )

        self.shaft = CrossSectInnerNotchedRotor.CrossSectShaft(
            name="Shaft", notched_rotor=self.rotorCore
        )

        self.rotorMagnet = CrossSectInnerNotchedRotor.CrossSectInnerNotchedMagnet(
            name="RotorMagnet", notched_rotor=self.rotorCore
        )

        self.stator_core = CrossSectStator.CrossSectInnerRotorStator(
            name="StatorCore",
            deg_alpha_st=self.machine_variant.alpha_st,
            deg_alpha_so=self.machine_variant.alpha_so,
            mm_r_si=self.machine_variant.r_si * 1e3,
            mm_d_so=self.machine_variant.d_so * 1e3,
            mm_d_sp=self.machine_variant.d_sp * 1e3,
            mm_d_st=self.machine_variant.d_st * 1e3,
            mm_d_sy=self.machine_variant.d_sy * 1e3,
            mm_w_st=self.machine_variant.w_st * 1e3,
            mm_r_st=0,  # dummy
            mm_r_sf=0,  # dummy
            mm_r_sb=0,  # dummy
            Q=self.machine_variant.Q,
            location=Location2D(anchor_xy=[0, 0], deg_theta=0),
        )

        self.coils = CrossSectStator.CrossSectInnerRotorStatorWinding(
            name="Coils", stator_core=self.stator_core
        )
        ####################################################
        # Drawing parts
        ####################################################
        # Rotor Core
        list_segments = self.rotorCore.draw(toolJd)
        toolJd.bMirror = False
        toolJd.iRotateCopy = self.rotorMagnet.notched_rotor.p * 2
        try:
            region1 = toolJd.prepareSection(list_segments)
        except:
            return False

        # Shaft
        list_segments = self.shaft.draw(toolJd)
        toolJd.bMirror = False
        toolJd.iRotateCopy = 1
        region0 = toolJd.prepareSection(list_segments)

        # Rotor Magnet
        list_regions = self.rotorMagnet.draw(toolJd)
        toolJd.bMirror = False
        toolJd.iRotateCopy = self.rotorMagnet.notched_rotor.p * 2
        region2 = toolJd.prepareSection(list_regions, bRotateMerge=False)

        # Sleeve
        # sleeve = CrossSectInnerNotchedRotor.CrossSectSleeve(
        #     name='Sleeve',
        #     notched_magnet=self.rotorMagnet,
        #     d_sleeve=self.machine_variant.d_sl * 1e3  # mm
        # )
        # list_regions = sleeve.draw(toolJd)
        # toolJd.bMirror = False
        # toolJd.iRotateCopy = self.rotorMagnet.notched_rotor.p * 2
        # try:
        #     regionS = toolJd.prepareSection(list_regions)
        # except:
        #     return False

        # Stator Core
        list_regions = self.stator_core.draw(toolJd)
        toolJd.bMirror = True
        toolJd.iRotateCopy = self.stator_core.Q
        region3 = toolJd.prepareSection(list_regions)

        # Stator Winding
        list_regions = self.coils.draw(toolJd)
        toolJd.bMirror = False
        toolJd.iRotateCopy = self.coils.stator_core.Q
        region4 = toolJd.prepareSection(list_regions)

        return True

    def pre_process(self, app, model):
        # pre-process : you can select part by coordinate!
        """Group"""

        def group(name, id_list):
            model.GetGroupList().CreateGroup(name)
            for the_id in id_list:
                model.GetGroupList().AddPartToGroup(name, the_id)
                # model.GetGroupList().AddPartToGroup(name, name) #<- this also works

        part_ID_list = model.GetPartIDs()

        if len(part_ID_list) != int(
            1 + 1 + self.machine_variant.p * 2 + 1 + self.machine_variant.Q * 2
        ):
            print("Parts are missing in this machine")
            return False

        self.id_backiron = id_backiron = part_ID_list[0]
        id_shaft = part_ID_list[1]
        partIDRange_Magnet = part_ID_list[2 : int(2 + self.machine_variant.p * 2)]
        # id_sleeve = part_ID_list[int(2 + self.machine_variant.p * 2)]
        id_statorCore = part_ID_list[int(2 + self.machine_variant.p * 2) + 1]
        partIDRange_Coil = part_ID_list[
            int(1 + self.machine_variant.p * 2)
            + 2 : int(2 + self.machine_variant.p * 2)
            + 2
            + int(self.machine_variant.Q * 2)
        ]

        # model.SuppressPart(id_sleeve, 1)

        group("Magnet", partIDRange_Magnet)
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

        # Shaft
        add_part_to_set("ShaftSet", 0.0, 0.0, ID=id_shaft)

        # Create Set for right layer
        Angle_StatorSlotSpan = 360 / self.machine_variant.Q
        # R = self.r_si + self.d_sp + self.d_st *0.5 # this is not generally working (JMAG selects stator core instead.)
        # THETA = 0.25*(Angle_StatorSlotSpan)/180.*np.pi
        R = np.sqrt(self.coils.PCoil[0] ** 2 + self.coils.PCoil[1] ** 2)
        THETA = np.arctan(self.coils.PCoil[1] / self.coils.PCoil[0])
        X = R * np.cos(THETA)
        Y = R * np.sin(THETA)
        count = 0
        for UVW, UpDown in zip(
            self.machine_variant.layer_phases[0], self.machine_variant.layer_polarity[0]
        ):
            count += 1
            add_part_to_set("coil_right_%s%s %d" % (UVW, UpDown, count), X, Y)

            # print(X, Y, THETA)
            THETA += Angle_StatorSlotSpan / 180.0 * np.pi
            X = R * np.cos(THETA)
            Y = R * np.sin(THETA)

        # Create Set for left layer
        THETA = (
            np.arctan(-self.coils.PCoil[1] / self.coils.PCoil[0])
            + (2 * np.pi) / self.machine_variant.Q
        )
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

        # Create Set for Magnets
        R = (
            self.machine_variant.r_si
            - self.machine_variant.delta_e
            - 0.5 * self.machine_variant.d_m
        ) * 1e3
        Angle_RotorSlotSpan = 360 / (self.machine_variant.p * 2)
        THETA = 0.5 * self.machine_variant.alpha_m / 180 * np.pi  # initial position
        X = R * np.cos(THETA)
        Y = R * np.sin(THETA)
        list_xy_magnets = []
        for ind in range(int(self.machine_variant.p * 2)):
            natural_ind = ind + 1
            add_part_to_set("Magnet %d" % (natural_ind), X, Y)
            list_xy_magnets.append([X, Y])

            THETA += Angle_RotorSlotSpan / 180.0 * np.pi
            X = R * np.cos(THETA)
            Y = R * np.sin(THETA)

        # Create Set for Motion Region
        def part_list_set(name, list_xy, list_part_id=None, prefix=None):
            model.GetSetList().CreatePartSet(name)
            model.GetSetList().GetSet(name).SetMatcherType("Selection")
            model.GetSetList().GetSet(name).ClearParts()
            sel = model.GetSetList().GetSet(name).GetSelection()
            for xy in list_xy:
                sel.SelectPartByPosition(xy[0], xy[1], 0)  # z=0 for 2D
            if list_part_id is not None:
                for ID in list_part_id:
                    sel.SelectPart(ID)
            model.GetSetList().GetSet(name).AddSelected(sel)

        part_list_set(
            "Motion_Region", list_xy_magnets, list_part_id=[id_backiron, id_shaft]
        )

        part_list_set("MagnetSet", list_xy_magnets)
        return True

    def add_magnetic_transient_study(
        self, app, model, dir_csv_output_folder, study_name
    ):
        model.CreateStudy("Transient2D", study_name)
        app.SetCurrentStudy(study_name)
        study = model.GetStudy(study_name)

        study.GetStudyProperties().SetValue("ConversionType", 0)
        study.GetStudyProperties().SetValue(
            "NonlinearMaxIteration", self.config.max_nonlinear_iterations
        )
        study.GetStudyProperties().SetValue(
            "ModelThickness", self.machine_variant.l_st * 1e3
        )  # [mm] Stack Length

        # Material
        self.add_material(study)

        # Conditions - Motion
        self.the_speed = self.excitation_freq * 60.0 / self.machine_variant.p  # rpm
        study.CreateCondition(
            "RotationMotion", "RotCon"
        )  # study.GetCondition(u"RotCon").SetXYZPoint(u"", 0, 0, 1) # megbox warning
        print("Speed in RPM", self.the_speed)
        study.GetCondition("RotCon").SetValue("AngularVelocity", int(self.the_speed))
        study.GetCondition("RotCon").ClearParts()
        study.GetCondition("RotCon").AddSet(
            model.GetSetList().GetSet("Motion_Region"), 0
        )
        # Implementation of id=0 control:
        #   d-axis initial position is self.alpha_m*0.5
        #   The U-phase current is sin(omega_syn*t) = 0 at t=0.
        study.GetCondition("RotCon").SetValue(
            "InitialRotationAngle",
            -self.machine_variant.alpha_m * 0.5
            + 90
            + self.initial_excitation_bias_compensation_deg()
            + (180 / self.machine_variant.p),
        )
        # add 360/(2p) deg to reverse the initial magnetizing direction to make torque positive.

        study.CreateCondition(
            "Torque", "TorCon"
        )  # study.GetCondition(u"TorCon").SetXYZPoint(u"", 0, 0, 0) # megbox warning
        study.GetCondition("TorCon").SetValue("TargetType", 1)
        study.GetCondition("TorCon").SetLinkWithType("LinkedMotion", "RotCon")
        study.GetCondition("TorCon").ClearParts()

        study.CreateCondition("Force", "ForCon")
        study.GetCondition("ForCon").SetValue("TargetType", 1)
        study.GetCondition("ForCon").SetLinkWithType("LinkedMotion", "RotCon")
        study.GetCondition("ForCon").ClearParts()

        # Conditions - FEM Coils & Conductors (i.e. stator/rotor winding)
        self.add_circuit(app, model, study, bool_3PhaseCurrentSource=False)

        # True: no mesh or field results are needed
        study.GetStudyProperties().SetValue(
            "OnlyTableResults", self.config.only_table_results
        )

        # this can be said to be super fast over ICCG solver.
        # https://www2.jmag-international.com/support/en/pdf/JMAG-Designer_Ver.17.1_ENv3.pdf
        study.GetStudyProperties().SetValue("DirectSolverType", 1)

        if self.config.multiple_cpus:
            # This SMP(shared memory process) is effective only if there are tons of elements. e.g., over 100,000.
            # too many threads will in turn make them compete with each other and slow down the solve. 2 is good enough
            # for eddy current solve. 6~8 is enough for transient solve.
            study.GetStudyProperties().SetValue("UseMultiCPU", True)
            study.GetStudyProperties().SetValue("MultiCPU", self.config.num_cpus)

        # two sections of different time step
        number_of_revolution_1TS = self.config.no_of_rev_1TS
        number_of_revolution_2TS = self.config.no_of_rev_2TS
        number_of_steps_1TS = (
            self.config.no_of_steps_per_rev_1TS * number_of_revolution_1TS
        )
        number_of_steps_2TS = (
            self.config.no_of_steps_per_rev_2TS * number_of_revolution_2TS
        )
        DM = app.GetDataManager()
        DM.CreatePointArray("point_array/timevsdivision", "SectionStepTable")
        refarray = [[0 for i in range(3)] for j in range(3)]
        refarray[0][0] = 0
        refarray[0][1] = 1
        refarray[0][2] = 50
        refarray[1][0] = number_of_revolution_1TS / self.excitation_freq
        refarray[1][1] = number_of_steps_1TS
        refarray[1][2] = 50
        refarray[2][0] = (
            number_of_revolution_1TS + number_of_revolution_2TS
        ) / self.excitation_freq
        refarray[2][1] = number_of_steps_2TS  # number_of_steps_2TS
        refarray[2][2] = 50
        DM.GetDataSet("SectionStepTable").SetTable(refarray)
        number_of_total_steps = (
            1 + number_of_steps_1TS + number_of_steps_2TS
        )  # don't forget to modify here!
        study.GetStep().SetValue("Step", number_of_total_steps)
        study.GetStep().SetValue("StepType", 3)
        study.GetStep().SetTableProperty("Division", DM.GetDataSet("SectionStepTable"))

        # add equations
        study.GetDesignTable().AddEquation("freq")
        study.GetDesignTable().AddEquation("speed")
        study.GetDesignTable().GetEquation("freq").SetType(0)
        study.GetDesignTable().GetEquation("freq").SetExpression(
            "%g" % self.excitation_freq
        )
        study.GetDesignTable().GetEquation("freq").SetDescription(
            "Excitation Frequency"
        )
        study.GetDesignTable().GetEquation("speed").SetType(1)
        study.GetDesignTable().GetEquation("speed").SetExpression(
            "freq * %d" % (60 / self.machine_variant.p)
        )
        study.GetDesignTable().GetEquation("speed").SetDescription(
            "mechanical speed of four pole"
        )

        # speed, freq, slip
        study.GetCondition("RotCon").SetValue("AngularVelocity", "speed")

        # Iron Loss Calculation Condition
        # Stator
        if True:
            cond = study.CreateCondition("Ironloss", "IronLossConStator")
            cond.SetValue("RevolutionSpeed", "freq*60/%d" % self.machine_variant.p)
            cond.ClearParts()
            sel = cond.GetSelection()
            EPS = 1e-2  # unit: mm
            sel.SelectPartByPosition(self.machine_variant.r_si * 1e3 + EPS, EPS, 0)
            cond.AddSelected(sel)
            # Use FFT for hysteresis to be consistent with FEMM's results and to have a FFT plot
            cond.SetValue("HysteresisLossCalcType", 1)
            cond.SetValue("PresetType", 3)  # 3:Custom
            # Specify the reference steps yourself because you don't really know what JMAG is doing behind you
            cond.SetValue(
                "StartReferenceStep",
                number_of_total_steps + 1 - number_of_steps_2TS * 0.5,
            )  # 1/4 period = number_of_steps_2TS*0.5
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
        study.GetStudyProperties().SetValue("CsvResultTypes", self.config.csv_results)
        study.GetStudyProperties().SetValue(
            "DeleteResultFiles", self.config.del_results_after_calc
        )

        # Rotor
        if True:
            cond = study.CreateCondition("Ironloss", "IronLossConRotor")
            cond.SetValue("BasicFrequencyType", 2)
            cond.SetValue("BasicFrequency", "freq")
            # cond.SetValue(u"BasicFrequency", u"slip*freq") # this require the signal length to be at least 1/4 of
            # slip period, that's too long!
            cond.ClearParts()
            sel = cond.GetSelection()
            sel.SelectPart(self.id_backiron)

            cond.AddSelected(sel)
            # Use FFT for hysteresis to be consistent with FEMM's results
            cond.SetValue("HysteresisLossCalcType", 1)
            cond.SetValue("PresetType", 3)
            # Specify the reference steps yourself because you don't really know what JMAG is doing behind you
            cond.SetValue(
                "StartReferenceStep",
                number_of_total_steps + 1 - number_of_steps_2TS * 0.5,
            )  # 1/4 period = number_of_steps_2TS*0.5
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

    def add_mesh(self, study, model):
        # this is for multi slide planes, which we will not be usin
        refarray = [[0 for i in range(2)] for j in range(1)]
        refarray[0][0] = 3
        refarray[0][1] = 1
        study.GetMeshControl().GetTable("SlideTable2D").SetTable(refarray)

        study.GetMeshControl().SetValue("MeshType", 1)  # make sure this has been exe'd:
        # study.GetCondition(u"RotCon").AddSet(model.GetSetList().GetSet(u"Motion_Region"), 0)
        study.GetMeshControl().SetValue(
            "RadialDivision", self.config.airgap_mesh_radial_div
        )  # for air region near which motion occurs
        study.GetMeshControl().SetValue(
            "CircumferentialDivision", self.config.airgap_mesh_circum_div
        )  # 1440) # for air region near which motion occurs
        study.GetMeshControl().SetValue(
            "AirRegionScale", self.config.mesh_air_region_scale
        )  # [Model Length]: Specify a value within (1.05 <= value < 1000)
        study.GetMeshControl().SetValue("MeshSize", self.config.mesh_size * 1e3)  # mm
        study.GetMeshControl().SetValue("AutoAirMeshSize", 0)
        study.GetMeshControl().SetValue(
            "AirMeshSize", self.config.mesh_size * 1e3
        )  # mm
        study.GetMeshControl().SetValue("Adaptive", 0)

        # This is not neccessary for whole model FEA. In fact, for BPMSM simulation, it causes mesh error "The copy
        # target region is not found".
        # study.GetMeshControl().CreateCondition("RotationPeriodicMeshAutomatic", "autoRotMesh") with this you can
        # choose to set CircumferentialDivision automatically

        study.GetMeshControl().CreateCondition("Part", "MagnetMeshCtrl")
        study.GetMeshControl().GetCondition("MagnetMeshCtrl").SetValue(
            "Size", self.config.magnet_mesh_size * 1e3
        )  # mm
        study.GetMeshControl().GetCondition("MagnetMeshCtrl").ClearParts()
        study.GetMeshControl().GetCondition("MagnetMeshCtrl").AddSet(
            model.GetSetList().GetSet("MagnetSet"), 0
        )

        def mesh_all_cases(study):
            numCase = study.GetDesignTable().NumCases()
            for case in range(0, numCase):
                study.SetCurrentCase(case)
                if not study.HasMesh():
                    study.CreateMesh()

        mesh_all_cases(study)

    def create_custom_material(self, app, steel_name):

        core_mat_obj = app.GetMaterialLibrary().GetCustomMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        )
        app.GetMaterialLibrary().DeleteCustomMaterialByObject(core_mat_obj)

        app.GetMaterialLibrary().CreateCustomMaterial(
            self.machine_variant.stator_iron_mat["core_material"], "Custom Materials"
        )
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue(
            "Density", self.machine_variant.stator_iron_mat["core_material_density"]
        )
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue("MagneticSteelPermeabilityType", 2)
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue("CoerciveForce", 0)
        # app.GetMaterialLibrary().GetUserMaterial(u"Arnon5-final").GetTable("BhTable").SetName(u"SmoothZeroPointOne")
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
        ).SetValue("ExtrapolationMethod", 1)
        app.GetMaterialLibrary().GetUserMaterial(
            self.machine_variant.stator_iron_mat["core_material"]
        ).SetValue(
            "YoungModulus", self.machine_variant.stator_iron_mat["core_youngs_modulus"]
        )
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

    def add_material(self, study):
        study.SetMaterialByName(
            "StatorCore", self.machine_variant.stator_iron_mat["core_material"]
        )
        study.GetMaterial("StatorCore").SetValue("Laminated", 1)
        study.GetMaterial("StatorCore").SetValue(
            "LaminationFactor",
            self.machine_variant.stator_iron_mat["core_stacking_factor"],
        )

        study.SetMaterialByName(
            "NotchedRotor", self.machine_variant.stator_iron_mat["core_material"]
        )
        study.GetMaterial("NotchedRotor").SetValue("Laminated", 1)
        study.GetMaterial("NotchedRotor").SetValue(
            "LaminationFactor",
            self.machine_variant.stator_iron_mat["core_stacking_factor"],
        )

        study.SetMaterialByName(
            "Shaft", self.machine_variant.shaft_mat["shaft_material"]
        )
        study.GetMaterial("Shaft").SetValue("Laminated", 0)
        study.GetMaterial("Shaft").SetValue("EddyCurrentCalculation", 1)

        study.SetMaterialByName("Coils", "Copper")
        study.GetMaterial("Coils").SetValue("UserConductivityType", 1)

        study.SetMaterialByName(
            "Magnet", "{}".format(self.machine_variant.magnet_mat["magnet_material"])
        )
        study.GetMaterial("Magnet").SetValue("EddyCurrentCalculation", 1)
        study.GetMaterial("Magnet").SetValue(
            "Temperature", self.operating_point.ambient_temp + self.operating_point.rotor_temp_rise
        )  # TEMPERATURE (There is no 75 deg C option)

        study.GetMaterial("Magnet").SetValue("Poles", 2 * self.machine_variant.p)

        study.GetMaterial("Magnet").SetDirectionXYZ(1, 0, 0)
        study.GetMaterial("Magnet").SetAxisXYZ(0, 0, 1)
        study.GetMaterial("Magnet").SetOriginXYZ(0, 0, 0)
        study.GetMaterial("Magnet").SetPattern("ParallelCircular")
        study.GetMaterial("Magnet").SetValue(
            "StartAngle", 0.5 * self.machine_variant.alpha_m
        )

    def add_circuit(self, app, model, study, bool_3PhaseCurrentSource=True):
        # Circuit - Current Source
        app.ShowCircuitGrid(True)
        study.CreateCircuit()

        # 4 pole motor Qs=24 dpnv implemented by two layer winding (6 coils). In this case, drive winding has the same
        # slot turns as bearing winding
        def circuit(poles, turns, Rs, ampT, ampS, freq, x=10, y=10):
            # Star Connection_2 is GroupAC
            # Star Connection_4 is GroupBD

            # placing Coils
            y_offset = 0
            study.GetCircuit().CreateComponent("Coil", "coil_Ua")
            study.GetCircuit().CreateInstance("coil_Ua", x - 4, y + y_offset + 6)
            study.GetCircuit().GetComponent("coil_Ua").SetValue("Turn", turns)
            study.GetCircuit().GetComponent("coil_Ua").SetValue("Resistance", Rs)
            study.GetCircuit().GetInstance("coil_Ua", 0).RotateTo(90)

            study.GetCircuit().CreateComponent("Coil", "coil_Ub")
            study.GetCircuit().CreateInstance("coil_Ub", x, y + y_offset + 6)
            study.GetCircuit().GetComponent("coil_Ub").SetValue("Turn", turns)
            study.GetCircuit().GetComponent("coil_Ub").SetValue("Resistance", Rs)
            study.GetCircuit().GetInstance("coil_Ub", 0).RotateTo(90)

            study.GetCircuit().CreateComponent("Coil", "coil_Va")
            study.GetCircuit().CreateInstance("coil_Va", x + 10, y + y_offset - 6)
            study.GetCircuit().GetComponent("coil_Va").SetValue("Turn", turns)
            study.GetCircuit().GetComponent("coil_Va").SetValue("Resistance", Rs)
            study.GetCircuit().GetInstance("coil_Va", 0).RotateTo(270)

            study.GetCircuit().CreateComponent("Coil", "coil_Vb")
            study.GetCircuit().CreateInstance("coil_Vb", x + 6, y + y_offset - 6)
            study.GetCircuit().GetComponent("coil_Vb").SetValue("Turn", turns)
            study.GetCircuit().GetComponent("coil_Vb").SetValue("Resistance", Rs)
            study.GetCircuit().GetInstance("coil_Vb", 0).RotateTo(270)

            study.GetCircuit().CreateComponent("Coil", "coil_Wa")
            study.GetCircuit().CreateInstance("coil_Wa", x - 10, y + y_offset - 6)
            study.GetCircuit().GetComponent("coil_Wa").SetValue("Turn", turns)
            study.GetCircuit().GetComponent("coil_Wa").SetValue("Resistance", Rs)
            study.GetCircuit().GetInstance("coil_Wa", 0).RotateTo(270)

            study.GetCircuit().CreateComponent("Coil", "coil_Wb")
            study.GetCircuit().CreateInstance("coil_Wb", x - 6, y + y_offset - 6)
            study.GetCircuit().GetComponent("coil_Wb").SetValue("Turn", turns)
            study.GetCircuit().GetComponent("coil_Wb").SetValue("Resistance", Rs)
            study.GetCircuit().GetInstance("coil_Wb", 0).RotateTo(270)

            # Connecting same phase Coils
            study.GetCircuit().CreateWire(
                x - 4, y + y_offset + 6 + 2, x, y + y_offset + 6 + 2
            )
            study.GetCircuit().CreateWire(
                x + 10, y + y_offset - 6 - 2, x + 6, y + y_offset - 6 - 2
            )
            study.GetCircuit().CreateWire(
                x - 10, y + y_offset - 6 - 2, x - 6, y + y_offset - 6 - 2
            )

            # Connecting group B Coils to GND
            study.GetCircuit().CreateWire(x, y + y_offset + 6 - 2, x, y + y_offset)
            study.GetCircuit().CreateWire(x + 6, y + y_offset - 6 + 2, x, y + y_offset)
            study.GetCircuit().CreateWire(x - 6, y + y_offset - 6 + 2, x, y + y_offset)
            study.GetCircuit().CreateComponent("Ground", "Ground")
            study.GetCircuit().CreateInstance("Ground", x, y + y_offset - 2)

            # Placing current sources
            I1t = "CS_t-1"
            I2t = "CS_t-2"
            I3t = "CS_t-3"
            study.GetCircuit().CreateComponent("CurrentSource", I1t)
            study.GetCircuit().CreateInstance(I1t, x - 2, y + y_offset + 6 + 4)
            study.GetCircuit().GetInstance(I1t, 0).RotateTo(90)
            study.GetCircuit().CreateComponent("CurrentSource", I2t)
            study.GetCircuit().CreateInstance(I2t, x + 8, y + y_offset - 6 - 4)
            study.GetCircuit().GetInstance(I2t, 0).RotateTo(270)
            study.GetCircuit().CreateComponent("CurrentSource", I3t)
            study.GetCircuit().CreateInstance(I3t, x - 8, y + y_offset - 6 - 4)
            study.GetCircuit().GetInstance(I3t, 0).RotateTo(270)

            I1s = "CS_s-1"
            I2s = "CS_s-2"
            I3s = "CS_s-3"
            study.GetCircuit().CreateComponent("CurrentSource", I1s)
            study.GetCircuit().CreateInstance(I1s, x - 4 - 2, y + y_offset + 6 - 2)
            study.GetCircuit().GetInstance(I1s, 0).RotateTo(0)
            study.GetCircuit().CreateComponent("CurrentSource", I2s)
            study.GetCircuit().CreateInstance(I2s, x + 10 + 2, y + y_offset - 6 + 2)
            study.GetCircuit().GetInstance(I2s, 0).RotateTo(180)
            study.GetCircuit().CreateComponent("CurrentSource", I3s)
            study.GetCircuit().CreateInstance(I3s, x - 10 - 2, y + y_offset - 6 + 2)
            study.GetCircuit().GetInstance(I3s, 0).RotateTo(0)

            # Setting current values
            func = app.FunctionFactory().Composite()
            f1 = app.FunctionFactory().Sin(ampT, freq, 0)
            # "freq" variable cannot be used here. So pay extra attension when you create new case of a different freq.
            func.AddFunction(f1)
            study.GetCircuit().GetComponent(I1t).SetFunction(func)

            func = app.FunctionFactory().Composite()
            f1 = app.FunctionFactory().Sin(ampT, freq, -120)
            func.AddFunction(f1)
            study.GetCircuit().GetComponent(I2t).SetFunction(func)

            func = app.FunctionFactory().Composite()
            f1 = app.FunctionFactory().Sin(ampT, freq, -240)
            func.AddFunction(f1)
            study.GetCircuit().GetComponent(I3t).SetFunction(func)

            func = app.FunctionFactory().Composite()
            f1 = app.FunctionFactory().Sin(ampS, freq, 0)
            f2 = app.FunctionFactory().Sin(-ampT / 2, freq, 0)
            func.AddFunction(f1)
            func.AddFunction(f2)
            study.GetCircuit().GetComponent(I1s).SetFunction(func)

            func = app.FunctionFactory().Composite()
            f1 = app.FunctionFactory().Sin(ampS, freq, 120)
            f2 = app.FunctionFactory().Sin(-ampT / 2, freq, -120)
            func.AddFunction(f1)
            func.AddFunction(f2)
            study.GetCircuit().GetComponent(I2s).SetFunction(func)

            func = app.FunctionFactory().Composite()
            f1 = app.FunctionFactory().Sin(ampS, freq, 240)
            f2 = app.FunctionFactory().Sin(-ampT / 2, freq, -240)
            func.AddFunction(f1)
            func.AddFunction(f2)
            study.GetCircuit().GetComponent(I3s).SetFunction(func)

            # Terminal Voltage/Circuit Voltage: Check for outputting CSV results
            study.GetCircuit().CreateTerminalLabel("Terminal_Us", 6, 14)
            study.GetCircuit().CreateTerminalLabel("Terminal_Ws", 0, 6)
            study.GetCircuit().CreateTerminalLabel("Terminal_Vs", 20, 6)
            study.GetCircuit().CreateTerminalLabel("Terminal_Ut", 8, 18)
            study.GetCircuit().CreateTerminalLabel("Terminal_Wt", 2, 2)
            study.GetCircuit().CreateTerminalLabel("Terminal_Vt", 18, 2)

        current_tpeak = self.current_trms * np.sqrt(2)  # max current at torque term
        current_speak = self.current_srms * np.sqrt(2)  # max current at suspension term
        I_hat = self.machine_variant.Rated_current * np.sqrt(2)
        slot_area_utilizing_ratio = (current_tpeak / 2 + current_speak) / I_hat
        print("---Slot area utilizing ratio is", slot_area_utilizing_ratio)
        print("---Peak Current per coil :", I_hat)
        print("---Peak torque current :", current_tpeak)
        print("---Peak suspension current :", current_speak)
        print("---Torque_current_ratio:", self.operating_point.Iq)
        print("---Suspension_current_ratio:", self.operating_point.Iy)

        circuit(
            self.machine_variant.p,
            self.machine_variant.Z_q,
            Rs=self.R_wdg,
            ampT=current_tpeak,
            ampS=current_speak,
            freq=self.excitation_freq,
        )

        for suffix, poles in zip(
            ["a", "b"], [self.machine_variant.p * 2, self.machine_variant.ps * 2]
        ):
            for UVW in ["U", "V", "W"]:
                study.CreateCondition("FEMCoil", "phase_" + UVW + suffix)
                # link between FEM Coil Condition and Circuit FEM Coil
                condition = study.GetCondition("phase_" + UVW + suffix)
                condition.SetLink("coil_%s%s" % (UVW, suffix))
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

            condition = study.GetCondition(
                "phase_" + UVW + self.machine_variant.coil_groups[index]
            )

            # right layer
            # print (count, "Coil Set %d"%(count), end=' ')
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
            # print (count_leftlayer, "Coil Set %d"%(count_leftlayer))
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
            for suffix in ["a", "b"]:
                for UVW in ["U", "V", "W"]:
                    condition = study.GetCondition("phase_" + UVW + suffix)
                    condition.RemoveSubCondition("delete")

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
            print("- Bearingless PMSM Individual #%s\n\t" % name, end=" ")
            print(", \n\t".join("%s = %s" % item for item in tuple_list))
            return ""
        else:
            return "\n- Bearingless PMSM Individual #%s\n\t" % name + ", \n\t".join(
                "%s = %s" % item for item in tuple_list
            )

    def run_study(self, app, study, toc):
        if not self.config.jmag_scheduler:
            print("-----------------------Running JMAG (et 30 secs)...")
            # if run_list[1] == True:
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
            # study.CheckForCaseResults()
        app.Save()

    def mesh_study(self, app, model, study):

        # this `if' judgment is effective only if JMAG-DeleteResultFiles is False
        # if not study.AnyCaseHasResult():
        # mesh
        print("------------------Adding mesh")
        self.add_mesh(study, model)

        # Export Image
        app.View().ShowAllAirRegions()
        # app.View().ShowMeshGeometry() # 2nd btn
        app.View().ShowMesh()  # 3rn btn
        app.View().Zoom(3)
        app.View().Pan(-self.machine_variant.r_si, 0)
        app.ExportImageWithSize(
            self.design_results_folder + self.project_name + "mesh.png", 2000, 2000
        )
        app.View().ShowModel()  # 1st btn. close mesh view, and note that mesh data will be deleted if only ouput table
        # results are selected.

    def extract_JMAG_results(self, path, study_name):
        current_csv_path = path + study_name + "_circuit_current.csv"
        voltage_csv_path = path + study_name + "_EXPORT_CIRCUIT_VOLTAGE.csv"
        torque_csv_path = path + study_name + "_torque.csv"
        force_csv_path = path + study_name + "_force.csv"
        iron_loss_path = path + study_name + "_iron_loss_loss.csv"
        hysteresis_loss_path = path + study_name + "_hysteresis_loss_loss.csv"
        eddy_current_loss_path = path + study_name + "_joule_loss.csv"

        curr_df = pd.read_csv(current_csv_path, skiprows=6)
        volt_df = pd.read_csv(
            voltage_csv_path,
        )
        volt_df.rename(
            columns={
                "Time, s": "Time(s)",
                "Terminal_Us [Case 1]": "Terminal_Us",
                "Terminal_Ut [Case 1]": "Terminal_Ut",
                "Terminal_Vs [Case 1]": "Terminal_Vs",
                "Terminal_Vt [Case 1]": "Terminal_Vt",
                "Terminal_Ws [Case 1]": "Terminal_Ws",
                "Terminal_Wt [Case 1]": "Terminal_Wt",
            },
            inplace=True,
        )

        tor_df = pd.read_csv(torque_csv_path, skiprows=6)
        force_df = pd.read_csv(force_csv_path, skiprows=6)
        iron_df = pd.read_csv(iron_loss_path, skiprows=6)
        hyst_df = pd.read_csv(hysteresis_loss_path, skiprows=6)
        eddy_df = pd.read_csv(eddy_current_loss_path, skiprows=6)

        range_2TS = int(self.config.no_of_steps_per_rev_2TS * self.config.no_of_rev_2TS)

        curr_df = curr_df.set_index("Time(s)")
        tor_df = tor_df.set_index("Time(s)")
        volt_df = volt_df.set_index("Time(s)")
        force_df = force_df.set_index("Time(s)")
        eddy_df = eddy_df.set_index("Time(s)")
        hyst_df = hyst_df.set_index("Frequency(Hz)")
        iron_df = iron_df.set_index("Frequency(Hz)")

        fea_data = {
            "current": curr_df,
            "voltage": volt_df,
            "torque": tor_df,
            "force": force_df,
            "iron_loss": iron_df,
            "hysteresis_loss": hyst_df,
            "eddy_current_loss": eddy_df,
            "copper_loss": self.copper_loss,
            "range_fine_step": range_2TS,
        }

        return fea_data
