"""Module holding classes required for design optimization.

This module holds the classes required for optimizing a design using pygmo in MachEval.
"""

import pygmo as pg
import pandas as pd
from typing import Protocol, runtime_checkable, Any
from abc import abstractmethod, ABC
import numpy as np
import pickle
import time
import sys
import pathlib
import multiprocessing as mp

__all__ = [
    "DesignOptimizationMOEAD",
    "DesignProblem",
    "Designer",
    "Design",
    "Evaluator",
    "DesignSpace",
    "DataHandler",
    "OptiData",
    "InvalidDesign",
]


class DesignOptimizationMOEAD:
    def __init__(self, design_problem):
        self.design_problem = design_problem
        self.prob = pg.problem(self.design_problem)

    def initial_pop(self, pop_size):
        pop = pg.population(self.prob, size=pop_size)
        return pop

    def run_optimization(
        self,
        pop,
        gen_size,
        pop_filepath: pathlib.Path,
        pop_fitness_filepath: pathlib.Path,
        pg_neighbors=20,
    ):
        algo = pg.algorithm(
            pg.moead(
                gen=1,
                weight_generation="grid",
                decomposition="tchebycheff",
                neighbours=pg_neighbors,
                CR=1,
                F=0.5,
                eta_m=20,
                realb=0.9,
                limit=2,
                preserve_diversity=True,
            )
        )

        for _ in range(0, gen_size):
            print("This is iteration", _)

            # Evolve population
            pop = algo.evolve(pop)

            # Save state
            print("Saving current generation")
            self.save_pop(pop_filepath, pop)
            self.save_pop_fitness(pop_fitness_filepath, pop)

        return pop

    def save_pop(self, filepath, pop):
        df = pd.DataFrame(pop.get_x())
        df.to_csv(filepath)

    def save_pop_fitness(self, filepath, pop):
        df = pd.DataFrame(pop.get_f())
        df.to_csv(filepath)

    def load_pop(
        self,
        pop_filepath: pathlib.Path,
        pop_fitness_filepath: pathlib.Path,
        pop_size: int,
        print_to_console=False,
    ):
        try:
            df_x = pd.read_csv(pop_filepath, index_col=0)
        except FileNotFoundError:
            return None

        try:
            df_fit = pd.read_csv(pop_fitness_filepath, index_col=0)
        except FileNotFoundError:
            print("NO FITNESS VALUES FOUND FOR POPULATION...")
            print("NOW COMPUTING FITNESS DURING POPULATION LOAD...")
            df_fit = None

        pop = pg.population(self.prob)

        for i in range(pop_size):
            x = df_x.iloc[i]

            if print_to_console:
                print(x)

            if df_fit is not None:
                f = df_fit.iloc[i]
                pop.push_back(x, f=f)
            else:
                pop.push_back(x)

        return pop


