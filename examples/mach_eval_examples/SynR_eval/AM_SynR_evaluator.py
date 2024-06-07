import os
import sys
from time import time as clock_time

os.chdir(os.path.dirname(__file__))
sys.path.append("../../../")

from mach_eval import (MachineEvaluator, MachineDesign)
from electromagnetic_AM_step import electromagnetic_AM_step
from inductance_AM_step import inductance_step
from example_AM_SynR_machine import Example_AM_SynR_Machine, Machine_Op_Pt

############################ Create Evaluator ########################
AM_SynR_evaluator = MachineEvaluator(
    [
        electromagnetic_AM_step
    ]
)

design_variant = MachineDesign(Example_AM_SynR_Machine, Machine_Op_Pt)

tic = clock_time()
results = AM_SynR_evaluator.evaluate(design_variant)
toc = clock_time()

print("Time spent on AM SynR evaluation is %g min." % ((toc- tic)/60))