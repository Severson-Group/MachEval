BSPM Evaluation Tutorial
===========================================

* **Goal:** Leverage capabilites of ``mach_eval`` to perform multi-physics evaluations on bearingless surface permanent magnet machines
* **Complexity:** 4/5
* **Estimated Time:** 30 - 60 min

This tutorial demonstrates how to perform a multi-physics evaluation of a ``BSPM_Machine`` by using the ``Analyzers`` available in ``eMach``.
By the end of this tutorial you will be able to:

* create a digital BSPM design
* use ``mach_eval`` analyzers together to perform multi-physics evaluations of BSPMs


Requirements 
---------------------

#. Python packages installed on system per :doc:`Pre-requisites <../../pre_reqs>`
#. Installation of JMAG v19 or above
#. Personal repo using ``eMach`` as submodule established (see :doc:`Rectangle Tutorial <../rectangle_tutorial/index>`)
#. (Recommended but not required) Review of mechanical and electromagnetic analyzers provided in ``mach_eval``


Step 1: Create a BSPM Design
----------------------------------------------------------------------

In the root folder of your repository, create a Python file named ``ecce_2020_bspm.py``. The code required to create an example BSPM design will
reside within this file. You can create this file by simply copying the ``ecce_2020_bspm.py`` file residing within 
``examples/mach_eval_examples/bspm_eval`` and updating the import statements as shown below.

.. code-block:: python

    import os
    import sys
    from eMach.mach_eval.machines.materials.electric_steels import Arnon5
    from eMach.mach_eval.machines.materials.jmag_library_magnets import N40H
    from eMach.mach_eval.machines.materials.miscellaneous_materials import (
        CarbonFiber,
        Steel,
        Copper,
        Hub,
        Air,
    )
    from eMach.mach_eval.machines.bspm import BSPM_Machine
    from eMach.mach_eval.machines.bspm.bspm_oper_pt import BSPM_Machine_Oper_Pt

Step 2: Create BSPM Evaluator
--------------------------------------------------------------------

The main purpose of this tutorial is to showcase how multi-physics evaluations are handled by ``eMach`` using the analyzers
provided within the repository. To demonstrate this, the structural, electromagnetic, and thermal performance of the example BSPM design created 
in ``ecce_2020_bspm.py`` are evaluated. ``AnalysisStep`` objects are created for each analyzer to ensure proper interface to and from the 
analyzers. The ``AnalysisSteps`` are then joined together to create an ``Evaluator``, in a manner so as to 
ensure proper transfer of information and to facilitate computational efficiency during optimization. In this particular example, the thermal
analyzers come after the electromagnetic analyzers as thermal performance is determined by motor losses. The structural analyzer is placed 
at the very beginning as this is a quick equation-based analyzer which determines whether an appropriate sized sleeve can be placed on an 
SPM rotor or not. Machines which are structurally unsound can be discarded prior to the computationally intensive electromagnetic 
``AnalysisStep``, thereby saving time. The steps involved in created a multi-physics BSPM ``Evaluator`` are discussed below. Readers can 
create a single Python script holding all the code snippets provided below or can separate them out into individual modules as done in  
``examples/mach_eval_examples/bspm_eval``.

Step 2.1: Create Structual ``AnalysisStep``
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

In this step, we define the interface between a BSPM design and the SPM rotor retaining :doc:`sleeve analyzer <../../../mechanical_analyzers/SPM_sleeve_analyzer>`. 
The purpose of this analyzer is to determine if a retaining sleeve of sufficient strength can be applied on the SPM rotor to hold the magnets
in place at rated speed. The code snip provided below shows how this analyzer can be interfaced to a BSPM design. After the analysis is 
completed, the design is either discarded if the analyzer was unable to find an appropriately sized sleeve, or a clone of the ``BSPM_Machine`` 
is created having the sleeve size required for magnet retention.   

