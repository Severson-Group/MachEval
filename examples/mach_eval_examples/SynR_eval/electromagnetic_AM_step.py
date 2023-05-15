import os
import sys
import copy

from mach_eval import AnalysisStep, ProblemDefinition
from mach_eval.analyzers.electromagnetic.SynR import AM_SynR_em_analyzer as AM_SynR_em
from mach_eval.analyzers.electromagnetic.SynR.AM_SynR_em_config import AM_SynR_EM_Config
from examples.mach_eval_examples.SynR_eval.AM_SynR_em_post_analyzer import AM_SynR_EM_PostAnalyzer

############################ Define Electromagnetic Step ###########################
class AM_SynR_EM_ProblemDefinition(ProblemDefinition):
    """Converts a State into a problem"""

    def __init__(self):
        pass

    def get_problem(state):

        problem = AM_SynR_em.AM_SynR_EM_Problem(
            state.design.machine, state.design.settings)
        return problem

# initialize em analyzer class with FEA configuration
configuration = AM_SynR_EM_Config(
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
    num_cpus=12,
    jmag_scheduler=False,
    jmag_visible=True,
    non_zero_end_ring_res = False,
    scale_axial_length = True,
)

AM_SynR_em_analysis = AM_SynR_em.AM_SynR_EM_Analyzer(configuration)

electromagnetic_AM_step = AnalysisStep(AM_SynR_EM_ProblemDefinition, AM_SynR_em_analysis, AM_SynR_EM_PostAnalyzer)