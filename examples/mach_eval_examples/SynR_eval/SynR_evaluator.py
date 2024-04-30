import os
import sys
from time import time as clock_time

os.chdir(os.path.dirname(__file__))
sys.path.append("../../../")

from mach_eval import (MachineEvaluator, MachineDesign)
from electromagnetic_step import electromagnetic_step
from inductance_step import inductance_step
from example_SynR_machine import Example_SynR_Machine, Machine_Op_Pt

############################ Create Evaluator #####################
SynR_evaluator = MachineEvaluator(
    [
        inductance_step
    ]
)

design_variant = MachineDesign(Example_SynR_Machine, Machine_Op_Pt)

tic = clock_time()
results = SynR_evaluator.evaluate(design_variant)
toc = clock_time()

print("Time spent on SynR evaluation is %g min." % ((toc- tic)/60))