.. code-block:: python

    from copy import deepcopy

    from eMach.mach_eval.analyzers.mechanical import rotor_structural as stra
    from eMach.mach_eval import AnalysisStep, ProblemDefinition
    from eMach.mach_opt import InvalidDesign

    ############################ Define Struct AnalysisStep ######################
    stress_limits = {
        "rad_sleeve": -100e6,
        "tan_sleeve": 1300e6,
        "rad_magnets": 0,
        "tan_magnets": 80e6,
    }

    struct_ana = stra.SPM_RotorSleeveAnalyzer(stress_limits)

    class MySleeveProblemDef(ProblemDefinition):
        def get_problem(state):
            design = state.design
            material_dict = {}
            for key, value in design.machine.rotor_iron_mat.items():
                material_dict[key] = value
            for key, value in design.machine.magnet_mat.items():
                material_dict[key] = value
            for key, value in design.machine.rotor_sleeve_mat.items():
                material_dict[key] = value
            for key, value in design.machine.shaft_mat.items():
                material_dict[key] = value

            r_sh = design.machine.r_sh
            r_ro = design.machine.r_ro
            d_m = design.machine.d_m
            N = design.settings.speed
            deltaT = design.settings.rotor_temp_rise

            problem = stra.SPM_RotorSleeveProblem(r_sh, d_m, r_ro, deltaT, material_dict, N)
            return problem

    class MyStructPostAnalyzer:
        """Converts a State into a problem"""

        def get_next_state(results, in_state):
            if results is False:
                raise InvalidDesign("Suitable sleeve not found")
            else:
                print("Suitable sleeve found!")
                machine = in_state.design.machine
                new_machine = machine.clone(dimensions_dict={"d_sl": results[0]})
            state_out = deepcopy(in_state)
            state_out.design.machine = new_machine
            return state_out

    struct_step = AnalysisStep(MySleeveProblemDef, struct_ana, MyStructPostAnalyzer)


.. note:: If you get stuck at any point of the tutorial, the ``examples/mach_eval_examples/bspm_eval folder`` provides a working example of 
    creating and evaluating the BSPM design discussed in this tutorial.


Step 2.2: Create Electromagnetic ``AnalysisStep``
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

In this step, we define the interface between a BSPM design and the :doc:`BSPM JMAG 2D FEA Analyzer <../../../EM_analyzers/bspm_jmag2d_analyzer>`. 
The purpose of this analyzer is to run a JMAG 2D FEA simulation of an input BSPM machine and return data relevant to the performance of
this machine. The input provided to this analyzer is the BSPM machine and its operating point. The analyzer returns a set of dataframes
extracted from JMAG 2D FEA solve which can be interpreted to determine the motor losses and torque and force performance. As interpreting this
information can be challenging, readers are advised to copy the ``bpsm_em_post_analyzer.py`` script file in ``examples/mach_eval_examples/bspm_eval`` 
to post-process FEA results. Simply modify the import statements as shown below.

.. code-block:: python

    import copy
    import numpy as np

    from mach_eval.analyzers.force_vector_data import (
        ProcessForceDataProblem,
        ProcessForceDataAnalyzer,
    )
    from mach_eval.analyzers.torque_data import (
        ProcessTorqueDataProblem,
        ProcessTorqueDataAnalyzer,
    )

The code snip provided below shows how this analyzer can be interfaced to a BSPM design. After the analysis is completed, relevant information 
is stored in ``State`` for future reference. It is worth noting that the losses obtained from this analysis are required by the next two thermal 
``AnalysisSteps`` to determine the rotor and stator temperatures.

.. code-block:: python
	
    from eMach.mach_eval.analyzers.electromagnetic.bspm import jmag_2d as em
    from eMach.mach_eval.analyzers.electromagnetic.bspm.jmag_2d_config import JMAG_2D_Config
    from eMach.examples.mach_eval_examples.bspm_eval.bpsm_em_post_analyzer import BSPM_EM_PostAnalyzer
    from eMach.mach_eval import AnalysisStep, ProblemDefinition


    ############################ Define EMAnalysisStep ###########################
    class BSPM_EM_ProblemDefinition(ProblemDefinition):
        """Converts a State into a problem"""

        def __init__(self):
            pass

        def get_problem(state):
            problem = em.BSPM_EM_Problem(state.design.machine, state.design.settings)
            return problem


    # initialize em analyzer class with FEA configuration
    jmag_config = JMAG_2D_Config(
        no_of_rev_1TS=3,
        no_of_rev_2TS=0.5,
        no_of_steps_per_rev_1TS=8,
        no_of_steps_per_rev_2TS=64,
        mesh_size=4e-3,
        magnet_mesh_size=2e-3,
        airgap_mesh_radial_div=5,
        airgap_mesh_circum_div=720,
        mesh_air_region_scale=1.15,
        only_table_results=False,
        csv_results=(r"Torque;Force;FEMCoilFlux;LineCurrent;TerminalVoltage;JouleLoss;TotalDisplacementAngle;"
                    "JouleLoss_IronLoss;IronLoss_IronLoss;HysteresisLoss_IronLoss"),
        del_results_after_calc=False,
        run_folder=os.path.dirname(__file__) + "/run_data/",
        jmag_csv_folder=os.path.dirname(__file__) + "/run_data/JMAG_csv/",
        max_nonlinear_iterations=50,
        multiple_cpus=True,
        num_cpus=4,
        jmag_scheduler=False,
        jmag_visible=False,
        jmag_version=None,
    )
    em_analysis = em.BSPM_EM_Analyzer(jmag_config)
    # define AnalysysStep for EM evaluation
    em_step = AnalysisStep(BSPM_EM_ProblemDefinition, em_analysis, BSPM_EM_PostAnalyzer)

