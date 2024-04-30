import numpy as np
import sys
import os
sys.path.append(os.path.dirname(__file__))

from rotor_structural import SPM_RotorStructuralProblem, SPM_RotorStructuralAnalyzer

class SPM_RotorSpeedLimitProblem:
    def __init__(
        self,
        r_sh: float,
        d_m: float,
        r_ro: float,
        d_sl: float,
        delta_sl: float,
        deltaT: float,
        N_max: float,
        mat_dict: dict,
        mat_failure_dict: dict,
        ) -> "SPM_RotorSpeedLimitProblem":

        """Creates SPM_RotorSpeedLimitAnalyzer object from input

        Args:
            r_sh (float): Shaft outer radius [m].
            d_m (float): Magnet Thickness [m].
            r_ro (float): Outer Rotor Radius [m].
            d_sl (float): Sleeve Thickness [m].
            delta_sl (float): Sleeve Undersize [m].
            deltaT (float): Temperature Rise [K].
            N_max (float): Maximum RPM to evaluate [RPM].
            mat_dict (dict): material dictionary 
            mat_failure_dict (dict): material yield strength dictionary

        Returns:
            problem (RotorSpeedLimitProblem): RotorSpeedLimitProblem
        """

        self.r_sh = r_sh
        self.d_m = d_m 
        self.r_ro = r_ro
        self.d_sl = d_sl
        self.delta_sl = delta_sl
        self.deltaT = deltaT
        self.N_max = N_max
        self.mat_dict = mat_dict
        self.mat_failure_dict = mat_failure_dict


