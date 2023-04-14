# Created: 4/13/2023
# Author: Dante Newman

import sys
from copy import deepcopy
import numpy as np

# add the directory three levels above this file's directory to path for module import
sys.path.append("../../..")

from ..machine import Machine, MissingValueError, Winding, MachineComponent
from ..radial_machines import Shaft, SynR_Rotor_Iron, Stator


__all__ = ['SynR_Machine']

class SynR_Machine(Machine, Shaft, SynR_Rotor_Iron, Stator, Winding):

    def __init__(
        self,
        dimensions_dict: dict,
        parameters_dict: dict,
        materials_dict: dict,
        winding_dict: dict,
    ):
        """Creates a SynR_Machine object
        Keyword Argumets:
            machine_geometry_dict: dict
            materials_dict: dict
            winding_dict: dict
        Return Values
            machine: SynR_Machine
        """
        cls = SynR_Machine

        # first checks to see if the input dictionaries have the required values

        if (
            cls.check_required_values(
                cls, dimensions_dict, parameters_dict, materials_dict, winding_dict
            )
            == True
        ):
            setattr(self, "_dimensions_dict", dimensions_dict)
            setattr(self, "_parameters_dict", parameters_dict)
            setattr(self, "_materials_dict", materials_dict)
            setattr(self, "_winding_dict", winding_dict)

        else:
            # If required values are missing, collect them and raise exception
            missing_values = cls.get_missing_required_values(
                cls, dimensions_dict, parameters_dict, materials_dict, winding_dict
            )
            raise (
                MissingValueError(
                    missing_values, ("Missing inputs to initialize in" + str(cls))
                )
            )

    def get_missing_required_values(
        cls,
        dimensions_dict: dict,
        parameters_dict: dict,
        materials_dict: dict,
        winding_dict: dict,
    ) -> list:
        """returns missing required values from input dictionary

        Keyword Arguments:
            cls: Class
            machine_geometry_dict: dict
            materials_dict: dict
            winding_dict: dict
            nameplate_dict: dict
        Return Values
            missing_values: list
        """
        missing_values = []
        for a in [
            [cls.required_dimensions(), dimensions_dict],
            [cls.required_parameters(), parameters_dict],
            [cls.required_materials(), materials_dict],
            [cls.required_winding(), winding_dict],
        ]:
            for value in a[0]:
                if value in a[1]:
                    pass
                else:
                    missing_values.append(value)
        return missing_values

    def check_required_values(
        cls,
        dimensions_dict: dict,
        parameters_dict: dict,
        materials_dict: dict,
        winding_dict: dict,
    ) -> bool:
        """Checks to see if input dictionary have required values

        Keyword Argumets:
            machine_geometry_dict: dict
            materials_dict: dict
            winding_dict: dict
            nameplate_dict: dict
        Return Values
            bool
        """
        if not cls.get_missing_required_values(
            cls, dimensions_dict, parameters_dict, materials_dict, winding_dict
        ):
            return True
        else:
            return False

    @staticmethod
    def required_dimensions():
        req_dims = ("l_st",)
        for cl in SynR_Machine.__bases__:
            if issubclass(cl, MachineComponent):
                if cl.required_dimensions() is not None:
                    req_dims = req_dims + cl.required_dimensions()
        return req_dims

    @staticmethod
    def required_parameters():
        req_params = (
            "rated_power",  # kW
            "rated_speed",  # rad/s
            "rated_voltage",  # Vrms (line-to-line, Wye-Connect)
            "rated_current",
            "p",
            "name",
        )
        for cl in SynR_Machine.__bases__:
            if issubclass(cl, MachineComponent):
                if cl.required_parameters() is not None:
                    req_params = req_params + cl.required_parameters()
        return req_params

    @staticmethod
    def required_materials():
        req_mat = ()
        for cl in SynR_Machine.__bases__:
            if issubclass(cl, MachineComponent):
                if cl.required_materials() is not None:
                    req_mat = req_mat + cl.required_materials()
        return req_mat

    @staticmethod
    def required_winding():
        req_winding = ()
        for cl in SynR_Machine.__bases__:
            if issubclass(cl, Winding):
                if cl.required_winding() is not None:
                    req_winding = req_winding + cl.required_winding()
        return req_winding

        

    def clone(self, **kwargs) -> "SynR_Machine":
        """Creates a clone of the machine with updated parameters using *kwars.

        Args:
            **kwargs: Machine dictionary to be updated.
        Returns:
            Cloned SynR_Machine object.
        """
        cloned_machine = deepcopy(self)
        for dict_to_update, updated_values in kwargs.items():
            if dict_to_update == "dimensions_dict":
                for key, value in updated_values.items():
                    cloned_machine._dimensions_dict[key] = value

            if dict_to_update == "parameters_dict":
                for key, value in updated_values.items():
                    cloned_machine._parameters_dict[key] = value

            if dict_to_update == "materials_dict":
                for key, value in updated_values.items():
                    cloned_machine._materials_dict[key] = value

            if dict_to_update == "winding_dict":
                for key, value in updated_values.items():
                    cloned_machine._winding_dict[key] = value
        return cloned_machine

    @property
    def l_st(self):
        return self._dimensions_dict["l_st"]

    @property
    def mech_power(self):
        return self._parameters_dict["rated_power"]

    @property
    def rated_speed(self):
        return self._parameters_dict["rated_speed"]
    
    @property
    def no_of_phases(self):
        return self._winding_dict["no_of_phases"]
    
    @property
    def name_phases(self):
        return self._winding_dict["name_phases"]

    @property
    def omega_m(self):
        return self.rated_speed / 60 * 2 * np.pi

    @property
    def voltage_rating(self):
        return self._parameters_dict["rated_voltage"]

    @property
    def rated_current(self):
        return self._parameters_dict["rated_current"]

    @property
    def p(self):
        return self._parameters_dict["p"]

    @property
    def name(self):
        return self._parameters_dict["name"]

    @property
    def delta_e(self):
        delta_e = self.r_si - self.r_ro
        return delta_e

    @property
    def R_airgap(self):
        R_airgap = (self.r_si + self.r_ro) / 2
        return R_airgap

    @property
    def R_bar_center(self):
        R_bar_center = self.r_ri + self.d_ri + self.r_rb
        return R_bar_center

    @property
    def V_shaft(self):
        V_shaft = np.pi * self.r_ri**2 * self.l_st
        return V_shaft

    @property
    def V_rotor(self):
        V_rotor = self.l_st * np.pi * self.r_ro ** 2
        return V_rotor