from time import time as clock_time
import os
import numpy as np
import pandas as pd
import sys

sys.path.append("../..")

from des_opt import InvalidDesign

from .eMach.python.emach.tools import jmag as jd
from .eMach.python.emach import model_obj as mo
from .eMach.python.emach.winding import Coil, CoilGroup, Winding

EPS = 1e-5  # unit: m


class BSPM_EM_Analysis:
    def __init__(self, configuration):
        self.configuration = configuration
        self.counter = 0
        self.machine_variant = None
        self.operating_point = None

    def analyze(self, problem, counter=0):
        self.counter = self.counter + 1
        self.machine_variant = problem.machine
        self.operating_point = problem.operating_point
        ####################################################
        # 01 Setting project name and output folder
        ####################################################
        self.project_name = 'proj_%d_' % self.counter

        expected_project_file = self.configuration['run_folder'] + "%s.jproj" % self.project_name

        # Create output folder
        if not os.path.isdir(self.configuration['JMAG_csv_folder']):
            os.makedirs(self.configuration['JMAG_csv_folder'])

        file = self.project_name + ".jproj"
        toolJd = jd.JmagDesigner2D()
        toolJd.open(comp_filepath=file, study_type='Transient2D')

        # print('Application is', app)
        # if attempts > 1:
        #     self.project_name = self.project_name + 'attempts_%d' % attempts

        self.study_name = self.project_name + "TranPMSM"
        self.design_results_folder = self.configuration['run_folder'] + "%sresults/" % self.project_name
        if not os.path.isdir(self.design_results_folder):
            os.makedirs(self.design_results_folder)
        ################################################################
        # 02 Run ElectroMagnetic analysis
        ################################################################
        self.create_custom_material(toolJd.jd, self.machine_variant.stator_iron_mat['core_material'])
        # Draw machine components
        machine_handle = self.draw_machine(toolJd)

        # Import Model into Designer
        toolJd.doc.SaveModel(True)  # True: Project is also saved.
        model = toolJd.jd.GetCurrentModel()
        model.SetName(self.project_name)
        # model.SetDescription(self.show(self.project_name, toString=True))
        # Add study and run
        valid_design = self.pre_process(toolJd.jd, model)
        if not valid_design:
            raise InvalidDesign

        # create study
        study = self.add_magnetic_transient_study(toolJd.jd, model, machine_handle['winding'],
                                                  self.configuration['JMAG_csv_folder'], self.study_name)

        self.mesh_study(toolJd.jd, model, study)
        self.run_study(toolJd.jd, study, clock_time())
        # export Voltage if field data exists.
        if not self.configuration['delete_results_after_calculation']:
            # Export Circuit Voltage
            ref1 = toolJd.jd.GetDataManager().GetDataSet("Circuit Voltage")
            toolJd.jd.GetDataManager().CreateGraphModel(ref1)
            toolJd.jd.GetDataManager().GetGraphModel("Circuit Voltage").WriteTable(
                self.configuration['JMAG_csv_folder'] + self.study_name + "_EXPORT_CIRCUIT_VOLTAGE.csv")
        toolJd.close()
        ####################################################
        # 03 Load FEA output
        ####################################################

        fea_rated_output = self.extract_JMAG_results(self.configuration['JMAG_csv_folder'], self.study_name)
        # dh.read_csv_results(self.study_name, self.configuration['JMAG_csv_folder'], self.configuration)

        ####################################################
        # 04 Update stack length for rated torque, update design param and performance accordingly
        ####################################################

        return fea_rated_output

    def initial_excitation_bias_compensation_deg(self):
        return 0

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
                self.machine_variant.r_si + self.machine_variant.d_sp + self.machine_variant.d_st / 2)
        l_ew = np.pi * 0.5 * (tau_u + self.machine_variant.w_st) / 2 + tau_u * self.machine_variant.Kov * (
                self.machine_variant.pitch - 1)
        l_coil = 2 * (self.machine_variant.l_st + l_ew)  # length of one coil
        return l_coil

    @property
    def R_coil(self):
        a_wire = (self.machine_variant.s_slot * self.machine_variant.Kcu) / (2 * self.machine_variant.Z_q)
        return (self.l_coil * self.machine_variant.Z_q * self.machine_variant.Q / 6) / (
                self.machine_variant.coil_mat['copper_elec_conductivity'] * a_wire)

    @property
    def copper_loss(self):
        return self.machine_variant.Q * ((self.current_trms / 2) ** 2 + self.current_srms ** 2) * self.R_coil

    def draw_machine(self, toolJd):
        ####################################################
        # Draw cross-sections
        ####################################################
        pole_pairs = self.machine_variant.p
        rotor_core = mo.CrossSectInnerNotchedRotor(name='NotchedRotor',
                                                   location=mo.Location2D(),
                                                   dim_alpha_rm=mo.DimDegree(self.machine_variant.alpha_m),
                                                   dim_alpha_rs=mo.DimDegree(self.machine_variant.alpha_ms / 2),
                                                   dim_d_ri=mo.DimMeter(self.machine_variant.d_ri),
                                                   dim_r_ri=mo.DimMeter(self.machine_variant.r_sh),
                                                   dim_d_rp=mo.DimMeter(self.machine_variant.d_mp),
                                                   dim_d_rs=mo.DimMeter(self.machine_variant.d_ri),
                                                   p=pole_pairs, s=self.machine_variant.n_m * 2)

        shaft = mo.CrossSectHollowCylinder(name='Shaft', location=mo.Location2D(),
                                           dim_t=mo.DimMeter(self.machine_variant.r_sh),
                                           dim_r_o=mo.DimMeter(self.machine_variant.r_sh))

        # all magnet cross-sections
        rotor_magnet = []
        for i in range(pole_pairs * 2):
            magnet = mo.CrossSectArc(name='RotorMagnet' + str(i),
                                     location=mo.Location2D(theta=mo.DimDegree(360 / (pole_pairs * 2) * i)),
                                     dim_d_a=mo.DimMeter(self.machine_variant.d_m),
                                     dim_r_o=mo.DimMeter(self.machine_variant.r_ro),
                                     dim_alpha=mo.DimDegree(360 / (pole_pairs * 2)))
            rotor_magnet.append(magnet)

        # stator cross-section
        stator_core = mo.CrossSectInnerRotorStator(name='StatorCore',
                                                   dim_alpha_st=mo.DimDegree(self.machine_variant.alpha_st),
                                                   dim_alpha_so=mo.DimDegree(self.machine_variant.alpha_so),
                                                   dim_r_si=mo.DimMeter(self.machine_variant.r_si),
                                                   dim_d_sy=mo.DimMeter(self.machine_variant.d_sy),
                                                   dim_d_st=mo.DimMeter(self.machine_variant.d_st),
                                                   dim_d_sp=mo.DimMeter(self.machine_variant.d_sp),
                                                   dim_d_so=mo.DimMeter(self.machine_variant.d_so),
                                                   dim_w_st=mo.DimMeter(self.machine_variant.w_st),
                                                   dim_r_st=mo.DimMeter(0),
                                                   dim_r_sf=mo.DimMeter(0),
                                                   dim_r_sb=mo.DimMeter(0),
                                                   Q=self.machine_variant.Q,
                                                   location=mo.Location2D(
                                                       anchor_xy=[mo.DimMillimeter(0), mo.DimMillimeter(0)]),
                                                   theta=mo.DimDegree(0))

        ####################################################
        # Create components
        ####################################################

        rotor_comp = mo.Component(
            name='NotchedRotor',
            cross_sections=[rotor_core],
            material=mo.MaterialGeneric(name=self.machine_variant.stator_iron_mat['core_material'], color=r'#808080'),
            make_solid=mo.MakeExtrude(location=mo.Location3D(),
                                      dim_depth=mo.DimMeter(self.machine_variant.l_st)))

        stator_comp = mo.Component(
            name='StatorCore',
            cross_sections=[stator_core],
            material=mo.MaterialGeneric(name=self.machine_variant.stator_iron_mat['core_material'], color=r'#808080'),
            make_solid=mo.MakeExtrude(location=mo.Location3D(),
                                      dim_depth=mo.DimMeter(self.machine_variant.l_st)))

        shaft_comp = mo.Component(
            name='Shaft',
            cross_sections=[shaft],
            material=mo.MaterialGeneric(name=self.machine_variant.stator_iron_mat['core_material'], color=r'#808080'),
            make_solid=mo.MakeExtrude(location=mo.Location3D(),
                                      dim_depth=mo.DimMeter(self.machine_variant.l_st)))

        magnet_comps = []
        for i in range(pole_pairs * 2):
            magnet_comp = mo.Component(
                name='Magnet' + str(i),
                cross_sections=[rotor_magnet[i]],
                material=mo.MaterialGeneric(name="Arnold/Reversible/N40H", color=r'#4d4b4f'),
                make_solid=mo.MakeExtrude(location=mo.Location3D(),
                                          dim_depth=mo.DimMeter(self.machine_variant.l_st)))
            magnet_comps.append(magnet_comp)

        coil1 = mo.CrossSectInnerRotorStatorCoil(name='coil1',
                                                 dim_r_si=mo.DimMeter(self.machine_variant.r_si),
                                                 dim_d_st=mo.DimMeter(self.machine_variant.d_st),
                                                 dim_d_sp=mo.DimMeter(self.machine_variant.d_sp),
                                                 dim_w_st=mo.DimMeter(self.machine_variant.w_st),
                                                 dim_r_st=mo.DimMeter(0),
                                                 dim_r_sf=mo.DimMeter(0),
                                                 dim_r_sb=mo.DimMeter(0),
                                                 Q=self.machine_variant.Q,
                                                 slot=1,
                                                 layer=0,
                                                 num_of_layers=2,
                                                 location=mo.Location2D(
                                                     anchor_xy=[mo.DimMeter(0), mo.DimMeter(0)]),
                                                 theta=mo.DimDegree(0))
        coil1_comp = mo.Component(name='Coil', cross_sections=[coil1],
                                  material=mo.MaterialGeneric(name="Copper", color=r'#b87333'),
                                  make_solid=mo.MakeExtrude(location=mo.Location3D(),
                                                            dim_depth=mo.DimMeter(self.machine_variant.l_st)))

        coil_1 = Coil(name='Coil1', slot1=6, slot2=4, slot1_layer=0, slot2_layer=1,
                      material=mo.MaterialGeneric(name="Copper", color=r'#b87333'), zQ=self.machine_variant.Z_q)
        coil_2 = Coil(name='Coil2', slot1=1, slot2=3, slot1_layer=0, slot2_layer=1,
                      material=mo.MaterialGeneric(name="Copper", color=r'#b87333'), zQ=self.machine_variant.Z_q)
        coil_3 = Coil(name='Coil3', slot1=2, slot2=6, slot1_layer=0, slot2_layer=1,
                      material=mo.MaterialGeneric(name="Copper", color=r'#b87333'), zQ=self.machine_variant.Z_q)
        coil_4 = Coil(name='Coil4', slot1=3, slot2=5, slot1_layer=0, slot2_layer=1,
                      material=mo.MaterialGeneric(name="Copper", color=r'#b87333'), zQ=self.machine_variant.Z_q)
        coil_5 = Coil(name='Coil5', slot1=4, slot2=2, slot1_layer=0, slot2_layer=1,
                      material=mo.MaterialGeneric(name="Copper", color=r'#b87333'), zQ=self.machine_variant.Z_q)
        coil_6 = Coil(name='Coil6', slot1=5, slot2=1, slot1_layer=0, slot2_layer=1,
                      material=mo.MaterialGeneric(name="Copper", color=r'#b87333'), zQ=self.machine_variant.Z_q)

        # create coil groups from a set of coils
        coil_group1 = CoilGroup(name='coil_Ua', coils=[coil_1])
        coil_group2 = CoilGroup(name='coil_Ub', coils=[coil_2])
        coil_group3 = CoilGroup(name='coil_Va', coils=[coil_3])
        coil_group4 = CoilGroup(name='coil_Vb', coils=[coil_4])
        coil_group5 = CoilGroup(name='coil_Wa', coils=[coil_5])
        coil_group6 = CoilGroup(name='coil_Wb', coils=[coil_6])

        # create winding from a set of coil groups
        winding = Winding(coil_groups=[coil_group1, coil_group2, coil_group3, coil_group4, coil_group5, coil_group6],
                          winding_nodes=['Ut'], slots=6, num_of_layers=2)

        try:

            # make stator and rotor in JMAG
            rotor_handle = rotor_comp.make(toolJd, toolJd)
            shaft_handle = shaft_comp.make(toolJd, toolJd)
            # make magnet components in JMAG
            magnet_handles = []
            for i in range(pole_pairs * 2):
                magnet_handle = magnet_comps[i].make(toolJd, toolJd)
                magnet_handles.append(magnet_handle)
            stator_handle = stator_comp.make(toolJd, toolJd)
            # draw winding and create coil condition in JMAG
            winding_handles = winding.wind(coil_cross=coil1, coil_comp=coil1_comp, tool=toolJd)
        except:
            raise InvalidDesign

        comp_handles = {'rotor': rotor_handle,
                        'stator': stator_handle,
                        'shaft': shaft_handle,
                        'magnets': magnet_handles,
                        'winding': winding_handles}
        return comp_handles

    def pre_process(self, app, model):
        # pre-process : you can select part by coordinate!
        """ Group """

        def group(name, id_list):
            model.GetGroupList().CreateGroup(name)
            for the_id in id_list:
                model.GetGroupList().AddPartToGroup(name, the_id)
                # model.GetGroupList().AddPartToGroup(name, name) #<- this also works

        part_ID_list = model.GetPartIDs()
        # check if everything except for the winding is drawn
        if len(part_ID_list) != int(1 + 1 + self.machine_variant.p * 2 + 1 + self.machine_variant.Q*2):
            print('Parts are missing in this machine')
            return False

        self.id_backiron = id_backiron = part_ID_list[0]
        id_shaft = part_ID_list[1]
        partIDRange_Magnet = part_ID_list[2:int(2 + self.machine_variant.p * 2)]

        group("Magnet", partIDRange_Magnet)

        # Add Part to Set for later references
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
        add_part_to_set('ShaftSet', 0.0, 0.0, ID=id_shaft)

        # Create Set for Magnets
        R = (self.machine_variant.r_si - self.machine_variant.delta_e - 0.5 * self.machine_variant.d_m)
        Angle_RotorSlotSpan = 360 / (self.machine_variant.p * 2)
        THETA = 0  # initial position
        X = R * np.cos(THETA)
        Y = R * np.sin(THETA)
        list_xy_magnets = []
        for ind in range(int(self.machine_variant.p * 2)):
            natural_ind = ind + 1
            add_part_to_set("Magnet %d" % natural_ind, X, Y)
            list_xy_magnets.append([X, Y])

            THETA += Angle_RotorSlotSpan / 180. * np.pi
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

        part_list_set('Motion_Region', list_xy_magnets, list_part_id=[id_backiron, id_shaft])
        part_list_set('MagnetSet', list_xy_magnets)
        return True

    def add_magnetic_transient_study(self, app, model, winding, dir_csv_output_folder, study_name):
        app.SetCurrentStudy(1)
        app.GetModel(1).GetStudy(0).SetName(study_name)
        app.SetCurrentStudy(study_name)
        study = model.GetStudy(study_name)

        study.GetStudyProperties().SetValue("ConversionType", 0)
        study.GetStudyProperties().SetValue("NonlinearMaxIteration", self.configuration['max_nonlinear_iterations'])

        # Material
        self.add_material(study)

        # Conditions - Motion
        speed = self.excitation_freq * 2*np.pi / self.machine_variant.p  # rpm
        study.CreateCondition("RotationMotion", "RotCon")
        # study.GetCondition(u"RotCon").SetXYZPoint(u"", 0, 0, 1) # megbox warning
        print('the_speed:', speed)
        study.GetCondition("RotCon").SetValue("AngularVelocity", int(speed))
        study.GetCondition("RotCon").ClearParts()
        study.GetCondition("RotCon").AddSet(model.GetSetList().GetSet("Motion_Region"), 0)
        # Implementation of id=0 control:
        #   d-axis initial position is self.alpha_m*0.5
        #   The U-phase current is sin(omega_syn*t) = 0 at t=0.
        study.GetCondition("RotCon").SetValue(u"InitialRotationAngle", -self.machine_variant.alpha_m * 0.5 + 180 +
                                              self.initial_excitation_bias_compensation_deg() +
                                              (180 / self.machine_variant.p))
        # add 360/(2p) deg to reverse the initial magnetizing direction to make torque positive.

        study.CreateCondition("Torque",
                              "TorCon")  # study.GetCondition(u"TorCon").SetXYZPoint(u"", 0, 0, 0) # megbox warning
        study.GetCondition("TorCon").SetValue("TargetType", 1)
        study.GetCondition("TorCon").SetLinkWithType("LinkedMotion", "RotCon")
        study.GetCondition("TorCon").ClearParts()

        study.CreateCondition("Force", "ForCon")
        study.GetCondition("ForCon").SetValue("TargetType", 1)
        study.GetCondition("ForCon").SetLinkWithType("LinkedMotion", "RotCon")
        study.GetCondition("ForCon").ClearParts()

        # Conditions - FEM Coils & Conductors (i.e. stator/rotor winding)
        self.add_circuit(app, study, winding, bool_3PhaseCurrentSource=False)

        # True: no mesh or field results are needed
        study.GetStudyProperties().SetValue("OnlyTableResults", self.configuration['OnlyTableResults'])

        # this can be said to be super fast over ICCG solver.
        # https://www2.jmag-international.com/support/en/pdf/JMAG-Designer_Ver.17.1_ENv3.pdf
        study.GetStudyProperties().SetValue("DirectSolverType", 1)

        if self.configuration['MultipleCPUs']:
            # This SMP(shared memory process) is effective only if there are tons of elements. e.g., over 100,000.
            # too many threads will in turn make them compete with each other and slow down the solve. 2 is good enough
            # for eddy current solve. 6~8 is enough for transient solve.
            study.GetStudyProperties().SetValue("UseMultiCPU", True)
            study.GetStudyProperties().SetValue("MultiCPU", 2)

            # two sections of different time step
        if True:
            number_of_revolution_1TS = self.configuration['number_of_revolution_1TS']
            number_of_revolution_2TS = self.configuration['number_of_revolution_2TS']
            number_of_steps_1TS = self.configuration['number_of_steps_per_rev_1TS'] * number_of_revolution_1TS
            number_of_steps_2TS = self.configuration['number_of_steps_per_rev_2TS'] * number_of_revolution_2TS
            DM = app.GetDataManager()
            DM.CreatePointArray("point_array/timevsdivision", "SectionStepTable")
            refarray = [[0 for i in range(3)] for j in range(3)]
            refarray[0][0] = 0
            refarray[0][1] = 1
            refarray[0][2] = 50
            refarray[1][0] = number_of_revolution_1TS / self.excitation_freq
            refarray[1][1] = number_of_steps_1TS
            refarray[1][2] = 50
            refarray[2][0] = (number_of_revolution_1TS + number_of_revolution_2TS) / self.excitation_freq
            refarray[2][1] = number_of_steps_2TS
            refarray[2][2] = 50
            DM.GetDataSet("SectionStepTable").SetTable(refarray)
            number_of_total_steps = 1 + number_of_steps_1TS + number_of_steps_2TS  # don't forget to modify here!
            study.GetStep().SetValue("Step", number_of_total_steps)
            study.GetStep().SetValue("StepType", 3)
            study.GetStep().SetTableProperty("Division", DM.GetDataSet("SectionStepTable"))

        # add equations
        study.GetDesignTable().AddEquation("freq")
        study.GetDesignTable().AddEquation("speed")
        study.GetDesignTable().GetEquation("freq").SetType(0)
        study.GetDesignTable().GetEquation("freq").SetExpression("%g" % self.excitation_freq)
        study.GetDesignTable().GetEquation("freq").SetDescription("Excitation Frequency")
        study.GetDesignTable().GetEquation("speed").SetType(1)
        study.GetDesignTable().GetEquation("speed").SetExpression("freq * %d" % (1 / self.machine_variant.p))
        study.GetDesignTable().GetEquation("speed").SetDescription("mechanical speed of four pole")

        # speed, freq, slip
        study.GetCondition("RotCon").SetValue("AngularVelocity", 'speed')

        # Iron Loss Calculation Condition
        # Stator
        if True:
            cond = study.CreateCondition("Ironloss", "IronLossConStator")
            cond.SetValue("RevolutionSpeed", "freq*60/%d" % self.machine_variant.p)
            cond.ClearParts()
            sel = cond.GetSelection()
            sel.SelectPartByPosition(self.machine_variant.r_si + EPS, EPS, 0)
            cond.AddSelected(sel)
            # Use FFT for hysteresis to be consistent with FEMM's results and to have a FFT plot
            cond.SetValue("HysteresisLossCalcType", 1)
            cond.SetValue("PresetType", 3)  # 3:Custom
            # Specify the reference steps yourself because you don't really know what JMAG is doing behind you
            cond.SetValue("StartReferenceStep",
                          number_of_total_steps + 1 - number_of_steps_2TS * 0.5)  # 1/4 period = number_of_steps_2TS*0.5
            cond.SetValue("EndReferenceStep", number_of_total_steps)
            cond.SetValue("UseStartReferenceStep", 1)
            cond.SetValue("UseEndReferenceStep", 1)
            cond.SetValue("Cyclicity", 4)  # specify reference steps for 1/4 period and extend it to whole period
            cond.SetValue("UseFrequencyOrder", 1)
            cond.SetValue("FrequencyOrder", "1-50")  # Harmonics up to 50th orders
        # Check CSV results for iron loss (You cannot check this for Freq study) # CSV and save space
        study.GetStudyProperties().SetValue("CsvOutputPath", dir_csv_output_folder)  # it's folder rather than file!
        study.GetStudyProperties().SetValue("CsvResultTypes", self.configuration['Csv_Results'])
        study.GetStudyProperties().SetValue("DeleteResultFiles", self.configuration['delete_results_after_calculation'])

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
            cond.SetValue("StartReferenceStep",
                          number_of_total_steps + 1 - number_of_steps_2TS * 0.5)  # 1/4 period = number_of_steps_2TS*0.5
            cond.SetValue("EndReferenceStep", number_of_total_steps)
            cond.SetValue("UseStartReferenceStep", 1)
            cond.SetValue("UseEndReferenceStep", 1)
            cond.SetValue("Cyclicity", 4)  # specify reference steps for 1/4 period and extend it to whole period
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

        study.GetMeshControl().SetValue("MeshType",
                                        1)  # make sure this has been exe'd:
        # study.GetCondition(u"RotCon").AddSet(model.GetSetList().GetSet(u"Motion_Region"), 0)
        study.GetMeshControl().SetValue("RadialDivision", self.configuration[
            'mesh_radial_division'])  # for air region near which motion occurs
        study.GetMeshControl().SetValue("CircumferentialDivision", self.configuration[
            'mesh_circum_division'])  # 1440) # for air region near which motion occurs 这个数足够大，sliding mesh才准确。
        study.GetMeshControl().SetValue("AirRegionScale", self.configuration[
            'mesh_air_region_scale'])  # [Model Length]: Specify a value within (1.05 <= value < 1000)
        study.GetMeshControl().SetValue("MeshSize", self.configuration['mesh_size'])  # m
        study.GetMeshControl().SetValue("AutoAirMeshSize", 0)
        study.GetMeshControl().SetValue("AirMeshSize", self.configuration['mesh_size'])  # m
        study.GetMeshControl().SetValue("Adaptive", 0)

        # This is not neccessary for whole model FEA. In fact, for BPMSM simulation, it causes mesh error "The copy
        # target region is not found".
        # study.GetMeshControl().CreateCondition("RotationPeriodicMeshAutomatic", "autoRotMesh") with this you can
        # choose to set CircumferentialDivision automatically

        study.GetMeshControl().CreateCondition("Part", "MagnetMeshCtrl")
        study.GetMeshControl().GetCondition("MagnetMeshCtrl").SetValue("Size", self.configuration[
            'mesh_magnet_size'])  # m
        study.GetMeshControl().GetCondition("MagnetMeshCtrl").ClearParts()
        study.GetMeshControl().GetCondition("MagnetMeshCtrl").AddSet(model.GetSetList().GetSet("MagnetSet"), 0)

        def mesh_all_cases(study):
            numCase = study.GetDesignTable().NumCases()
            for case in range(0, numCase):
                study.SetCurrentCase(case)
                if not study.HasMesh():
                    study.CreateMesh()

        mesh_all_cases(study)

    def create_custom_material(self, app, steel_name):

        core_mat_obj = app.GetMaterialLibrary().GetCustomMaterial(self.machine_variant.stator_iron_mat['core_material'])
        app.GetMaterialLibrary().DeleteCustomMaterialByObject(core_mat_obj)

        app.GetMaterialLibrary().CreateCustomMaterial(self.machine_variant.stator_iron_mat['core_material'],
                                                      "Custom Materials")
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "Density", self.machine_variant.stator_iron_mat['core_material_density'])
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "MagneticSteelPermeabilityType", 2)
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "CoerciveForce", 0)
        # app.GetMaterialLibrary().GetUserMaterial(u"Arnon5-final").GetTable("BhTable").SetName(u"SmoothZeroPointOne")
        BH = np.loadtxt(self.machine_variant.stator_iron_mat['core_bh_file'], unpack=True,
                        usecols=(0, 1))  # values from Nishanth Magnet BH curve
        refarray = BH.T.tolist()
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).GetTable(
            "BhTable").SetTable(refarray)
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "DemagnetizationCoerciveForce", 0)
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "MagnetizationSaturated", 0)
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "MagnetizationSaturated2", 0)
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "ExtrapolationMethod", 1)
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "YoungModulus", self.machine_variant.stator_iron_mat['core_youngs_modulus'])
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "ShearModulus", 0)
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "YoungModulusX", 0)
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "YoungModulusY", 0)
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "YoungModulusZ", 0)
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "ShearModulusXY", 0)
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "ShearModulusYZ", 0)
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "ShearModulusZX", 0)
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "Loss_Type", 1)
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "LossConstantKhX", self.machine_variant.stator_iron_mat['core_ironloss_Kh'])
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "LossConstantKeX", self.machine_variant.stator_iron_mat['core_ironloss_Ke'])
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "LossConstantAlphaX", self.machine_variant.stator_iron_mat['core_ironloss_a'])
        app.GetMaterialLibrary().GetUserMaterial(self.machine_variant.stator_iron_mat['core_material']).SetValue(
            "LossConstantBetaX", self.machine_variant.stator_iron_mat['core_ironloss_b'])

    def add_material(self, study):
        study.GetMaterial("StatorCore").SetValue("Laminated", 1)
        study.GetMaterial("StatorCore").SetValue("LaminationFactor",
                                                 self.machine_variant.stator_iron_mat['core_stacking_factor'])

        study.GetMaterial("NotchedRotor").SetValue("Laminated", 1)
        study.GetMaterial("NotchedRotor").SetValue("LaminationFactor",
                                                   self.machine_variant.stator_iron_mat['core_stacking_factor'])

        # study.SetMaterialByName("Coils", "Copper")
        # study.GetMaterial("Coils").SetValue("UserConductivityType", 1)

        study.SetMaterialByName(u"Magnet", u"{}".format(self.machine_variant.magnet_mat['magnet_material']))
        study.GetMaterial(u"Magnet").SetValue(u"EddyCurrentCalculation", 1)
        study.GetMaterial(u"Magnet").SetValue(u"Temperature", self.machine_variant.magnet_mat[
            'magnet_max_temperature'])  # TEMPERATURE (There is no 75 deg C option)

        study.GetMaterial(u"Magnet").SetValue(u"Poles", 2 * self.machine_variant.p)

        study.GetMaterial(u"Magnet").SetDirectionXYZ(1, 0, 0)
        study.GetMaterial(u"Magnet").SetAxisXYZ(0, 0, 1)
        study.GetMaterial(u"Magnet").SetOriginXYZ(0, 0, 0)
        study.GetMaterial(u"Magnet").SetPattern(u"ParallelCircular")
        study.GetMaterial(u"Magnet").SetValue(u"StartAngle", 0)

    def add_circuit(self, app, study, winding, bool_3PhaseCurrentSource=True):
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
            study.GetCircuit().CreateWire(x - 4, y + y_offset + 6 + 2, x, y + y_offset + 6 + 2)
            study.GetCircuit().CreateWire(x + 10, y + y_offset - 6 - 2, x + 6, y + y_offset - 6 - 2)
            study.GetCircuit().CreateWire(x - 10, y + y_offset - 6 - 2, x - 6, y + y_offset - 6 - 2)

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
            study.GetCircuit().CreateTerminalLabel("Terminal_Us", 6, -14)
            study.GetCircuit().CreateTerminalLabel("Terminal_Ws", 0, -6)
            study.GetCircuit().CreateTerminalLabel("Terminal_Vs", 20, -6)
            study.GetCircuit().CreateTerminalLabel("Terminal_Ut", 8, -18)
            study.GetCircuit().CreateTerminalLabel("Terminal_Wt", 2, -2)
            study.GetCircuit().CreateTerminalLabel("Terminal_Vt", 18, -2)

        current_tpeak = self.current_trms * np.sqrt(2)  # It, max current at torque terminal
        current_speak = self.current_srms * np.sqrt(2)  # Is, max current at suspension terminal Is+It/2

        slot_area_utilizing_ratio = (current_tpeak / 2 + current_speak) / (
                self.machine_variant.Rated_current * np.sqrt(2))
        print('---Slot area utilizing ratio is', slot_area_utilizing_ratio)
        print('---Peak Current per coil :', self.machine_variant.Rated_current * np.sqrt(2))
        print('---Peak torque current :', current_tpeak)
        print('---Peak suspension current :', current_speak)
        print('---Torque_current_ratio:', self.operating_point.Iq)
        print('---Suspension_current_ratio:', self.operating_point.Iy)

        circuit(self.machine_variant.p, self.machine_variant.Z_q, Rs=self.R_coil, ampT=current_tpeak,
                ampS=current_speak, freq=self.excitation_freq)

        ## link winding coils to circuit coils
        for i in range(len(winding)):
            coil_name = winding[i].GetName()
            print("Coil is", coil_name)
            study.GetCondition(i).SetLink(coil_name)

    def show(self, name, toString=False):
        attrs = list(vars(self).items())
        key_list = [el[0] for el in attrs]
        val_list = [el[1] for el in attrs]
        the_dict = dict(list(zip(key_list, val_list)))
        sorted_key = sorted(key_list, key=lambda item: (
            int(item.partition(' ')[0]) if item[0].isdigit() else float('inf'),
            item))  # this is also useful for string beginning with digiterations '15 Steel'.
        tuple_list = [(key, the_dict[key]) for key in sorted_key]
        if not toString:
            print('- Bearingless PMSM Individual #%s\n\t' % name, end=' ')
            print(', \n\t'.join("%s = %s" % item for item in tuple_list))
            return ''
        else:
            return '\n- Bearingless PMSM Individual #%s\n\t' % name + ', \n\t'.join(
                "%s = %s" % item for item in tuple_list)

    def run_study(self, app, study, toc):
        if not self.configuration['JMAG_Scheduler']:
            print('-----------------------Running JMAG (et 30 secs)...')
            # if run_list[1] == True:
            study.RunAllCases()
            msg = 'Time spent on %s is %g s.' % (study.GetName(), clock_time() - toc)
            print(msg)
        else:
            print('Submit to JMAG_Scheduler...')
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
        print('------------------Adding mesh')
        self.add_mesh(study, model)

        # Export Image
        app.View().ShowAllAirRegions()
        # app.View().ShowMeshGeometry() # 2nd btn
        app.View().ShowMesh()  # 3rn btn
        app.View().Zoom(3)
        app.View().Pan(-self.machine_variant.r_si, 0)
        app.ExportImageWithSize(self.design_results_folder + self.project_name + 'mesh.png', 2000, 2000)
        app.View().ShowModel()  # 1st btn. close mesh view, and note that mesh data will be deleted if only ouput table
        # results are selected.

    def extract_JMAG_results(self, path, study_name):
        current_csv_path = path + study_name + '_circuit_current.csv'
        voltage_csv_path = path + study_name + '_EXPORT_CIRCUIT_VOLTAGE.csv'
        torque_csv_path = path + study_name + '_torque.csv'
        force_csv_path = path + study_name + '_force.csv'
        iron_loss_path = path + study_name + '_iron_loss_loss.csv'
        hysteresis_loss_path = path + study_name + '_hysteresis_loss_loss.csv'
        eddy_current_loss_path = path + study_name + '_joule_loss.csv'

        curr_df = pd.read_csv(current_csv_path, skiprows=6)
        volt_df = pd.read_csv(voltage_csv_path, )
        volt_df.rename(columns={'Time, s': 'Time(s)', 'Terminal_Us [Case 1]': 'Terminal_Us',
                                'Terminal_Ut [Case 1]': 'Terminal_Ut',
                                'Terminal_Vs [Case 1]': 'Terminal_Vs',
                                'Terminal_Vt [Case 1]': 'Terminal_Vt',
                                'Terminal_Ws [Case 1]': 'Terminal_Ws',
                                'Terminal_Wt [Case 1]': 'Terminal_Wt', }, inplace=True)

        tor_df = pd.read_csv(torque_csv_path, skiprows=6)
        force_df = pd.read_csv(force_csv_path, skiprows=6)
        iron_df = pd.read_csv(iron_loss_path, skiprows=6)
        hyst_df = pd.read_csv(hysteresis_loss_path, skiprows=6)
        eddy_df = pd.read_csv(eddy_current_loss_path, skiprows=6)

        range_2TS = int(
            self.configuration['number_of_steps_per_rev_2TS'] * self.configuration['number_of_revolution_2TS'])

        curr_df = curr_df.set_index('Time(s)')
        tor_df = tor_df.set_index('Time(s)')
        volt_df = volt_df.set_index('Time(s)')
        force_df = force_df.set_index('Time(s)')
        eddy_df = eddy_df.set_index('Time(s)')
        hyst_df = hyst_df.set_index('Frequency(Hz)')
        iron_df = iron_df.set_index('Frequency(Hz)')

        fea_data = {
            'current': curr_df,
            'voltage': volt_df,
            'torque': tor_df,
            'force': force_df,
            'iron_loss': iron_df,
            'hysteresis_loss': hyst_df,
            'eddy_current_loss': eddy_df,
            'copper_loss': self.copper_loss,
            'range_fine_step': range_2TS
        }

        return fea_data
