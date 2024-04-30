SynR JMAG 2D FEA Analyzer
########################################################################

This analyzer enables the 2D transient FEA evaluation of synchronous reluctance (SynR) machines in JMAG.

Model Background
****************

Synchronous reluctance (SynR) machines are electric machines capable of producing electromagnetic torque without the need for a 
rotor-mounted field source. Basic characteristics of the design and analysis of synchronous reluctance machines can be done 
by hand, as is shown in the paper `here <https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=5167704>`_. Common ways of
characterizing SynR machines include finding the following qualities of their design:

1) Torque density
2) Power density
3) Efficiency
4) Torque ripple

* R. R. Moghaddam, F. Magnussen and C. Sadarangani, "A FEM1 investigation on the Synchronous Reluctance Machine rotor geometry with 
  just one flux barrier as a guide toward the optimal barrier's shape," `IEEE EUROCON 2009`, St. Petersburg, Russia, 2009, 
  pp. 663-670, doi: 10.1109/EURCON.2009.5167704.

This analyzer calculates the aforementioned parameters using JMAG's transient solver. It has been set up such that the evaluation process 
is split into two distinct time-step sections. In the first section, the rotor current will reach steady state within a reasonable number 
of steps. Once the machine is at steady state, operation is evaluated by having small steps with respect to stator frequency. The following 
document will provide a description of the analyzer inputs and outputs:

Input from User
*********************************

To use this analyzer, users must pass in a ``MachineDesign`` object. An instance of the ``MachineDesign`` class can be created by passing in 
``machine`` and ``operating_point`` objects. The machine must be a ``SynR_Machine`` and the ``operating_point`` must be of type 
``SynR_Machine_Oper_Pt``. More information on both these classes is available in the ``SynR Design`` section under ``MACHINE DESIGNS``. To 
initialize the ``SynR_JMAG_2D_FEA_Analyzer``, users must also specify analyzer configuration parameters. One can control the version of JMAG
desired for use in this analyzer using ``jmag_version``. For example, the use of JMAG-Designer21.1 would require an input of ``21.1``.

The tables below provide the input expected by the ``MachineDesign`` class and the configuration input required to initialize the 
``SynR_JMAG_2D_FEA_Analyzer``.

.. csv-table:: `MachineDesign Input`
   :file: input_SynR_jmag2d_analyzer.csv
   :widths: 70, 70
   :header-rows: 1

.. csv-table:: `SynR_JMAG_2D_FEA_Analyzer Initialization`
   :file: init_SynR_jmag2d_analyzer.csv
   :widths: 70, 70
   :header-rows: 1

Example code initializing the machine design for the optimized SynR design provided in the example found in the ``SynR Design`` section of 
``MACHINE DESIGNS`` is shown below. An identical file titled ``example_SynR_machine`` is stored in the ``SynR_eval`` folder within the 
``mach_eval_examples`` folder in the ``examples`` folder of ``eMach``.

