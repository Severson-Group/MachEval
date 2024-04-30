import os
import sys
from time import time as clock_time

os.chdir(os.path.dirname(__file__))
sys.path.append("../../../")

from mach_eval import (MachineEvaluator, MachineDesign)
from electromagnetic_step import electromagnetic_step
#from electromagnetic_vision_step import electromagnetic_vision_step
from example_SynR_machine import Example_SynR_Machine, Machine_Op_Pt
#from example_vision_SynR_machine import Example_Vision_SynR_Machine, Vision_Machine_Op_Pt

############################ Create Evaluator #####################
SynR_evaluator = MachineEvaluator(
    [
        electromagnetic_step
    ]
)

design_variant = MachineDesign(Example_SynR_Machine, Machine_Op_Pt)

tic = clock_time()
results = SynR_evaluator.evaluate(design_variant)
toc = clock_time()

print("Time spent on SynR evaluation is %g min." % ((toc- tic)/60))