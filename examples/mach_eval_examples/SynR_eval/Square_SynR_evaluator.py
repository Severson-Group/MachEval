import os
import sys
from time import time as clock_time

os.chdir(os.path.dirname(__file__))
sys.path.append("../../../")

from mach_eval import (MachineEvaluator, MachineDesign)
from electromagnetic_square_step import electromagnetic_square_step
from example_Square_SynR_machine import Example_Square_SynR_Machine, Machine_Op_Pt

############################ Create Evaluator ########################
Square_SynR_evaluator = MachineEvaluator(
    [
        electromagnetic_square_step
    ]
)

design_variant = MachineDesign(Example_Square_SynR_Machine, Machine_Op_Pt)

tic = clock_time()
results = Square_SynR_evaluator.evaluate(design_variant)
toc = clock_time()

print("Time spent on AM SynR evaluation is %g min." % ((toc- tic)/60))