class SPM_RotorSpeedLimitAnalyzer:
    def __init__(
            self, 
            N_step: float,
            node: int
            ) -> "SPM_RotorSpeedLimitAnalyzer":
        
        """Analyzer Class for SPM_RotorSpeedLimitProblem
        
        Args:
            N_step (float): RPM evaluation step size [RPM].
            node (int): number of nodes to evaluate 
        """
        
        self.N_step = N_step
        self.node = node


    def analyze(self, problem: "SPM_RotorSpeedLimitProblem"):
        """Analyze rotor to determine failure material and rotational speed

        Args:
            problem (PM_RotorSpeedLimitProblem): problem for analyzer.

        Returns:
            results (): 
        """
        self.r_sh = problem.r_sh
        self.d_m = problem.d_m
        self.r_ro = problem.r_ro
        self.d_sl = problem.d_sl
        self.delta_sl = problem.delta_sl
        self.deltaT = problem.deltaT
        self.mat_dict = problem.mat_dict
        self.N_max = problem.N_max

        # Failure Condition 
        mat_failure_dict = problem.mat_failure_dict
        self.mat_fail_cond = np.array([
            mat_failure_dict["shaft_yield_strength"],
            mat_failure_dict["core_yield_strength"],
            mat_failure_dict["magnet_ultimate_strength"],
            mat_failure_dict["sleeve_ultimate_strength"],
            mat_failure_dict["adhesive_ultimate_strength"]])

        # Overall radius of the rotor
        r_rotor = self.r_ro + self.d_sl - self.delta_sl

        # Vector of radius for materials   
        r_vect_sh=np.linspace(
            self.r_sh/10000, 
            self.r_sh,
            round((self.r_sh/r_rotor)*self.node))
        
        r_vect_rc=np.linspace(
            self.r_sh, 
            self.r_ro-self.d_m,
            round(((self.r_ro-self.d_m-self.r_sh)/r_rotor)*self.node))
        
        r_vect_pm=np.linspace(
            self.r_ro-self.d_m, 
            self.r_ro,
            round((self.d_m/r_rotor)*self.node))
        
        r_vect_sl=np.linspace(
            self.r_ro, 
            self.r_ro+self.d_sl,
            round((self.d_sl/r_rotor)*self.node))
        
        r_vect_ah = np.array([self.r_ro-self.d_m])

        self.r_vect = np.array([
            r_vect_sh,
            r_vect_rc,
            r_vect_pm,
            r_vect_sl,
            r_vect_ah], dtype=object)

        # Create speed array
        N = np.arange(0,self.N_max,self.N_step) 

        for speed in N:            
            # Check if failure is found and determine failure material
            (fail, failure_mat) = self.check_if_fail(speed)      

            # If failure is found, break for loop
            if fail:
                break

        if failure_mat is None:
            # if no failure is found, return "None" for both 
            # failure material and speed
            return SPM_RotorSpeedLimitResults(None, None)
        else:
            # if failure is found, return result class with 
            # failure material and speed
            return SPM_RotorSpeedLimitResults(failure_mat, speed)
        
    def check_if_fail(self, speed):
        """ Check if rotor material failure occured for a given rotational speed

        Args:
            speed (float): rotational speed of rotor 

        Returns:
            results (tuple): Tuple(True, failure_mat) 
            results (tuple): Tuple(False, None)
        """

        # Material Array
        # ( Must follow this specific order )
        materials = np.array(
            ["Shaft",
            "Core",
            "Magnet",
            "Sleeve",
            "Adhesive"])
        
        # Create rotor structral problem
        st_problem = SPM_RotorStructuralProblem(
            self.r_sh, 
            self.d_m, 
            self.r_ro, 
            self.d_sl, 
            self.delta_sl, 
            self.deltaT, 
            speed, 
            self.mat_dict)

        # Initialize analyzers
        st_analyzer = SPM_RotorStructuralAnalyzer()

        # Analyze rotor structual problem
        st_sigmas = st_analyzer.analyze(st_problem)

        sigma_max = np.zeros(len(materials))
        failure_mat = None

        # Determine maxmium Von Mises Stress for all rotor materials
        for idx,mat in enumerate(materials):
            # Skip the adhesive since it has a special case
            if mat == "Adhesive":
                continue

            # Skip the sleeve calculation if not present
            if mat == "Sleeve" and self.r_vect[idx].size == 0:
                continue
            
            # Determine tangential and radial stress
            sigma_t = st_sigmas[idx].tangential(self.r_vect[idx])
            sigma_r = st_sigmas[idx].radial(self.r_vect[idx])
            
            # Create static stress problem 
            ss_problem = SteadyStateStressProblem(sigma_t,sigma_r)

            # Analyze static stress problem
            ss_analyzer = SteadyStateStressAnalyzer()
            ss_stress = ss_analyzer.analyze(ss_problem)

            if mat in ["Shaft", "Core"]:
                # Use Von Mises Stress for ductile materials
                # [0] index provides Von Mises Stress
                sigma_max[idx] = np.max(ss_stress[0])
            else:
                # Use MSST Stress for brittle material
                # [1] index provides MSST Stress (yield)
                sigma_max[idx] = np.max(ss_stress[1])

        # Determine adhesive MSST Stress
        # (assumed to be at the interface between core and magnet with zero thickness)
        # (self.r_vect[4] is the radial location of the adhesive)
        core_idx = np.where(materials == "Core")[0][0]

        ss_problem = SteadyStateStressProblem(
            st_sigmas[core_idx].tangential(self.r_vect[4]),
            st_sigmas[core_idx].radial(self.r_vect[4]))
        
        ss_stress = ss_analyzer.analyze(ss_problem)
        sigma_max[-1] = np.min(ss_stress[1])

        # Determine percenatge to failure for all materials
        pct_to_fail = sigma_max/self.mat_fail_cond

        # Check maximum stress against failure condition to determine failure material
        for idx, pct in enumerate(pct_to_fail):
            
            # Failure when pct is @ 100%
            pct_max = 1.0
            if pct >= pct_max:
                failure_mat = materials[idx]
                return (True,failure_mat)
        
        # return False and None if no failure is found
        return (False, None)
        
class SteadyStateStressProblem:
    def __init__(
            self,
            sigma_x,
            sigma_y,
            sigma_z = 0) -> "SteadyStateStressProblem":
        """Problem class for SPM_RotorSpeedLimitAnalyzer
    
        Attributes:
            sigma_x (np.array): Tangential Stress Vector [Pa]
            sigma_y (np.array): Radial Stress Vector [Pa]
            sigma_z (float): Axial Stress (Constant) [Pa]

        Returns:
            problem (SteadyStateStressProblem): SteadyStateStressProblem
        """

        self.sigma_x = sigma_x
        self.sigma_y = sigma_y

        # Create np.array with same size as sigma_x and sigma_y, filled with sigma_z value.
        # Default sigma_z value = 0 [Pa]
        self.sigma_z = np.full(len(sigma_x),sigma_z)

        # Stack nominal stress arrays
        self.sigma_normal = np.stack((
            self.sigma_x, 
            self.sigma_y, 
            self.sigma_z),
            axis=1)
        
