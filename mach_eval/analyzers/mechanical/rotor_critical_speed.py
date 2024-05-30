import numpy as np
from functools import cached_property

class RotorCritcalSpeedProblem:
    """Problem class for RotorCritcalSpeedProblem"""

    def __init__(
            self, 
            r_sh:float,
            L:float,
            beta_l:float,
            material:dict,
            ) -> 'RotorCritcalSpeedProblem':
        
        """Creates RotorCritcalSpeedProblem object from input

        Args:
            r_sh (float): shaft radius, in unit [m]
            L (float): shaft length, in unit [m] 
            beta_l (float): boundary condition numerical constant
            material (dict): material dictionary

        Notes:

        * `material` dictionary must contain the following key-value pairs

            youngs_modulus (float): Young's Modulus of the shaft material
            density (float): density of the shaft material

        Returns:
            RotorCritcalSpeedProblem: RotorCritcalSpeedProblem
        """
        self.r_sh = r_sh
        self.L = L
        self.beta_l = beta_l
        self.material = material

    @cached_property
    def I_sh(self):
        """Area moment of inertia of shaft"""
        return (1/4)*np.pi*self.r_sh**4
    
    @cached_property
    def A_sh(self):
        """Cross-sectional area of shaft"""
        return np.pi*self.r_sh**2


class RotorCritcalSpeedAnalyzer:
    """Analyzer class for RotorCritcalSpeedProblem"""

    def __init__(
            self,
            problem: RotorCritcalSpeedProblem
            ) -> 'RotorCritcalSpeedAnalyzer':
        """Creates RotorCritcalSpeedAnalyzer object from input

        Args:
            problem (RotorCritcalSpeedProblem): Problem class

        Returns:
            RotorCritcalSpeedAnalyzer: RotorCritcalSpeedAnalyzer
        """

        self.problem = problem
        self.material = problem.material

    def solve(self):
        return RotorCritcalSpeedResult(self.omega_n)
        
    @property
    def omega_n(self):
        """Estimated critical speed [rad/s]"""
        return self.problem.beta_l**2*np.sqrt(
            self.material['youngs_modulus']*self.problem.I_sh/
            (self.material['density']*self.problem.A_sh*self.problem.L**4))
    
class RotorCritcalSpeedResult:
    """Result class for RotorCritcalSpeedAnalyzer"""
    def __init__(
            self,
            omega_n
            ) -> 'RotorCritcalSpeedResult':
        """Result class for RotorCritcalSpeedAnalyzer

        Attr:
            omega_n (float): rotor first bending mode crtical speed [rad/s]

        Returns:
            result (RotorCritcalSpeedResult): RotorCritcalSpeedResult
        """
        self.omega_n = omega_n


if __name__ == "__main__":
    mat_dict = {
        'youngs_modulus':206E9, #Pa
        'density':7870, # kg/m3
        }
    problem = RotorCritcalSpeedProblem(9E-3,164E-3,4.7,mat_dict)
    analyzer = RotorCritcalSpeedAnalyzer(problem)
    result = analyzer.solve()
    print(result.omega_n)