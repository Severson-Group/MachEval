import os
import sys

# change current working directory to file location
os.chdir(os.path.dirname(__file__))
# add the directory immediately above this file's directory to path for module import
sys.path.append("../..")

import numpy as np
from matplotlib import pyplot as plt
from typing import Any, List

import mach_opt as mo
import mach_eval as me
import pygmo as pg
from copy import deepcopy


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class Architect(me.Architect):
    """Class converts input tuple x into a machine object"""

    def __init__(self, mat: "Material"):
        self.mat = mat

    def create_new_design(self, x: tuple) -> "me.Machine":
        """
        converts x tuple into a machine object.

        Args:
            x (tuple): Input free variables.
            
        Returns:
            machine (me.Machine): Machine object
        """
        r = x[3]
        delta = x[2]
        machine = Machine(r, delta, self.mat)
        return machine


class Material:
    """Material object for holding material properites"""

    def __init__(self, rho, C_e, C_hy, C_omega):
        self.rho = rho
        self.C_e = C_e
        self.C_hy = C_hy
        self.C_omega = C_omega


class Machine:
    """Class defines a Machine object 
    
    Attributes:
        TODO
    """

    def __init__(self, r, delta, mat):
        """Creates a machine object.

        Args:
            TODO

        """

        self.r = r
        self.delta = delta
        self.mat = mat
        self.L = NotImplementedError

    @property
    def V_r(self):
        return np.pi * self.r ** 2 * self.L

    @property
    def V_s(self):
        return np.pi * ((1.5 * self.r ** 2) - self.r ** 2) * self.L

    def newMachineFromNewLength(self, L) -> "Machine":
        newMachine = deepcopy(self)
        newMachine.L = L
        return newMachine

    def check_required_properites():
        """Checks for required input properties"""
        # TODO
        pass

    def get_missing_properties():
        """Returns missing input properites"""
        # TODO
        pass


class SettingsHandler(me.SettingsHandler):
    def __init__(self, P_rated):
        self.P_rated = P_rated

    def get_settings(self, x):
        B_hat = x[0]
        A_hat = x[1]
        Omega = x[4]
        settings = Settings(B_hat, A_hat, Omega, self.P_rated)
        return settings


class Settings:
    def __init__(self, B_hat, A_hat, Omega, P_rated):
        self.B_hat = B_hat
        self.A_hat = A_hat
        self.Omega = Omega
        self.P_rated = P_rated

    @property
    def f(self):
        return self.Omega / (2 * np.pi)

    @property
    def T(self):
        return self.P_rated / self.Omega


class TipSpeedConstraintEvaluationStep:
    """Constraint evaluation step template"""

    def __init__(self, maxTipSpeed):
        self.maxTipSpeed = maxTipSpeed

    def step(self, stateIn):
        """Checks input state to see if constraint is violated
        
        Raises ConstraintError if violated, otherwise appends values to 
        State conditions and moves forward"""
        r = stateIn.design.machine.r
        omega = stateIn.design.settings.Omega
        v_tip = r * omega
        if v_tip >= self.maxTipSpeed:
            raise mo.InvalidDesign([v_tip, "Tip Speed Violation"])
        else:
            stateOut = deepcopy(stateIn)
            stateOut.conditions.v_tip = v_tip
            return [v_tip, stateOut]


class LengthProblemDefinition(me.ProblemDefinition):
    """Class converts input state into a problem"""

    def get_problem(self, state: "me.State") -> "me.Problem":
        """Returns Problem from Input State"""
        T = state.design.settings.T
        B_hat = state.design.settings.B_hat
        A_hat = state.design.settings.A_hat
        r = state.design.machine.r
        problem = LengthProblem(T, B_hat, A_hat, r)
        return problem


class LengthProblem:
    """problem class utilized by the Analyzer
    
    Attributes:
        TODO
    """

    def __init__(self, T, B_hat, A_hat, r):
        """Creates problem class
        
        Args:
            TODO
            
        """
        # TODO define problem
        self.T = T
        self.B_hat = B_hat
        self.A_hat = A_hat
        self.r = r


