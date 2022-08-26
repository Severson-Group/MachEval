import numpy as np
import os
import sys

# change current working directory to file location
os.chdir(os.path.dirname(__file__))
# add the directory 3 levels above this file's directory to path for module import
sys.path.append("../../..")

# from .architect import Architect
from mach_eval.machines.bspm import BSPM_Machine
from mach_eval.machines.bspm.winding_layout import WindingLayout


class BSPM_Architect1:
    """
    This class acts as an interface between the end user and the BSPM_Machine class.
    Each Architect class has to be tailor made based on the expected free variables
    from the optimization algorithm

    """

    def __init__(self, specification):
        """
        Initializes the architecture with BSPM machine materials and design
        specifications.

        Parameters
        ----------
        specification : BSPMMachineSpec
            This is an object of the class BSPMMachineSpec.

        Returns
        -------
        None.

        """
        self.__design_spec = specification.design_spec
        self.__rotor_material = specification.rotor_material
        self.__stator_material = specification.stator_material
        self.__sleeve_material = specification.sleeve_material
        self.__coil_material = specification.coil_material
        self.__rotor_hub = specification.rotor_hub
        self.__air = specification.air
        self.__magnet_material = specification.magnet_material
        self.__shaft_material = specification.shaft_material
        self.__winding = WindingLayout(
            DPNV_or_SEPA=True, Qs=self.__design_spec["Q"], p=self.__design_spec["p"]
        )

    def create_new_design(self, x):
        """
        Takes in a list of free variables from the optimization algorithm,
        based on which the Machine class is instantiated.

        Parameters
        ----------
        x : List
            A list of free variables

        Returns
        -------
        machine_variant : BSPM_Machine
            An instance of the BSPM_Machine class containing all information
            relavant to a bearingless synchronous permanent magnet motor.

        """

        free_variables = self.x_to_dict(x)

        bspm_dimensions = {
            "alpha_st": free_variables["alpha_st"],
            "d_so": free_variables["d_so"],
            "w_st": free_variables["w_st"],
            "d_st": free_variables["d_st"],
            "d_sy": free_variables["d_sy"],
            "alpha_m": free_variables["alpha_m"],
            "d_m": free_variables["d_m"],
            "d_mp": free_variables["d_mp"],
            "d_ri": free_variables["d_ri"],
            # dependant variables
            "alpha_so": self.__get_alpha_so(free_variables),
            "d_sp": self.__get_d_sp(free_variables),
            "r_si": self.__get_r_si(free_variables),
            "alpha_ms": self.__get_alpha_ms(free_variables),
            "d_ms": self.__get_d_ms(free_variables),
            "r_sh": self.__get_r_sh(free_variables),
            "l_st": self.__get_l_st(free_variables),
            "d_sl": 0.00067,
            "delta_sl": 0.00011,
        }

        bspm_parameters = {
            "p": self.__design_spec["p"],
            "ps": self.__design_spec["ps"],
            "n_m": 1,
            "Q": self.__design_spec["Q"],
            "rated_speed": self.__design_spec["rated_speed"],
            "rated_power": self.__design_spec["rated_power"],
            "rated_voltage": self.__design_spec["voltage_rating"],
            "rated_current": self.__current_coil,
        }
        
        bspm_materials = {
            "air_mat": self.__air,
            "rotor_iron_mat": self.__rotor_material,
            "stator_iron_mat": self.__stator_material,
            "magnet_mat": self.__magnet_material,
            "rotor_sleeve_mat": self.__sleeve_material,
            "coil_mat": self.__coil_material,
            "shaft_mat": self.__shaft_material,
            "rotor_hub": self.__rotor_hub,
        }

        bspm_winding = {
            "no_of_layers": self.__winding.no_winding_layer,
            "layer_phases": [
                self.__winding.rightlayer_phase,
                self.__winding.leftlayer_phase,
            ],
            "layer_polarity": [
                self.__winding.rightlayer_polarity,
                self.__winding.leftlayer_polarity,
            ],
            "coil_groups": self.__winding.grouping_a,
            "pitch": self.__winding.y,
            "Z_q": self.__get_zQ(free_variables),
            "Kov": self.__design_spec["Kov"],
            "Kcu": self.__design_spec["Kcu"],
        }
        machine_variant = BSPM_Machine(
            bspm_dimensions, bspm_parameters, bspm_materials, bspm_winding
        )
        return machine_variant

    @property
    def __current_coil(self):
        I_rms = self.__design_spec["wire_A"] * self.__design_spec["J"]
        return I_rms

    def __get_d_sp(self, free_variables):
        d_so = free_variables["d_so"]
        return 1.5 * d_so

    def __get_r_si(self, free_variables):
        delta_e = free_variables["delta_e"]
        r_ro = free_variables["r_ro"]
        return r_ro + delta_e

    def __get_alpha_ms(self, free_variables):
        alpha_m = free_variables["alpha_m"]
        return alpha_m

    def __get_d_ms(self, free_variables):
        return 0

    def __get_r_sh(self, free_variables):
        r_ro = free_variables["r_ro"]
        d_m = free_variables["d_m"]
        d_ri = free_variables["d_ri"]
        return r_ro - d_m - d_ri

    def s_slot(self, free_variables):
        r_si = self.__get_r_si(free_variables)
        d_sp = self.__get_d_sp(free_variables)
        w_st = free_variables["w_st"]
        d_st = free_variables["d_st"]
        return (np.pi / self.__design_spec["Q"]) * (
            (r_si + d_sp + d_st) ** 2 - (r_si + d_sp) ** 2
        ) - w_st * d_st

    def __get_zQ(self, free_variables):
        s_slot = self.s_slot(free_variables)
        Kcu = self.__design_spec["Kcu"]
        zQ = round(Kcu * s_slot / (2 * self.__design_spec["wire_A"]))
        return zQ

    def __get_l_st(self, free_variables):
        return 0.025

    def __get_alpha_so(self, free_variables):
        alpha_so = free_variables["alpha_st"] / 2
        return alpha_so

    def __winding(self):
        x = self.__design_spec["Q"]
        return x

    def x_to_dict(self, x):
        free_variables = {
            "delta_e": x[0],
            "r_ro": x[1],
            "alpha_st": x[2],
            "d_so": x[3],
            "w_st": x[4],
            "d_st": x[5],
            "d_sy": x[6],
            "alpha_m": x[7],
            "d_m": x[8],
            "d_mp": x[9],
            "d_ri": x[10],
        }
        return free_variables