class SteadyStateStressAnalyzer:
    """Analyzer class for SteadyStateStressProblem"""
    def __init__(self):
        pass

    def analyze(self, problem: "SteadyStateStressProblem"):
        """Analyze method for SPM_RotorSpeedLimitAnalyzer
    
        Attributes:
            problem (SteadyStateStressProblem): SteadyStateStressProblem

        Returns:
            criterial_stress (np.array): [von_mises_stress,tresca_stress]
        """
        
        sigma_normal = problem.sigma_normal

        # Create Mohrs Circle to compute principle stresses
        self.mohrs_stress = self.create_mohrs_circle(sigma_normal)

        # Compute Von Mises and Tresca Stress

        criterial_stress = np.array([self.von_mises_stress,self.MSST_stress])
        return criterial_stress

    @property
    def von_mises_stress(self):
        """ Determine Von Mises Equivalent Stress.

        Attributes:
            mohrs_stress (np.array): Principle Stresses [sigma_1,sigma_2,sigma_3,tau_max]

        Returns:
            sigma_e (float): Von Mises Equivalent Stress.
        """
        sigma_1 = self.mohrs_stress[0]
        sigma_2 = self.mohrs_stress[1]
        sigma_3 = self.mohrs_stress[2]

        # Compute Von Mises Equivalent Stress 
        sigma_e = np.sqrt(2)/2*np.sqrt(
            (sigma_2-sigma_1)**2+(sigma_3-sigma_1)**2+(sigma_3-sigma_2)**2)
        
        return sigma_e

    @property
    def MSST_stress(self):
        """ Determine Stress (yield) based on MSST criterion.

        Attributes:
            mohrs_stress (np.array): Principle Stresses [sigma_1,sigma_2,sigma_3,tau_max]

        Returns:
            sigma_1-sigma_3 (float): MSST Stress (yield).
        """
        # Compute Tresca/MSST stress (yield)
        sigma_1 = self.mohrs_stress[0]
        sigma_3 = self.mohrs_stress[2]
        return sigma_1-sigma_3

    def create_mohrs_circle(self,sigma_normal):
        """ Determine Principle Stresses (sigma_1, sigma_2, sigma_3) 
        and Maximum Shear Stress (tau_maximum) using 3D Mohr's Circle Method.
        ( Applied shear stress terms are omitted in calculation )

        Attributes:
            sigma_normal (np.array): nominal stress arrays
        
        Returns:
            mohrs_result (np.array): numpy array of mohrs cicrle principle 
            stresses and maxmimum shear stress.
        """
    
        # Sort arrays for determining principle stresses
        sigma_normal_s = np.sort(sigma_normal)

        # Split arrays into three arrays
        sigma_principle = [np.array(x) for x in zip(*sigma_normal_s)] 

        # Obtain Principle Stresses
        sigma_1 = sigma_principle[2]
        sigma_2 = sigma_principle[1]
        sigma_3 = sigma_principle[0]

        # Copmute Maximum Shear Stress
        tau_max = (sigma_1-sigma_3)/2

        mohrs_stress = np.array([sigma_1,sigma_2,sigma_3,tau_max])
        return mohrs_stress
        

class SPM_RotorSpeedLimitResults:
    def __init__(
            self, 
            failure_mat: str,
            speed: float
            ):
        """Results class for SPM_RotorSpeedLimitAnalyzer
    
        Attributes:
            failure_mat (str): material where failure occurs
            speed (float): speed where failure occurs [RPM]

        Returns:
            result (SPM_RotorSpeedLimitResults): SPM_RotorSpeedLimitResults
        """
        self.failure_mat = failure_mat
        self.speed = speed