class LengthAnalyzer(me.Analyzer):
    """"Calculates the required machine length to produce deisred torque"""

    def analyze(self, problem: "me.Problem"):
        """Performs Analysis on a problem

        Args:
            problem (me.Problem): Problem Object

        Returns:
            results (Any): 
                Results of Analysis

        """
        # TODO Define Analyzer
        T = problem.T
        B_hat = problem.B_hat
        A_hat = problem.A_hat
        r = problem.r
        L = T / (B_hat * A_hat * np.pi * r ** 2)
        return L


class LengthPostAnalyzer(me.PostAnalyzer):
    """Converts input state into output state for TemplateAnalyzer"""

    def get_next_state(self, results, stateIn: "me.State") -> "me.State":
        stateOut = deepcopy(stateIn)
        newMachine = stateOut.design.machine.newMachineFromNewLength(results)
        stateOut.design.machine = newMachine
        # TODO define Post-Analyzer
        return stateOut


class L2rConstraintEvaluationStep:
    """Constraint evaluation step template"""

    def __init__(self, maxL2r):
        self.maxL2r = maxL2r

    def step(self, stateIn):
        """Checks input state to see if constraint is violated
        
        Raises ConstraintError if violated, otherwise appends values to 
        State conditions and moves forward"""
        r = stateIn.design.machine.r
        L = stateIn.design.machine.L
        L2r = L / r  # TODO define constraint
        if L2r >= self.maxL2r:
            raise mo.InvalidDesign([L2r, "Length to radius Ratio"])
        else:
            stateOut = deepcopy(stateIn)
            stateOut.conditions.L2r = L2r
            return [L2r, stateOut]


class LossProblemDefinition(me.ProblemDefinition):
    """Class converts input state into a problem"""

    def get_problem(self, state: "me.State") -> "me.Problem":
        """Returns Problem from Input State"""
        # TODO define problem definition
        rho = state.design.machine.mat.rho
        V_s = state.design.machine.V_s
        C_e = state.design.machine.mat.C_e
        f = state.design.settings.f
        B_hat = state.design.settings.B_hat
        C_hy = state.design.machine.mat.C_hy
        C_omega = state.design.machine.mat.C_omega
        A_hat = state.design.settings.A_hat
        problem = LossProblem(rho, V_s, C_e, f, B_hat, C_hy, C_omega, A_hat)
        return problem


class LossProblem:
    """problem class utilized by the Analyzer
    
    Attributes:
        TODO
    """

    def __init__(self, rho, V_s, C_e, f, B_hat, C_hy, C_omega, A_hat):
        """Creates problem class
        
        Args:
            TODO
            
        """
        self.rho = rho
        self.V_s = V_s
        self.C_e = C_e
        self.f = f
        self.B_hat = B_hat
        self.C_hy = C_hy
        self.C_omega = C_omega
        self.A_hat = A_hat


class LossAnalyzer(me.Analyzer):
    """"Class Analyzes the CubiodProblem  for volume and Surface Areas"""

    def analyze(self, problem: "me.Problem"):
        """Performs Analysis on a problem

        Args:
            problem (me.Problem): Problem Object

        Returns:
            results (Any): 
                Results of Analysis

        """
        rho = problem.rho
        V_s = problem.V_s
        C_e = problem.C_e
        f = problem.f
        B_hat = problem.B_hat
        C_hy = problem.C_hy
        C_omega = problem.C_omega
        A_hat = problem.A_hat
        P_loss = (
            rho * V_s * (C_e * (f ** 2) * (B_hat * 2) + C_hy * f * (B_hat ** 2))
            + C_omega * V_s * A_hat ** 2
        )
        return P_loss


class LossPostAnalyzer(me.PostAnalyzer):
    """Converts input state into output state for TemplateAnalyzer"""

    def get_next_state(self, results: Any, stateIn: "me.State") -> "me.State":
        stateOut = deepcopy(stateIn)
        stateOut.conditions.P_loss = results
        return stateOut