.. code-block:: python

    import os
    import sys

    from mach_eval.machines.materials.electric_steels import (Arnon5)
    from mach_eval.machines.materials.miscellaneous_materials import (
        Steel,
        Copper,
        Air,
    )
    from mach_eval.machines.SynR.SynR_machine import SynR_Machine
    from mach_eval.machines.SynR.SynR_machine_oper_pt import SynR_Machine_Oper_Pt

    SynR_dimensions = {
        'alpha_b': 135,
        'r_sh': 6,
        'r_ri': 6,
        'r_ro': 49,
        'r_f1': 0.1,
        'r_f2': 0.1,
        'r_f3': 0.1,
        'd_r1': 4,
        'd_r2': 8,
        'd_r3': 8,
        'w_b1': 4,
        'w_b2': 4,
        'w_b3': 4,
        'l_b1': 34.1,
        'l_b2': 24.75,
        'l_b3': 13.1,
        'l_b4': 13,
        'l_b5': 10,
        'l_b6': 7,
        'alpha_st': 25,
        'alpha_so': 12.5,
        'r_si': 50,
        'd_so': 5,
        'd_sp': 9,
        'd_st': 40,
        'd_sy': 36,
        'w_st': 12,
        'l_st': 100,
    }

    SynR_parameters = {
        'p': 2,
        'Q': 12,
        "name": "Example_SynR_Machine",
        'rated_speed': 1800,
        'rated_current': 20,   
    }

    SynR_materials = {
        "air_mat": Air,
        "rotor_iron_mat": Arnon5,
        "stator_iron_mat": Arnon5,
        "coil_mat": Copper,
        "shaft_mat": Steel,
    }

    SynR_winding = {
        "no_of_layers": 2,
        "layer_phases": [ ['U', 'V', 'W', 'U', 'V', 'W', 'U', 'V', 'W', 'U', 'V', 'W'],
                            ['V', 'W', 'U', 'V', 'W', 'U', 'V', 'W', 'U', 'V', 'W', 'U'] ],
        "layer_polarity": [ ['+', '-', '+', '-', '+', '-', '+', '-', '+', '-', '+', '-'],
                            ['-', '+', '-', '+', '-', '+', '-', '+', '-', '+', '-', '+'] ],
        "pitch": 2,
        "Z_q": 20,
        "Kov": 1.8,
        "Kcu": 0.5,
        "phase_current_offset": 0,
    }

    Example_SynR_Machine = SynR_Machine(
        SynR_dimensions, SynR_parameters, SynR_materials, SynR_winding
    )

    ################ DEFINE SynR operating point ################
    Machine_Op_Pt = SynR_Machine_Oper_Pt(
        speed=1800,
        phi_0 = 0,
        ambient_temp=25,
        rotor_temp_rise=0,
    )

To use this code, another file must be created and placed one level outside of the ``eMach`` folder in the repository in which it lies. The 
objective of this file is to call the example machine (in this case the ``example_SynR_machine.py`` that was just created in the ``SynR_eval``
folder) and create a machine design object. 

.. code-block:: python

    import os
    import sys
    from time import time as clock_time

    os.chdir(os.path.dirname(__file__))

    from eMach.mach_eval import (MachineEvaluator, MachineDesign)
    from eMach.examples.mach_eval_examples.SynR_eval.electromagnetic_step import electromagnetic_step
    from eMach.examples.mach_eval_examples.SynR_eval.example_SynR_machine import Example_SynR_Machine, Machine_Op_Pt

    ############################ Create Evaluator ########################
    SynR_evaluator = MachineEvaluator(
        [
            electromagnetic_step
        ]
    )

    design_variant = MachineDesign(Example_SynR_Machine, Machine_Op_Pt)

    results = SynR_evaluator.evaluate(design_variant)

Example code defining the electromagnetic step is provided below. This code defines the analyzer problem class (input to the analyzer), 
initializes the analyzer class with an explanation of the required configurations, and calls the post-analyzer class. The 
``SynR_EM_PostAnalyzer`` class is used to process the torque and power data (to calculate average and ripple values) and to print the 
results. This part can be modified by user to perform further processing (calculation of losses, efficiency, torque/power density, etc.).
A copy of this file lies in the ``eMach\examples\mach_eval_examples\SynR_eval`` folder.

