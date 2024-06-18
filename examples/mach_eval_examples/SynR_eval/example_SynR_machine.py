import os
import sys
import numpy as np

from mach_eval.machines.materials.electric_steels import (Arnon5)
from mach_eval.machines.materials.miscellaneous_materials import (
    Steel,
    Copper,
    Air,
)
from mach_eval.machines.SynR.SynR_machine import SynR_Machine
from mach_eval.machines.SynR.SynR_machine_oper_pt import SynR_Machine_Oper_Pt

################ DEFINE SynR Machine ################
SynR_dimensions = {
    'alpha_b': 135,
    'r_sh': 6,
    'r_ri': 6,
    'r_ro': 49,
    'r_f1': 0.1,
    'r_f2': 0.1,
    'r_f3': 0.1,
    'd_r1': 4,
    'd_r2': 8,
    'd_r3': 8,
    'w_b1': 4,
    'w_b2': 4,
    'w_b3': 4,
    'l_b1': 34.1,
    'l_b2': 24.75,
    'l_b3': 13.1,
    'l_b4': 13,
    'l_b5': 10,
    'l_b6': 7,
    'alpha_st': 25,
    'alpha_so': 12.5,
    'r_si': 50,
    'd_so': 5,
    'd_sp': 9,
    'd_st': 40,
    'd_sy': 36,
    'w_st': 12,
    'l_st': 100,
}


SynR_parameters = {
    'p': 2,
    'Q': 12,
    "name": "Example_SynR_Machine",
    'rated_speed': 1800,
    'rated_current': 20,   
}

SynR_materials = {
    "air_mat": Air,
    "rotor_iron_mat": Arnon5,
    "stator_iron_mat": Arnon5,
    "coil_mat": Copper,
    "shaft_mat": Steel,
}

SynR_winding = {
    "no_of_layers": 2,
    "name_of_phases": ['U', 'V', 'W'],
    "layer_phases": [ ['U', 'W', 'V', 'U', 'W', 'V', 'U', 'W', 'V', 'U', 'W', 'V'],
                        ['W', 'V', 'U', 'W', 'V', 'U', 'W', 'V', 'U', 'W', 'V', 'U'] ],
    "layer_polarity": [ ['+', '-', '+', '-', '+', '-', '+', '-', '+', '-', '+', '-'],
                        ['-', '+', '-', '+', '-', '+', '-', '+', '-', '+', '-', '+'] ],
    "pitch": 2,
    "Z_q": 20,
    "Kov": 1.8,
    "Kcu": 0.5,
    "phase_current_offset": 0,
}

Example_SynR_Machine = SynR_Machine(
    SynR_dimensions, SynR_parameters, SynR_materials, SynR_winding
)

################ DEFINE SynR operating point ################
Machine_Op_Pt = SynR_Machine_Oper_Pt(
    speed=1800,
    speed_ratio=1,
    phi_0 = 0,
    ambient_temp=25,
    rotor_temp_rise=0,
)