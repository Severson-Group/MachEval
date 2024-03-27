import os
import sys
import copy
import numpy as np

from mach_eval import AnalysisStep, ProblemDefinition
from mach_eval.analyzers.electromagnetic import inductance_analyzer as inductance

############################ Define Electromagnetic Step ###########################
class SynR_Ind_ProblemDefinition(ProblemDefinition):
    """Converts a State into a problem"""

    def __init__(self):
        pass

    def get_problem(state):

        problem = inductance.Inductance_Problem(
            state.conditions.I_hat, state.conditions.path, state.conditions.study_name, state.conditions.rotor_angle, state.conditions.name_of_phases)
        return problem

clarke_transformation_matrix = 2/3*np.array([[1, -1/2, -1/2], [0, np.sqrt(3)/2, -np.sqrt(3)/2], [1/2, 1/2, 1/2]])

class SynR_Inductance_PostAnalyzer:
    
    def get_next_state(results, in_state):
        state_out = copy.deepcopy(in_state)

        state_out.conditions.Lalpha = results["Lalpha"]
        state_out.conditions.Lbeta = results["Lbeta"]
        state_out.conditions.Ld = results["Ld"]
        state_out.conditions.Lq = results["Lq"]
        L_d = sum(state_out.conditions.Ld)/len(state_out.conditions.Ld)
        L_q = sum(state_out.conditions.Lq)/len(state_out.conditions.Lq)
        saliency_ratio = L_d/L_q

        print("\n************************ INDUCTANCE RESULTS ************************")
        print("Ld = ", L_d, " H")
        print("Lq = ", L_q, " H")
        print("Saliency Ratio = ", saliency_ratio)
        print("*************************************************************************\n")

        return state_out

SynR_inductance_analysis = inductance.Inductance_Analyzer(clarke_transformation_matrix)

SynR_inductance_step = AnalysisStep(SynR_Ind_ProblemDefinition, SynR_inductance_analysis, SynR_Inductance_PostAnalyzer)