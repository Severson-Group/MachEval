import os
import sys

os.chdir(os.path.dirname(__file__))
sys.path.append("../../../")

from mach_opt import DesignProblem, DesignOptimizationMOEAD
from mach_eval import MachineEvaluator
from my_data_handler import MyDataHandler
from SynR_designer import designer
from SynR_ds import SynRDesignSpace
from optimization_vision_step import optimization_vision_step
from time import time as clock_time

SynR_evaluator = MachineEvaluator(
    [
        optimization_vision_step,
    ]
)

# set bounds for pygmo optimization problem
dims = (
    6, # r_ri
    50, #r_ro
    4, # d_r1
    6, # d_r2
    4, # w_b1
    4, # w_b2
    25, # l_b1
    27, # l_b2
    12, # l_b4
    6, # l_b5
    1, # speed ratio
)

bounds = [
    [0.5 * dims[0], 2 * dims[0]],  # r_ri
    [0.9 * dims[1], 1 * dims[1]],  # r_ro
    [0.8 * dims[2], 1.2 * dims[2]],  # d_r1
    [0.8 * dims[3], 1.2 * dims[3]],  # d_r2
    [0.8 * dims[4], 1.2 * dims[4]],  # w_b1
    [0.8 * dims[5], 1.2 * dims[5]],  # w_b2
    [0.8 * dims[6], 1.2 * dims[6]],  # l_b1
    [0.8 * dims[7], 1.2 * dims[7]],  # l_b2
    [0.8 * dims[8], 1.2 * dims[8]],  # l_b4
    [0.8 * dims[9], 1.2 * dims[9]],  # l_b5
    [0.6 * dims[10], 1 * dims[10]],  # speed ratio
]

n_obj = 3

# create optimization Design Space object
opt_settings = SynRDesignSpace(n_obj, bounds)

# create optimization Data Handler
path = os.path.dirname(__file__)
arch_file = path + r"\opti_arch.pkl"  # specify file where archive data will reside
des_file = path + r"\opti_designer.pkl"
pop_file = path + r"\latest_pop.csv"  # csv file holding free variables of latest population
dh = MyDataHandler(arch_file, des_file)  # initialize data handler with required file paths

# create pygmo Problem
design_prob = DesignProblem(designer, SynR_evaluator, opt_settings, dh)
# define pygmo MOEAD optimization
design_opt = DesignOptimizationMOEAD(design_prob)

# define population size and number of generations
pop_size = 78
gen_size = 20 # CHANGE ONCE OPTIMIZATION IS FINALIZED!

# load latest population
population = design_opt.load_pop(filepath=pop_file, pop_size=pop_size)
# create random initial population if no prior data exists
if population is None:
    print("NO EXISTING POPULATION TO LOAD")
    population = design_opt.initial_pop(pop_size)

# RUN OPTIMIZATION
tic = clock_time()
pop = design_opt.run_optimization(population, gen_size, pop_file)
toc = clock_time()
print("Time spent on Vision SynR optimization is %g hours." % ((toc- tic)/3600))