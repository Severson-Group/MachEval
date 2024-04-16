import os
import sys
import copy

from mach_eval import AnalysisStep, ProblemDefinition
import Vision_SynR_opt_analyzer as Vision_SynR_opt
from Vision_SynR_opt_config import Vision_SynR_Opt_Config
from Vision_SynR_opt_post_analyzer import Vision_SynR_Opt_PostAnalyzer

############################ Define Structural Step ###########################
class Vision_SynR_Opt_ProblemDefinition(ProblemDefinition):
    """Converts a State into a problem"""

    def __init__(self):
        pass

    def get_problem(state):

        problem = Vision_SynR_opt.Vision_SynR_Opt_Problem(
            state.design.machine, state.design.settings)
        return problem

# initialize em analyzer class with FEA configuration
configuration = Vision_SynR_Opt_Config(
    no_of_rev = 1,
    no_of_steps = 72,

    mesh_size=3, # mm
    mesh_size_rotor=0.1, # mm
    airgap_mesh_radial_div=4,
    airgap_mesh_circum_div=768,
    mesh_air_region_scale=1.05,

    only_table_results=False,
    csv_struct_results="CsvOutputCalculation",
    csv_em_results= ("Torque;Force;FEMCoilFlux;LineCurrent;JouleLoss;TotalDisplacementAngle;"
                  "JouleLoss_IronLoss;IronLoss_IronLoss;HysteresisLoss_IronLoss"),
    del_results_after_calc=False,
    run_folder=os.path.dirname(__file__) + "/run_data/",
    jmag_csv_folder=os.path.dirname(__file__) + "/run_data/jmag_csv/",

    max_nonlinear_iterations=50,
    multiple_cpus=True,
    num_cpus=8,
    jmag_scheduler=False,
    jmag_visible=True,
    scale_axial_length = True,
)

Vision_SynR_opt_analysis = Vision_SynR_opt.Vision_SynR_Opt_Analyzer(configuration)

optimization_vision_step = AnalysisStep(Vision_SynR_Opt_ProblemDefinition, Vision_SynR_opt_analysis, Vision_SynR_Opt_PostAnalyzer)