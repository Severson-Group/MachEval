import copy
import numpy as np
import scipy.optimize
import pandas as pd
import matplotlib as mpl
import numpy as np

class Inductance_Problem:
    """Problem class for torque data processing
    Attributes:
        torque: numpy array of torque against time or position
    """

    def __init__(self, I_hat, jmag_csv_folder, study_name, rotor_angle, name_of_phases):
        self.I_hat = I_hat
        self.jmag_csv_folder = jmag_csv_folder 
        self.study_name = study_name
        self.rotor_angle = rotor_angle
        self.name_of_phases = name_of_phases


class Inductance_Analyzer:
    def __init__(self, clarke_trans_matrix):
        self.clarke_trans_matrix = clarke_trans_matrix

    def analyze(self, problem: Inductance_Problem):
        """Calcuates average torque and torque ripple

        Args:
            problem: object of type ProcessTorqueDataProblem holding torque data
        Returns:
            torque_avg: Average torque calculated from provided data
            torque_ripple: Torque ripple calculated from provided data
        """
        path = problem.jmag_csv_folder
        study_name = problem.study_name
        I_hat = problem.I_hat
        name_of_phases = problem.name_of_phases
        rotor_angle = problem.rotor_angle
        L_abc = [] 
        flux_linkages = [] # make mxm list
        flux_linkages_files = {}

        for col in range(len(name_of_phases)):
            flux_linkages_files[col] = pd.read_csv(path + study_name + "_%s_flux_of_fem_coil.csv" % col, skiprows=6)
            flux_linkages.append([])
            L_abc.append([])
            for row in range(len(name_of_phases)):
                flux_linkages[col].append(row)
                L_abc[col].append(row)
                flux_linkages[col][row] = np.array(flux_linkages_files[col]["coil_%s" % name_of_phases[row]])
                L_abc[col][row] = flux_linkages[col][row]/I_hat

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

        data = self.extract_results(problem, L_alpha_beta, L_dq) 

        return data
    
    def extract_results(self, problem, L_alpha_beta, L_dq):


        data = {
                "rotor_angle": problem.rotor_angle,
                "Lalphabeta": L_alpha_beta,
                "Ldq": L_dq,
            }

        return data