import numpy as np
import pandas as pd
import numpy as np

class Inductance_Problem:
    """Problem class for inductance data processing
    Attributes:
        I_hat: 
        csv_folder: 
        study_name: 
        rotor_angle: 
        name_of_phases: 
    """

    def __init__(self, I_hat, csv_folder, study_name, rotor_angle, name_of_phases):
        self.I_hat = I_hat
        self.csv_folder = csv_folder 
        self.study_name = study_name
        self.rotor_angle = rotor_angle
        self.name_of_phases = name_of_phases


class Inductance_Analyzer:
    def __init__(self, clarke_trans_matrix):
        self.clarke_trans_matrix = clarke_trans_matrix

    def analyze(self, problem):
        """Calcuates abc, alpha-beta, and dq inductances

        Args:
            problem: object of type Inductance_Problem holding torque data
        Returns:
            data: dictionary of inductances and rotor angles
        """
        path = problem.csv_folder
        study_name = problem.study_name
        I_hat = problem.I_hat
        name_of_phases = problem.name_of_phases
        rotor_angle = problem.rotor_angle
        L_abc = [] 
        flux_linkages = [] # make mxm list
        flux_linkages_files = {}
        L_zero = [] 
        flux_linkages_zero = [] # make 1xm list
        flux_linkages_files_zero = {}

        for col in range(len(name_of_phases)):
            flux_linkages_files_zero[col] = pd.read_csv(path + study_name + "_flux_of_fem_coil_0.csv", skiprows=6)
            flux_linkages_zero.append([])
            L_zero.append([])
            for row in range(len(name_of_phases)):
                flux_linkages_zero[col].append(row)
                L_zero[col].append(row)
                flux_linkages_zero[col][row] = np.array(flux_linkages_files_zero[col]["coil_%s" % name_of_phases[row]])

        for col in range(len(name_of_phases)):
            flux_linkages_files[col] = pd.read_csv(path + study_name + "_flux_of_fem_coil_phase_%s.csv" % name_of_phases[col], skiprows=6)
            flux_linkages.append([])
            L_abc.append([])
            for row in range(len(name_of_phases)):
                flux_linkages[col].append(row)
                L_abc[col].append(row)
                flux_linkages[col][row] = np.array(flux_linkages_files[col]["coil_%s" % name_of_phases[row]])
                L_abc[col][row] = (flux_linkages[col][row] - flux_linkages_zero[col][row])/I_hat

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
            theta = -rotor_angle[0][i]*np.pi/180
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