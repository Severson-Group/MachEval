import os
import sys

# add the directory 3 levels above this file's directory to path for module import
sys.path.append(os.path.dirname(__file__)+"/../../..")
sys.path.append(os.path.dirname(__file__))

from mach_eval.analyzers.electromagnetic.bspm import jmag_2d as em
from mach_eval.analyzers.electromagnetic.bspm.jmag_2d_config import JMAG_2D_Config
from bspm_em_post_analyzer import BSPM_EM_PostAnalyzer
from mach_eval import AnalysisStep, ProblemDefinition


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
    jmag_version="21.1",
)
em_analysis = em.BSPM_EM_Analyzer(jmag_config)
# define AnalysysStep for EM evaluation
em_step = AnalysisStep(BSPM_EM_ProblemDefinition, em_analysis, BSPM_EM_PostAnalyzer)