Step 2.3: Create Rotor Thermal ``AnalysisStep``
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

In this step, we define the interface between a BSPM design and the :doc:`SPM Airflow Analyzer <../../../mechanical_analyzers/SPM_rotor_airflow_analyzer>`. 
The purpose of this analyzer is evaluate the airflow required (under certain bounds) to prevent the BSPM machine magnets from overheating at 
the provided operating conditions. The code snip provided below shows how this analyzer can be interfaced to a BSPM design and the loss data
obtained from FEA. After the analysis is completed, the design is discarded if the magnets get overheated. If the magnets are not at risk of
de-magnetization from high temperatures, the required airflow and the corresponding magnet temperature rises are saved for future reference.

.. code-block:: python
	
    from copy import deepcopy
    import numpy as np

    from eMach.mach_eval.analyzers.mechanical import rotor_thermal as therm
    from eMach.mach_eval import AnalysisStep, ProblemDefinition
    from eMach.mach_opt import InvalidDesign


    ###################### Define Rotor Thermal AnalysisStep #####################
    class MyAirflowProblemDef(ProblemDefinition):
        def get_problem(state):
            design = state.design
            material_dict = {}
            for key, value in design.machine.rotor_iron_mat.items():
                material_dict[key] = value
            for key, value in design.machine.magnet_mat.items():
                material_dict[key] = value
            for key, value in design.machine.rotor_sleeve_mat.items():
                material_dict[key] = value
            for key, value in design.machine.shaft_mat.items():
                material_dict[key] = value
            for key, value in design.machine.air_mat.items():
                material_dict[key] = value
            for key, value in design.machine.rotor_hub.items():
                material_dict[key] = value

            r_sh = design.machine.r_sh
            d_ri = design.machine.d_ri
            r_ro = design.machine.r_ro
            d_sl = design.machine.d_sl
            r_si = design.machine.r_si
            l_st = design.machine.l_st
            l_hub = 3e-3
            T_ref = design.settings.ambient_temp
            omega = design.settings.speed * 2 * np.pi / 60
            losses = state.conditions.em
            rotor_max_temp = material_dict["magnet_max_temperature"]
            prob = therm.AirflowProblem(
                r_sh=r_sh,
                d_ri=d_ri,
                r_ro=r_ro,
                d_sl=d_sl,
                r_si=r_si,
                l_st=l_st,
                l_hub=l_hub,
                T_ref=T_ref,
                losses=losses,
                omega=omega,
                max_temp=rotor_max_temp,
                mat_dict=material_dict,
            )
            return prob


    class MyAirflowPostAnalyzer:
        """Converts a State into a problem"""

        def get_next_state(results, in_state):
            if results["valid"] is False:
                raise InvalidDesign("Magnet temperature beyond limits")
            else:
                state_out = deepcopy(in_state)
                state_out.conditions.airflow = results
            print("Magnet temperature is ", results["magnet Temp"])
            print("Required airflow is ", results["Required Airflow"])
            return state_out


    rotor_therm_step = AnalysisStep(
        MyAirflowProblemDef, therm.AirflowAnalyzer(), MyAirflowPostAnalyzer
    )

Step 2.4: Create Stator Thermal ``AnalysisStep``
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

