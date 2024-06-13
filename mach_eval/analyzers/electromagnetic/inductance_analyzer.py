import numpy as np
import pandas as pd
import numpy as np

class InductanceProblem:
    """Problem class for inductance data processing
    Attributes:
        I_hat: peak current value for inductance calculations
        linkages: arrays of flux linkages, should be (m+1) x m for m-phase machine
        rotor_angle: array of rotor angle values for inductance calculations
        name_of_phases: array of name of m-phases for machine
    """

    def __init__(self, I_hat, linkages, rotor_angle, name_of_phases):
        self.I_hat = I_hat
        self.linkages = linkages 
        self.rotor_angle = rotor_angle
        self.name_of_phases = name_of_phases


class InductanceAnalyzer:
    def __init__(self, clarke_trans_matrix):
        self.clarke_trans_matrix = clarke_trans_matrix

    def analyze(self, problem):
        """Calcuates abc, alpha-beta, and dq inductances

        Args:
            problem: object of type Inductance_Problem holding torque data
        Returns:
            data: dictionary of inductances and rotor angles
        """

        L_abc = [] 
        flux_linkages = [] # make mxm list
        flux_linkages_files = {}
        L_zero = [] 
        flux_linkages_zero = [] # make 1xm list
        flux_linkages_files_zero = {}

        for col in range(len(problem.name_of_phases)+1):
            if col == 0:
                flux_linkages_files_zero[col] = problem.linkages[0]
                flux_linkages_zero.append([])
                L_zero.append([])
                for row in range(len(problem.name_of_phases)):
                    flux_linkages_zero[col].append(row)
                    L_zero[col].append(row)
                    flux_linkages_zero[col][row] = np.array(flux_linkages_files_zero[col]["coil_%s" % problem.name_of_phases[row]])
            else:
                flux_linkages_files[col-1] = problem.linkages[col]
                flux_linkages.append([])
                L_abc.append([])
                for row in range(len(problem.name_of_phases)):
                    flux_linkages[col-1].append(row)
                    L_abc[col-1].append(row)
                    flux_linkages[col-1][row] = np.array(flux_linkages_files[col-1]["coil_%s.%s" % (problem.name_of_phases[row], str(col))])
                    L_abc[col-1][row] = (flux_linkages[col-1][row] - flux_linkages_zero[0][row])/problem.I_hat

        L_abc = np.array(L_abc)

        L_alpha_beta = []
        for i in range(len(L_abc[0][0])):
            L_alpha_beta.append([])
            L_alpha_beta[i] = np.dot(self.clarke_trans_matrix,L_abc[:,:,i])
            L_alpha_beta[i] = np.dot(L_alpha_beta[i],np.linalg.inv(self.clarke_trans_matrix))

        L_alpha_beta = np.array(L_alpha_beta)
        
        L_dq = []
        for i in range(len(L_alpha_beta)):
            L_dq.append([])
            theta = -problem.rotor_angle[0][i]*np.pi/180
            park_trans_matrix = np.array([[np.cos(theta), -np.sin(theta), 0], [np.sin(theta), np.cos(theta), 0], [0, 0, 1]])
            L_dq[i] = np.dot(park_trans_matrix,L_alpha_beta[i,:,:])
            L_dq[i] = np.dot(L_dq[i],np.linalg.inv(park_trans_matrix))

        L_dq = np.array(L_dq)

        data = self.extract_results(problem, L_abc, L_alpha_beta, L_dq) 

        return data
    
    def extract_results(self, problem, L_abc, L_alpha_beta, L_dq):

        data = {
                "rotor_angle": problem.rotor_angle,
                "Labc": L_abc,
                "Lalphabeta": L_alpha_beta,
                "Ldq": L_dq,
            }

        return data