class DesignProblem:
    """Class to create, evaluate, and optimize designs

    Attributes:
        designer: Objects which convert free variables to a design.

        evaluator: Objects which evaluate the performance of different designs.

        design_space: Objects which characterizes the design space of the optimization.

        dh: Data handlers which enable saving optimization results and its resumption.

        invalid_design_objs: List of (large) objective values to use for invalid designs
    """

    def __init__(
        self,
        designer: "Designer",
        evaluator: "Evaluator",
        design_space: "DesignSpace",
        dh: "DataHandler",
        invalid_design_objs=None,
        crash_safe_evaluation=False,
    ):
        self.__designer = designer
        self.__evaluator = evaluator
        self.__design_space = design_space
        self.__dh = dh
        self.__crash_safe_evaluation = crash_safe_evaluation

        if invalid_design_objs is None:
            self.__invalid_design_objs = 1e4 * np.ones([1, self.get_nobj()])
        else:
            if len(invalid_design_objs) != self.get_nobj():
                raise Exception("Incorrect length for invalid_design_objs")
            self.__invalid_design_objs = invalid_design_objs

        dh.save_designer(designer)

    @staticmethod
    def evaluate_design_func(evaluator, design, queue: mp.Queue):
        try:
            # Run the evaluator (this is slow and might crash!)
            full_results = evaluator.evaluate(design)
        except InvalidDesign:
            # Tell caller this design is invalid with code 1
            sys.exit(1)
        except Exception:
            # Some other failure... tell caller with code 2
            sys.exit(2)

        # Tell parent we are done
        queue.put(True)

        # Give the result to the caller process
        queue.put(full_results)

        # Code of 0 means this eval was a success
        sys.exit(0)

    def fitness(self, x: "tuple") -> "tuple":
        """Calculates the fitness or objectives of each design based on evaluation results.

        This function creates, evaluates, and calculates the fitness of each design generated by the optimization
        algorithm. It also saves the results and handles invalid designs.

        Args:
            x: The list of free variables required to create a complete design

        Returns:
            objs: Returns the fitness of each design

        Raises:
            e: The errors encountered during design creation or evaluation apart from the InvalidDesign error
        """
        try:
            design = self.__designer.create_design(x)

            ###############################################
            # Evaluate the design
            ###############################################

            if not self.__crash_safe_evaluation:
                full_results = self.__evaluator.evaluate(design)
            else:
                # Make a new process to evaluate the design
                queue = mp.Queue()
                p = mp.Process(
                    target=self.evaluate_design_func,
                    args=(
                        self.__evaluator,
                        design,
                        queue,
                    ),
                )
                p.start()

                # Wait for evalulation to complete, or it to crash
                is_done = False
                while not is_done:
                    if queue.empty():
                        time.sleep(0.1)

                        if p.exitcode is not None:
                            # Child process (evaluation) is done
                            if p.exitcode != 0:
                                if p.exitcode not in [1, 2]:
                                    # Unknown error during design evaluation
                                    # (NOT InvalidDesign or Exception)
                                    # Breakpoint here can catch JMAG crash
                                    pass

                                # It was not successful
                                raise InvalidDesign("Bad design (code %d)" % p.exitcode)
                    else:
                        is_done = queue.get()

                # We know the child process will put the results
                # into the queue right NOW, so pull them out to
                # trigger the queue's buffer to flush......see:
                # https://stackoverflow.com/questions/26025486/#comment40796894_26041762
                full_results = queue.get()

                # The process should be done by now,
                # but make sure by joining it here
                p.join()

            # Apply transform to full_results (if needed)
            if self.__dh.full_results_transform is not None:
                full_results = self.__dh.full_results_transform(full_results)

            objs = self.__design_space.get_objectives(full_results)
            self.__dh.save_to_archive(x, design, full_results, objs)
            # print('The fitness values are', objs)
            return objs

        except Exception as e:
            # Check if e is an InvalidDesign exception using the class name
            # This is done to catch InvalidDesign exceptions regardless of what module they orginate from (mach_opt.mach_opt.InvalidDesign OR eMachPrivate.eMach.mach_opt.mach_opt.InvalidDesign)
            if (e.__class__.__name__ == InvalidDesign().__class__.__name__): 
                temp = tuple(map(tuple, self.__invalid_design_objs))
                objs = temp[0]
                return objs

            ################ Uncomment below block of code to prevent one off errors from JMAG ###################
            elif type(e) is FileNotFoundError:
                print('**********ERROR*************')
                temp = tuple(map(tuple, self.__invalid_design_objs))
                objs = temp[0]
                return objs
            else:
                raise e

    def get_bounds(self):
        """Returns bounds for optimization problem"""
        return self.__design_space.bounds

    def get_nobj(self):
        """Returns number of objectives of optimization problem"""
        return self.__design_space.n_obj


@runtime_checkable
class Designer(Protocol):
    """Parent class for all designers"""

    @abstractmethod
    def create_design(self, x: "tuple") -> "Design":
        raise NotImplementedError