class CostProblemDefinition(me.ProblemDefinition):
    """Class converts input state into a problem"""

    def get_problem(self, state: "me.State") -> "me.Problem":
        """Returns Problem from Input State"""
        # TODO define problem definition
        delta = state.design.machine.delta
        V_s = state.design.machine.V_s
        V_r = state.design.machine.V_r
        problem = CostProblem(delta, V_s, V_r)
        return problem


class CostProblem:
    """problem class utilized by the Analyzer
    
    Attributes:
        TODO
    """

    def __init__(self, delta, V_s, V_r):
        """Creates problem class
        
        Args:
            TODO
            
        """
        self.delta = delta
        self.V_s = V_s
        self.V_r = V_r


class CostAnalyzer(me.Analyzer):
    """"Class Analyzes the CubiodProblem  for volume and Surface Areas"""

    def analyze(self, problem: "me.Problem"):
        """Performs Analysis on a problem

        Args:
            problem (me.Problem): Problem Object

        Returns:
            results (Any): 
                Results of Analysis

        """
        delta = problem.delta
        V_s = problem.V_s
        V_r = problem.V_r
        P_r = 1000 * (9.85 + 5000 * delta)
        P_s = 6750
        C_s = P_s * V_s
        C_r = P_r * V_r
        C = C_s + C_r
        results = [C, C_s, C_r]
        return results


class CostPostAnalyzer(me.PostAnalyzer):
    """Converts input state into output state for TemplateAnalyzer"""

    def get_next_state(self, results: Any, stateIn: "me.State") -> "me.State":
        stateOut = deepcopy(stateIn)
        stateOut.conditions.C = results[0]
        stateOut.conditions.C_s = results[1]
        stateOut.conditions.C_r = results[2]
        return stateOut


class TorqueRippleProblemDefinition(me.ProblemDefinition):
    """Class converts input state into a problem"""

    def get_problem(self, state: "me.State") -> "me.Problem":
        """Returns Problem from Input State"""
        # TODO define problem definition
        r = state.design.machine.r
        delta = state.design.machine.delta
        problem = TorqueRippleProblem(r, delta)
        return problem


class TorqueRippleProblem:
    """problem class utilized by the Analyzer
    
    Attributes:
        TODO
    """

    def __init__(self, r, delta):
        """Creates problem class
        
        Args:
            TODO
            
        """
        self.r = r
        self.delta = delta


class TorqueRippleAnalyzer(me.Analyzer):
    """"Class Analyzes the CubiodProblem  for volume and Surface Areas"""

    def analyze(self, problem: "me.Problem"):
        """Performs Analysis on a problem

        Args:
            problem (me.Problem): Problem Object

        Returns:
            results (Any): 
                Results of Analysis

        """
        r = problem.r
        delta = problem.delta
        T_r = (1 / (20 * (r * delta) ** 0.25)) + 0.25 * np.sin(4000 * np.pi * delta)
        return T_r


class TorqueRipplePostAnalyzer(me.PostAnalyzer):
    """Converts input state into output state for TemplateAnalyzer"""

    def get_next_state(self, results: Any, stateIn: "me.State") -> "me.State":
        stateOut = deepcopy(stateIn)
        stateOut.conditions.T_r = results
        return stateOut


class ConstraintError(Error):
    """Error for violating optimization constraint"""

    def __init__(self, value, message):
        # TODO define error
        self.value = value
        self.message = message


class DesignSpace:
    """Design space of optimization"""

    def __init__(self, n_obj, bounds):
        self._n_obj = n_obj
        self._bounds = bounds

    def check_constraints(self, full_results) -> bool:
        return True

    @property
    def n_obj(self) -> int:
        return self._n_obj

    def get_objectives(self, full_results) -> tuple:
        """ Calculates objectives from evaluation results
        

        Args:
            full_results (List): Results from MachineEvaluator

        Returns:
            Tuple: objectives tuple 
        """
        final_state = full_results[-1][-1]
        P_loss = final_state.conditions.P_loss
        C = final_state.conditions.C
        T_r = final_state.conditions.T_r
        P_rated = final_state.design.settings.P_rated

        Eff = (P_rated - P_loss) / P_rated
        results = (-Eff, C, T_r)  # TODO define objectives
        return results

    @property
    def bounds(self) -> tuple:
        return self._bounds


