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