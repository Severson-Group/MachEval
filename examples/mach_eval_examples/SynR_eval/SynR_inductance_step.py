#%%
import os
import sys
import copy
import numpy as np
import matplotlib.pyplot as plt

from mach_eval import AnalysisStep, ProblemDefinition
from mach_eval.analyzers.electromagnetic import inductance_analyzer as inductance

############################ Define Inductance Step ###########################
class SynR_Ind_ProblemDefinition(ProblemDefinition):
    """Converts a State into a problem"""

    def __init__(self):
        pass

    def get_problem(state):

        problem = inductance.Inductance_Problem(
            state.conditions.I_hat, 
            state.conditions.path, 
            state.conditions.study_name, 
            state.conditions.rotor_angle, 
            state.conditions.name_of_phases)
        return problem

clarke_transformation_matrix = 2/3*np.array([[1, -1/2, -1/2], [0, np.sqrt(3)/2, -np.sqrt(3)/2], [1/2, 1/2, 1/2]])

class SynR_Inductance_PostAnalyzer:
    
    def get_next_state(results, in_state):
        state_out = copy.deepcopy(in_state)

        state_out.conditions.rotor_angle = results["rotor_angle"]
        state_out.conditions.Lalphabeta = results["Lalphabeta"]
        state_out.conditions.Ldq = results["Ldq"]
        L_d = np.mean(state_out.conditions.Ldq[:,0,0])
        L_q = np.mean(state_out.conditions.Ldq[:,1,1])
        saliency_ratio = L_d/L_q

        fig1 = plt.figure()
        ax1 = plt.axes()
        fig1.add_axes(ax1)
        ax1.plot(state_out.conditions.rotor_angle[0], state_out.conditions.Lalphabeta[:,0,0]*1000)
        ax1.plot(state_out.conditions.rotor_angle[0], state_out.conditions.Lalphabeta[:,0,1]*1000)
        ax1.plot(state_out.conditions.rotor_angle[0], state_out.conditions.Lalphabeta[:,1,0]*1000)
        ax1.plot(state_out.conditions.rotor_angle[0], state_out.conditions.Lalphabeta[:,1,1]*1000)
        ax1.plot(state_out.conditions.rotor_angle[0], state_out.conditions.Lalphabeta[:,2,2]*1000)
        ax1.set_xlabel("Rotor Angle [deg]")
        ax1.set_ylabel("Inductance [mH]")
        ax1.set_title(r"$\alpha \beta \gamma$ Inductances")
        plt.legend([r"$L_{\alpha \alpha}$", r"$L_{\alpha \beta}$", r"$L_{\beta \alpha}$", r"$L_{\beta \beta}$", r"$L_{\gamma \gamma}$"], fontsize=12)
        plt.grid(True, linewidth=0.5, color="#A9A9A9", linestyle="-.")
        plt.show()

        fig2 = plt.figure()
        ax2 = plt.axes()
        fig2.add_axes(ax2)
        plt.plot(state_out.conditions.rotor_angle[0], state_out.conditions.Ldq[:,0,0]*1000)
        plt.plot(state_out.conditions.rotor_angle[0], state_out.conditions.Ldq[:,1,1]*1000)
        plt.plot(state_out.conditions.rotor_angle[0], state_out.conditions.Ldq[:,2,2]*1000)
        ax2.set_xlabel("Rotor Angle [deg]")
        ax2.set_ylabel("Inductance [mH]")
        ax2.set_title("dq0 Inductances")
        plt.legend(["$L_d$", "$L_q$", "$L_0$"], fontsize=12)
        plt.grid(True, linewidth=0.5, color="#A9A9A9", linestyle="-.")
        plt.show()

        print("\n************************ INDUCTANCE RESULTS ************************")
        print("Ld = ", L_d*1000, " mH")
        print("Lq = ", L_q*1000, " mH")
        print("Saliency Ratio = ", saliency_ratio)
        print("*************************************************************************\n")

        return state_out

SynR_inductance_analysis = inductance.Inductance_Analyzer(clarke_transformation_matrix)

SynR_inductance_step = AnalysisStep(SynR_Ind_ProblemDefinition, SynR_inductance_analysis, SynR_Inductance_PostAnalyzer)