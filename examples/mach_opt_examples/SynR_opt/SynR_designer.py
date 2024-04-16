import os
import sys

from SynR_architect import SynR_Architect
from mach_eval.machines.materials.electric_steels import Arnon5
from mach_eval.machines.materials.miscellaneous_materials import (
    Copper,
    Steel,
    Air,
)
from mach_eval.machines.materials.AM_materials import (
    Fe3Si,
    L316,
)
from SynR_settings_handler import SynR_Settings_Handler
from mach_eval import MachineDesigner

# Specify machine specifications
SynR_parameters = {
    'p': 2,
    'Q': 36,
    'rated_speed': 70000,
    'rated_current': 4,   
}

SynR_materials = {
    "air_mat": Air,
    "rotor_iron_mat": Fe3Si,
    "rotor_barrier_mat": L316,
    "stator_iron_mat": Arnon5,
    "coil_mat": Copper,
    "shaft_mat": Steel,
}

SynR_winding = {
    "no_of_layers": 2,
    "layer_phases": [ ['U', 'U', 'U', 'W', 'W', 'W', 'V', 'V', 'V', 'U', 'U', 'U', 'W', 'W', 'W', 'V', 'V', 'V', 'U', 'U', 'U', 'W', 'W', 'W', 'V', 'V', 'V', 'U', 'U', 'U', 'W', 'W', 'W', 'V', 'V', 'V'],
                      ['U', 'U', 'W', 'W', 'W', 'V', 'V', 'V', 'U', 'U', 'U', 'W', 'W', 'W', 'V', 'V', 'V', 'U', 'U', 'U', 'W', 'W', 'W', 'V', 'V', 'V', 'U', 'U', 'U', 'W', 'W', 'W', 'V', 'V', 'V', 'U' ] ],
    "layer_polarity": [ ['+', '+', '+', '-', '-', '-', '+', '+', '+', '-', '-', '-', '+', '+', '+', '-', '-', '-', '+', '+', '+', '-', '-', '-', '+', '+', '+', '-', '-', '-', '+', '+', '+', '-', '-', '-'],
                        ['+', '+', '-', '-', '-', '+', '+', '+', '-', '-', '-', '+', '+', '+', '-', '-', '-', '+', '+', '+', '-', '-', '-', '+', '+', '+', '-', '-', '-', '+', '+', '+', '-', '-', '-', '+'] ],
    "pitch": 8,
    "Z_q": 29,
    "Kov": 1.8,
    "Kcu": 0.5,
    "phase_current_offset": 0,
}

# initialize Architect with machine specification
arch = SynR_Architect(SynR_parameters, SynR_materials, SynR_winding)
set_handler = SynR_Settings_Handler()

designer = MachineDesigner(arch, set_handler)