In this step, we define the interface between a BSPM design and the :doc:`Stator Thermal Analyzer <../../../mechanical_analyzers/inner_rotor_stator_thermal_analyzer>`. 
The purpose of this analyzer is evaluate the stator winding temperature for a provided stator outer bore convection coefficient. 
The cooling rate is set at ``h = 200 W/m^2K`` for this evaluation. The code snip provided below shows how this analyzer can be interfaced to 
a BSPM design and the loss data obtained from FEA. After the analysis is completed, the stator winding and yoke temperatures are saved for 
future reference if the coil temperature is under 300 degC.

.. code-block:: python
	
    from copy import deepcopy
    import numpy as np

    from mach_eval.analyzers.mechanical import thermal_stator as st_therm
    from mach_eval import AnalysisStep, ProblemDefinition
    from mach_opt import InvalidDesign


    ###################### Define Stator Thermal AnalysisStep #####################
    class MyThermalProblemDefinition(ProblemDefinition):
        """Class converts input state into a problem"""

        def get_problem(state):
            """Returns Problem from Input State"""
            # TODO define problem definition
            g_sy = state.conditions.g_sy  # Volumetric loss in Stator Yoke [W/m^3]
            g_th = state.conditions.g_th  # Volumetric loss in Stator Tooth [W/m^3]
            w_st = state.design.machine.w_st  # Tooth width [m]
            l_st = state.design.machine.l_st  # Stack length [m]
            r_sy = state.design.machine.r_so - state.design.machine.d_sy
            alpha_q = 2 * np.pi / state.design.machine.Q  # [rad]
            r_so = state.design.machine.r_so  # outer stator radius [m]

            k_ins = 1  # thermal insulation conductivity (~1)
            w_ins = 0.5e-3  # insulation thickness [m] (.5mm)
            k_fe = state.design.machine.stator_iron_mat["core_therm_conductivity"]
            h = 200  # convection co-eff W/m^2K
            alpha_slot = alpha_q - 2 * np.arctan(
                w_st / (2 * r_sy)
            )  # span of back of stator slot [rad]
            T_ref = 20  # temperature of cooling liquid [K]

            r_si = state.design.machine.r_si  # inner stator radius
            Q_coil = state.conditions.Q_coil  # ohmic loss per coil
            h_slot = 0  # in slot convection coeff [W/m^2K] set to 0

            problem = st_therm.StatorThermalProblem(
                g_sy=g_sy,
                g_th=g_th,
                w_tooth=w_st,
                l_st=l_st,
                alpha_q=alpha_q,
                r_si=r_si,
                r_so=r_so,
                r_sy=r_sy,
                k_ins=k_ins,
                w_ins=w_ins,
                k_fe=k_fe,
                h=h,
                alpha_slot=alpha_slot,
                Q_coil=Q_coil,
                h_slot=h_slot,
                T_ref=T_ref,
            )
            return problem


    class MyStatorThermalPostAnalyzer:
        """Converts input state into output state for TemplateAnalyzer"""

        def get_next_state(results, stateIn):
            if results["Coil temperature"] > 300 == True:
                raise InvalidDesign("Coil temperature beyond limits")
            else:
                stateOut = deepcopy(stateIn)
                stateOut.conditions.T_coil = results["Coil temperature"]
                stateOut.conditions.T_sy = results["Stator yoke temperature"]

            print("Coil Temp is ", results["Coil temperature"])
            print("Stator Temp is ", results["Stator yoke temperature"])
            return stateOut


    stator_therm_step = AnalysisStep(
        MyThermalProblemDefinition,
        st_therm.StatorThermalAnalyzer(),
        MyStatorThermalPostAnalyzer,
    )

Step 2.5: Create Windage Loss ``AnalysisStep``
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Finally, an ``AnalysisStep`` is created to define the interface between the BSPM design and the :doc:`Windage Loss Analyzer <../../../mechanical_analyzers/windage_loss_analyzer>`.
The purpose of this analyzer is evaluate the windage loss arising in a BSPM due to rotational speed of the machine. The code snip provided 
below shows how this analyzer can be interfaced to a BSPM design and the required rotor axial airflow for cooling the magnets. After the 
analysis is completed, the overall efficiency of the motor is calculated and saved.