.. code-block:: python

    import os
    import sys
    import copy

    from mach_eval import AnalysisStep, ProblemDefinition
    from mach_eval.analyzers.electromagnetic.SynR import SynR_em_analyzer as SynR_em
    from mach_eval.analyzers.electromagnetic.SynR.SynR_em_config import SynR_EM_Config
    from examples.mach_eval_examples.SynR_eval.SynR_em_post_analyzer import SynR_EM_PostAnalyzer

    ############################ Define Electromagnetic Step ###########################
    class SynR_EM_ProblemDefinition(ProblemDefinition):
        """Converts a State into a problem"""

        def __init__(self):
            pass

        def get_problem(state):

            problem = SynR_em.SynR_EM_Problem(
                state.design.machine, state.design.settings)
            return problem

    # initialize em analyzer class with FEA configuration
    configuration = SynR_EM_Config(
        no_of_rev = 1,
        no_of_steps = 72,

        mesh_size=3, # mm
        mesh_size_rotor=1.5, # mm
        airgap_mesh_radial_div=4,
        airgap_mesh_circum_div=720,
        mesh_air_region_scale=1.05,

        only_table_results=False,
        csv_results=("Torque;Force;FEMCoilFlux;LineCurrent;JouleLoss;TotalDisplacementAngle;"
                    "JouleLoss_IronLoss;IronLoss_IronLoss;HysteresisLoss_IronLoss"),
        del_results_after_calc=False,
        run_folder=os.path.dirname(__file__) + "/run_data/",
        jmag_csv_folder=os.path.dirname(__file__) + "/run_data/jmag_csv/",

        max_nonlinear_iterations=50,
        multiple_cpus=True,
        num_cpus=4,
        jmag_scheduler=False,
        jmag_visible=True,
        scale_axial_length = True,
        jmag_version=None,
    )

    SynR_em_analysis = SynR_em.SynR_EM_Analyzer(configuration)

    electromagnetic_step = AnalysisStep(SynR_EM_ProblemDefinition, SynR_em_analysis, SynR_EM_PostAnalyzer)

Output to User
**********************************

The ``SynR_JMAG_2D_FEA_Analyzer`` returns a dictionary holding the results obtained from the transient analysis of the machine. The elements 
of this dictionary and their descriptions are provided below:

.. csv-table:: `SynR_JMAG_2D_FEA_Analyzer Output`
   :file: output_SynR_jmag2d_analyzer.csv
   :widths: 70, 70
   :header-rows: 1

As mentioned, the post analyzer is necessary to extract and compute the analyzer's computations and to interpret the results. The post analyzer 
contains the following code and lies also in the ``eMach\examples\mach_eval_examples\SynR_eval`` folder. The code contained in the post analyzer, 
in this case to find torque and power quantities, can be seen here:

.. code-block:: python

    import copy
    import numpy as np
    import os
    import sys

    from mach_eval.analyzers.torque_data import (
        ProcessTorqueDataProblem,
        ProcessTorqueDataAnalyzer,
    )

    class SynR_EM_PostAnalyzer:
        def copper_loss(self):
            return 3 * (self.I ** 2) * (self.R_wdg)

        def get_next_state(results, in_state):
            state_out = copy.deepcopy(in_state)
            machine = state_out.design.machine
            op_pt = state_out.design.settings

            ############################ Extract required info ###########################
            no_of_steps = results["no_of_steps"]
            no_of_rev = results["no_of_rev"]
            number_of_total_steps = results["current"].shape[0]
            i1 = number_of_total_steps - no_of_steps
            i2 = - int(no_of_steps / no_of_rev * 0.25)
            omega_m = machine.omega_m
            m = 3
            drive_freq = results["drive_freq"]
            R_wdg = results["stator_wdg_resistances"][0]
            R_wdg_coil_ends = results["stator_wdg_resistances"][1]
            R_wdg_coil_sides = results["stator_wdg_resistances"][2]

            results["current"] = results["current"].iloc[i1:]
            results["torque"] = results["torque"].iloc[i1:]
            results["iron_loss"] = results["iron_loss"]
            results["hysteresis_loss"] = results["hysteresis_loss"]
            results["eddy_current_loss"] = results["eddy_current_loss"]

            ############################ calculating volumes ###########################
            machine = state_out.design.machine
            V_sh = np.pi*(machine.r_sh**2)*machine.l_st
            V_rfe = machine.l_st * (np.pi * (machine.r_ro ** 2 - machine.r_ri**2) - 2 * machine.p * (machine.w_b1 * (2 * machine.l_b1 + machine.l_b4) + machine.w_b2 * (2 * machine.l_b2 + machine.l_b5) + machine.w_b3 * (2 * machine.l_b3 + machine.l_b6)))

            ############################ Post-processing #################################
            rotor_mass = (
                V_rfe * 1e-9 * machine.rotor_iron_mat["core_material_density"]
                + V_sh * 1e-9 * machine.shaft_mat["shaft_material_density"]
            )
            rotor_volume = (V_rfe + V_sh) * 1e-9

            ############################ post processing ###########################
            # Torque
            torque_prob = ProcessTorqueDataProblem(results["torque"]["TorCon"])
            torque_analyzer = ProcessTorqueDataAnalyzer()
            torque_avg, torque_ripple = torque_analyzer.analyze(torque_prob)
            TRW = torque_avg / rotor_mass
            TRV = torque_avg / rotor_volume
            PRW = TRW * omega_m
            PRV = TRV * omega_m

            # Losses
            # From JMAG
            stator_iron_loss = results["iron_loss"]["StatorCore"][0]
            rotor_iron_loss = results["iron_loss"]["RotorCore"][0]
            stator_eddy_current_loss = results["eddy_current_loss"]["StatorCore"][0]
            rotor_eddy_current_loss = results["eddy_current_loss"]["RotorCore"][0]
            stator_hysteresis_loss= results["hysteresis_loss"]["StatorCore"][0]
            rotor_hysteresis_loss = results["hysteresis_loss"]["RotorCore"][0]
            stator_ohmic_loss = results["ohmic_loss"]["Coils"].iloc[i2:].mean()
            
            # Calculate stator winding ohmic losses
            I_hat = machine.rated_current * op_pt.current_ratio * np.sqrt(2)
            stator_calc_ohmic_loss = R_wdg * m / 2 * I_hat ** 2

            # Total losses, output power, and efficiency
            total_losses = (
                stator_iron_loss + rotor_iron_loss + stator_calc_ohmic_loss)
            P_out = torque_avg * omega_m
            efficiency = P_out / (P_out + total_losses)

            ############################ Output #################################
            post_processing = {}
            post_processing["torque_avg"] = torque_avg
            post_processing["torque_ripple"] = torque_ripple
            post_processing["TRW"] = TRW
            post_processing["TRV"] = TRV
            post_processing["PRW"] = PRW
            post_processing["PRV"] = PRV
            post_processing["l_st"] = machine.l_st
            post_processing["rotor_mass"] = rotor_mass
            post_processing["rotor_volume"] = rotor_volume
            post_processing["stator_iron_loss"] = stator_iron_loss
            post_processing["rotor_iron_loss"] = rotor_iron_loss
            post_processing["stator_eddy_current_loss"] = stator_eddy_current_loss
            post_processing["rotor_eddy_current_loss"] = rotor_eddy_current_loss
            post_processing["stator_hysteresis_loss"] = stator_hysteresis_loss
            post_processing["rotor_hysteresis_loss"] = rotor_hysteresis_loss
            post_processing["stator_ohmic_loss"] = stator_ohmic_loss
            post_processing["stator_calc_ohmic_loss"] = stator_calc_ohmic_loss
            post_processing["total_losses"] = total_losses
            post_processing["output_power"] = P_out
            post_processing["efficiency"] = efficiency

            state_out.conditions.em = post_processing

            print("\n************************ ELECTROMAGNETIC RESULTS ************************")
            #print("Torque = ", torque_avg, " Nm")
            print("Torque density = ", TRV, " Nm/m3",)
            print("Torque ripple = ", torque_ripple)
            #print("Power = ", P_out, " W")
            print("Power density = ", PRV, " W/m3",)
            print("Efficiency = ", efficiency * 100, " %")
            print("*************************************************************************\n")

            return state_out

All example SynR evaluation scripts, including the one used for this analyzer, can be found in ``eMach\examples\mach_eval_examples\SynR_eval``,
where the post-analyzer script uses FEA results and calculates machine performance metrics, including torque density, power density, efficiency,
and torque ripple. This analyzer can be run by simply running the ``SynR_evaluator`` file in the aforementioned folder. This example should 
produce the following results:

.. csv-table:: `SynR_JMAG_2D_FEA_Analyzer Results`
   :file: results_SynR_jmag2d_analyzer.csv
   :widths: 70, 70, 30
   :header-rows: 1