Flux Linkage Analyzer
########################################################################

This analyzer enables the flux linkage evaluation of a mutli-phase electric machine after running 2D FEA simulations using JMAG.

Model Background
****************

The flux linkage of a coil is defined as the amount of flux linking together for a multi-coil arrangment with electric current flowing 
through them. The flux linkage of a coil within an electric machine comes from all coils present in the machine and has a profound 
impact on the machine characteristics. Calculating coil flux linkages over time can lead to inductance calculations for an electric 
machine, which are also important for characterizing that machine. The flux linkage is an important parameter for inductance calculations
as can be seen in the following equation:

.. math::

    L = \lambda I \\

where :math:`\lambda` is the flux linkage, :math:`L` is the inductance, and :math:`I` is the coil current.

The code is structured such that the ``flux_linkage_analyzer`` contains the code for setting up and running the JMAG simulations based on 
1) the machine inputs and conditions of the user and 2) the conditions required of the machine to be able to calculate the 
necessary parameters. In the case of each machine, DC excitement of each phase coil occurs with all other coils open. This repeats for 
each coil until all of the coils have been excited with DC current and all of the flux linkages have been captured. 

This analyzer calculates the self and mutual flux linkages of each coil using JMAG's transient solver. It models an electric machine 
under synchronous operation. The following information document will provide a description of the analyzer inputs and outputs.

Input from User
*********************************

This analyzer is used in the same way as the ``SynR_JMAG_2D_FEA_Analyzer``. The inputs and initialization are the exact same and are shown
in the tables below:

.. csv-table:: `MachineDesign Input`
   :file: input_SynR_jmag2d_analyzer.csv
   :widths: 70, 70
   :header-rows: 1

.. csv-table:: `SynR_flux_linkage_analyzer Initialization`
   :file: init_SynR_jmag2d_analyzer.csv
   :widths: 70, 70
   :header-rows: 1

Example Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example code defining the flux linkage step is provided below. This code defines the analyzer problem class (input to the analyzer), 
initializes the analyzer class with an explanation of the required configurations, and calls the post-analyzer class.

.. code-block:: python

    import os
    import copy

    from mach_eval import AnalysisStep, ProblemDefinition
    from mach_eval.analyzers.electromagnetic import flux_linkage_analyzer as flux_linkage
    from mach_eval.analyzers.electromagnetic.flux_linkage_analyzer_config import Flux_Linkage_Config

    ############################ Define Flux Linkage Step ###########################
    class SynR_EM_ProblemDefinition(ProblemDefinition):
        """Converts a State into a problem"""

        def __init__(self):
            pass

        def get_problem(state):

            problem = flux_linkage.Flux_Linkage_Problem(
                state.design.machine, state.design.settings)
            return problem

    # initialize em analyzer class with FEA configuration
    configuration = Flux_Linkage_Config(
        no_of_rev = 1,
        no_of_steps = 72,

        mesh_size=3, # mm
        mesh_size_rotor=1.5, # mm
        airgap_mesh_radial_div=4,
        airgap_mesh_circum_div=720,
        mesh_air_region_scale=1.05,

        only_table_results=False,
        csv_results=("FEMCoilFlux"),
        del_results_after_calc=False,
        run_folder=os.path.dirname(__file__) + "/run_data/",
        jmag_csv_folder=os.path.dirname(__file__) + "/run_data/jmag_csv/",

        max_nonlinear_iterations=50,
        multiple_cpus=True,
        num_cpus=4,
        jmag_scheduler=False,
        jmag_visible=True,
        non_zero_end_ring_res = False,
        scale_axial_length = True,
        time_step = 0.0001
    )

    class SynR_Flux_Linkage_PostAnalyzer:
        
        def get_next_state(results, in_state):
            state_out = copy.deepcopy(in_state)

            state_out.conditions.path = results["csv_folder"]
            state_out.conditions.study_name = results["study_name"]
            state_out.conditions.I_hat = results["current_peak"]
            state_out.conditions.rotor_angle = results["rotor_angle"]
            state_out.conditions.name_of_phases = results["name_of_phases"]

            print("\n************************ FLUX LINKAGE RESULTS ************************")
            print("path = ", state_out.conditions.path)
            print("study_name = ", state_out.conditions.study_name)
            print("I_hat = ", state_out.conditions.I_hat, " A")
            print("rotor_angle = ", state_out.conditions.rotor_angle, " deg")
            print("name_of_phases = ", state_out.conditions.name_of_phases)
            print("*************************************************************************\n")

            return state_out

    SynR_flux_linkage_analysis = flux_linkage.Flux_Linkage_Analyzer(configuration)

    SynR_flux_linkage_step = AnalysisStep(SynR_EM_ProblemDefinition, SynR_flux_linkage_analysis, SynR_Flux_Linkage_PostAnalyzer)

It should be noted that this code should be contained as an analysis step in the main folder of the eMach repository. It must be contained 
within the same folder as the code below in order for the code below to run.

Output to User
**********************************

The ``SynR_flux_linkage_analyzer`` returns a directory holding the results obtained from the transient analysis of the machine. The elements 
of this dictionary and their descriptions are provided below:

.. csv-table:: `SynR_flux_linkage_analyzer Output`
   :file: output_flux_linkage_analyzer.csv
   :widths: 70, 70
   :header-rows: 1

The following code should be used to run the example analysis:

.. code-block:: python

    import os
    import sys
    from time import time as clock_time

    os.chdir(os.path.dirname(__file__))

    from mach_eval import (MachineEvaluator, MachineDesign)
    from examples.mach_eval_examples.SynR_eval.SynR_flux_linkage_step import SynR_flux_linkage_step
    from examples.mach_eval_examples.SynR_eval.example_SynR_machine import Example_SynR_Machine, Machine_Op_Pt

    ############################ Create Evaluator ########################
    SynR_evaluator = MachineEvaluator(
        [
            SynR_flux_linkage_step
        ]
    )

    design_variant = MachineDesign(Example_SynR_Machine, Machine_Op_Pt)

    results = SynR_evaluator.evaluate(design_variant)

All example SynR evaluation scripts, including the one used for this analyzer, can be found in ``eMach\examples\mach_eval_examples\SynR_eval``,
where the post-analyzer script uses FEA results and calculates machine performance metrics, including torque density, power density, efficiency,
and torque ripple. This analyzer can be run by simply running the ``SynR_evaluator`` file in the aforementioned folder using the ``flux_linkage_step``.

This example, contained in the aforementioned ``SynR_eval`` folder, should produce the following results:

.. csv-table:: `flux_linkage_analyzer Results`
   :file: results_flux_linkage_analyzer.csv
   :widths: 70, 70, 30
   :header-rows: 1

One should expect the csv_folder location to differ depending on where the desired destination is. Within the ``resuls_folder`` there should be a 
total of 6 csv files that contains the information requested in the ``_step`` file.