class Design(ABC):
    """Parent class for all designs"""

    pass


class Evaluator(Protocol):
    """Parent class for all design evaluators"""

    @abstractmethod
    def evaluate(self, design: "Design") -> Any:
        pass


class DesignSpace(Protocol):
    """Parent class for a optimization DesignSpace classes"""

    @abstractmethod
    def check_constraints(self, full_results) -> bool:
        raise NotImplementedError

    @abstractmethod
    def n_obj(self) -> int:
        return NotImplementedError

    @abstractmethod
    def get_objectives(self, valid_constraints, full_results) -> tuple:
        raise NotImplementedError

    @abstractmethod
    def bounds(self) -> tuple:
        raise NotImplementedError


class DataHandler():
    """ Parent class for data handlers"""

    def __init__(self, archive_filepath, designer_filepath, full_results_transform=None):
        self.archive_filepath = archive_filepath
        self.designer_filepath = designer_filepath
        self.full_results_transform = full_results_transform

    def save_to_archive(self, x, design, full_results, objs):
        """ Save machine evaluation data to optimization archive using Pickle

        Args:
            x: Free variables used to create design
            design: Created design
            full_results: Input, output, and results corresponding to each step of an evaluator
            objs: Fitness values corresponding to a design
        """

        # Assign relevant data to OptiData class attributes
        opti_data = OptiData(x=x, design=design, full_results=full_results, objs=objs)

        # Write to pkl file. 'ab' indicates binary append
        with open(self.archive_filepath, 'ab') as archive:
            pickle.dump(opti_data, archive, -1)

    def load_from_archive(self):
        """ Load data from Pickle optimization archive """

        with open(self.archive_filepath, "rb") as f:
            while True:
                try:
                    # Use generator: each yield returns
                    # a single design from the archive
                    yield pickle.load(f)
                except EOFError:
                    # After we read and return the
                    # full archive, stop and return
                    break
                except pickle.UnpicklingError:
                    # If there is an issue with the archive file,
                    # this occurs so it can keep trying
                    continue

    def save_designer(self, designer):
        """ Save designer used in optimization"""

        with open(self.designer_filepath, 'wb') as des:
            pickle.dump(designer, des, -1)
    
    def save_object(self, obj, filename):
        """ Save object to specified filename"""

        with open(filename, 'wb') as fn:
            pickle.dump(obj, fn, -1)
    
    def load_object(self, filename):
        """load object from specified filename"""

        with open(filename, 'rb') as f:
            while 1:
                try:
                    obj = pickle.load(f)  # use generator
                except EOFError:
                    break
            return obj

    def get_archive_data(self):
        archive = self.load_from_archive()
        fitness = []
        free_vars = []
        for data in archive:
            fitness.append(data.objs)
            free_vars.append(data.x)
        return fitness, free_vars
    
    def get_pareto_data(self):
        """ Return data of Pareto optimal designs"""
        archive = self.load_from_archive()
        fitness, free_vars = self.get_archive_data()
        ndf, dl, dc, ndr = pg.fast_non_dominated_sorting(fitness)
        fronts_index = ndf[0]
        
        i = 0
        for data in archive:
            if i in fronts_index:
                yield data
            i = i+1

    def get_pareto_fitness_freevars(self):
        """ Extract fitness and free variables for Pareto optimal designs """

        archive = self.get_pareto_data()
        fitness = []
        free_vars = []
        for data in archive:
            fitness.append(data.objs)
            free_vars.append(data.x)
        return fitness, free_vars


class OptiData:
    """Object template for serializing optimization results with Pickle"""

    def __init__(self, x, design, full_results, objs):
        self.x = x
        self.design = design
        self.full_results = full_results
        self.objs = objs


class InvalidDesign(Exception):
    """Exception raised for invalid designs"""

    def __init__(self, message="Invalid Design"):
        self.message = message
        super().__init__(self.message)