class DataHandler:
    """Parent class for all data handlers"""

    def save_to_archive(self, x, design, full_results, objs):
        pass

    def save_designer(self, designer):
        pass


if __name__ == "__main__":

    # Create Designer
    settingsHandler = SettingsHandler(100e3)  # TODO define settings
    material = Material(7850, 6.88e-5, 0.0186, 0.002)
    arch = Architect(material)
    des = me.MachineDesigner(arch, settingsHandler)

    # Create evaluation steps
    v_tip_max = 150
    maxL2r = 10
    evalSteps = [
        TipSpeedConstraintEvaluationStep(v_tip_max),
        me.AnalysisStep(
            LengthProblemDefinition(), LengthAnalyzer(), LengthPostAnalyzer()
        ),
        L2rConstraintEvaluationStep(maxL2r),
        me.AnalysisStep(LossProblemDefinition(), LossAnalyzer(), LossPostAnalyzer()),
        me.AnalysisStep(CostProblemDefinition(), CostAnalyzer(), CostPostAnalyzer()),
        me.AnalysisStep(
            TorqueRippleProblemDefinition(),
            TorqueRippleAnalyzer(),
            TorqueRipplePostAnalyzer(),
        ),
    ]

    # Create Evaluator
    evaluator = me.MachineEvaluator(evalSteps)
    dh = DataHandler()

    # set evaluation bounds
    bounds = (
        [0.1, 10e3, 0.1e-3, 10e-3, 1000 * 2 * np.pi / 60],
        [1, 100e3, 10e-3, 95.5e-3, 15000 * 2 * np.pi / 60],
    )

    # set number of objectives
    n_obj = 3

    # Create Machine Design Problem
    ds = DesignSpace(n_obj, bounds)
    machDesProb = mo.DesignProblem(des, evaluator, ds, dh)

    # Run Optimization
    opt = mo.DesignOptimizationMOEAD(machDesProb)
    pop_size = 496
    gen_size = 10
    pop = opt.initial_pop(pop_size)
    pop = opt.run_optimization(pop, gen_size)
    fits, vectors = pop.get_f(), pop.get_x()
    ndf, dl, dc, ndr = pg.fast_non_dominated_sorting(fits)

    fig1 = plt.figure()
    ax1 = fig1.add_subplot()
    im1 = ax1.scatter(fits[ndf[0], 0], fits[ndf[0], 1], c=fits[ndf[0], 2], marker="x")
    ax1.set_xlabel("-Efficiency")
    ax1.set_ylabel("Cost [$]")
    ax1.set_title("Pareto Front")
    cb1 = fig1.colorbar(im1, ax=ax1,)
    cb1.set_label("Torque Ripple [ ]")

    fig2 = plt.figure()
    ax2 = fig2.add_subplot()
    im2 = ax2.scatter(fits[ndf[0], 1], fits[ndf[0], 2], c=fits[ndf[0], 0], marker="x")
    ax2.set_xlabel("Cost [$]")
    ax2.set_ylabel("Torque Ripple [ ]")
    ax2.set_title("Pareto Front")
    cb2 = fig2.colorbar(im2, ax=ax2,)
    cb2.set_label("-Efficiency")

    fig3 = plt.figure()
    ax3 = fig3.add_subplot()
    im3 = ax3.scatter(fits[ndf[0], 2], fits[ndf[0], 0], c=fits[ndf[0], 1], marker="x")
    ax3.set_xlabel("Torque Ripple [ ]")
    ax3.set_ylabel("-Efficiency")
    ax3.set_title("Pareto Front")
    cb3 = fig3.colorbar(im3, ax=ax3,)
    cb3.set_label("Cost [$]")