.. code-block:: python
	
    from copy import deepcopy
    import numpy as np

    # add the directory 3 levels above this file's directory to path for module import
    sys.path.append(os.path.dirname(__file__)+"../../..")

    from mach_eval.analyzers.mechanical import windage_loss as wl
    from mach_eval import AnalysisStep, ProblemDefinition


    ############################ Define Windage AnalysisStep #####################
    class MyWindageProblemDef(ProblemDefinition):
        def get_problem(state):
            design = state.design
            omega = design.settings.speed * 2 * np.pi / 60
            r_ro = design.machine.r_ro + design.machine.d_sl
            l_st = design.machine.l_st
            r_si = design.machine.r_si
            m_dot_air = state.conditions.airflow["Required Airflow"]
            T_air = design.settings.ambient_temp

            prob = wl.WindageLossProblem(omega, r_ro, l_st, r_si, m_dot_air, T_air)
            return prob


    class MyWindageLossPostAnalyzer:
        """Converts a State into a problem"""

        def get_next_state(results, in_state):
            state_out = deepcopy(in_state)
            omega = state_out.design.settings.speed * 2 * np.pi / 60
            Pout = state_out.conditions.em["torque_avg"] * omega
            eff = (
                100
                * Pout
                / (
                    Pout
                    + results[0]
                    + results[1]
                    + results[2]
                    + state_out.conditions.em["copper_loss"]
                    + state_out.conditions.em["rotor_iron_loss"]
                    + state_out.conditions.em["stator_iron_loss"]
                    + state_out.conditions.em["magnet_loss"]
                )
            )
            state_out.conditions.windage = {"loss": results, "efficiency": eff}
            print("Efficiency is ", eff)
            return state_out

    windage_step = AnalysisStep(
        MyWindageProblemDef, wl.WindageLossAnalyzer, MyWindageLossPostAnalyzer
    )

Step 2.6: Create the Multi-Physics ``Evaluator``
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Simply merge all the ``AnalysisStep`` s in the order in which they were defined above to create the ``Evaluator``. The code provided below
assumes each ``AnalysisStep`` was defined in a separate Python file / module. Readers are advised to name this file ``bspm_evaluator.py``.

.. code-block:: python

    from mach_eval import MachineEvaluator
    from examples.mach_eval_examples.bspm_eval.structural_step import struct_step
    from examples.mach_eval_examples.bspm_eval.electromagnetic_step import em_step
    from examples.mach_eval_examples.bspm_eval.rotor_thermal_step import rotor_therm_step
    from examples.mach_eval_examples.bspm_eval.stator_thermal_step import stator_therm_step
    from examples.mach_eval_examples.bspm_eval.windage_loss_step import windage_step

    ############################ Create Evaluator ########################
    bspm_evaluator = MachineEvaluator(
        [
            struct_step,
            em_step,
            rotor_therm_step,
            stator_therm_step,
            windage_step,
        ]
    )

Step 3: Evaluate BSPM Design
--------------------------------------------------------------------
	
To evaluate the BSPM machine created in Step 1 at the defined operating point, we need to instantiate a ``MachineDesign`` object and pass it 
as an argument to the ``evaluate`` method of the ``bspm_evaluator`` created in the preceding step. The code below is provided in a manner 
such that the BSPM design is evaluated only when users try to run the ``bspm_evaluator.py`` file.

.. code-block:: python
	
    if __name__ == "__main__":
        from ecce_2020_bspm import ecce_2020_machine, ecce_2020_op_pt
        from mach_eval import MachineDesign

        ecce_2020_design = MachineDesign(ecce_2020_machine, ecce_2020_op_pt)
        results = bspm_evaluator.evaluate(ecce_2020_design)

Upon running this script you should get the following results:

- Suitable sleeve found! Thickness =  0.00093  m
- Torque =  0.33  Nm 
- Torque Density = 70260.15 Nm/m3
- Power = 5519.5 W
- Force = 0.63 N
- Force per rotor wieght = 1.81 pu 
- Force error angle = 1.06 deg 
- Magnet temperature = 54.7 degC
- Coil temperature = 169.5 degC
- Stator temperature = 161.5 degC
- Efficiency = 97.2\%

.. note:: The ``examples/mach_eval_examples/bspm_eval`` folder provides working code for the tutorial discussed here. You can run the 
    ``bspm_evaluator.py`` script here to evaluate the ``ecce_2020_design`` and compare the results against those obtained from your own 
    ``Evaluator``.

Conclusion
----------------

Congratulations! You have successfully used ``eMach`` to create a digital BSPM design and a multi-physics BSPM evaluator as well! You can now
attempt evaluating other BSPM designs using this evaluator and see what results you end up with.

