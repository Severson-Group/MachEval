import os
import sys
from time import time as clock_time

os.chdir(os.path.dirname(__file__))
sys.path.append("../../../")

from mach_eval import (MachineEvaluator, MachineDesign)
from electromagnetic_vision_step import electromagnetic_vision_step
from electromagnetic_vision_step import electromagnetic_vision_step
from example_vision_SynR_machine import Example_Vision_SynR_Machine, Vision_Machine_Op_Pt

############################ Create Evaluator ########################
Vision_SynR_evaluator = MachineEvaluator(
    [
        electromagnetic_vision_step
    ]
)

design_variant = MachineDesign(Example_Vision_SynR_Machine, Vision_Machine_Op_Pt)

tic = clock_time()
results = Vision_SynR_evaluator.evaluate(design_variant)
toc = clock_time()

print("Time spent on Vision SynR evaluation is %g min." % ((toc - tic)/60))