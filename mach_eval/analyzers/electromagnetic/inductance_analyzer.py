import copy
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
import pandas as pd

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
        L = {}

        for i in range(len(name_of_phases)):
            flux_linkages = pd.read_csv(path + study_name + "_%s_flux_of_fem_coil.csv" % i, skiprows=7)
            #flux_linkages = flux_linkages.to_numpy()
            L[i] = flux_linkages/I_hat
            
        L = np.stack(L.values())
        L = L[:, :, 1:]
        L_abc = np.sum(L,axis = 2)

        L_alpha_beta = {}
        for i in range(len(L_abc[0])):
            L_alpha_beta[i] = np.dot(self.clarke_trans_matrix,L_abc[:,i].reshape(len(name_of_phases),1))
        
        L_dq = {}
        for i in range(len(L_alpha_beta)):
            L_dq[i] = np.dot(np.array([[np.cos(problem.rotor_angle[i]), np.sin(problem.rotor_angle[i]), 0], [-np.sin(problem.rotor_angle[i]), np.cos(problem.rotor_angle[i]), 0], [0, 0, 1]]),L_alpha_beta[i])

        data = self.extract_results(L_alpha_beta, L_dq) 

        return data
    
    def extract_results(self, L_alpha_beta, L_dq):

        L_alpha = {}
        L_beta = {}
        L_gamma = {}
        for i in range(len(L_alpha_beta)):
            L_alpha[i] = float(L_alpha_beta[i][0])
            L_beta[i] = float(L_alpha_beta[i][1])
            L_gamma[i] = float(L_alpha_beta[i][2])

        L_d = {}
        L_q = {}
        L_zero = {}
        for i in range(len(L_dq)):
            L_d[i] = float(L_dq[i][0])
            L_q[i] = float(L_dq[i][1])
            L_zero[i] = float(L_dq[i][2])

        data = {
                "Lalpha": L_alpha,
                "Lbeta": L_beta,
                "Lgamma": L_gamma,
                "Ld": L_d,
                "Lq": L_q,
                "Lzero": L_zero,
            }

        return data