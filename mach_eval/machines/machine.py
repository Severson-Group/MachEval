from abc import ABC, abstractmethod


class Machine(ABC):
    """ABC for Machine objects"""

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def required_parameters():
        pass

    @abstractmethod
    def check_required_values():
        pass

    @abstractmethod
    def get_missing_required_values():
        pass


class MachineComponent(ABC):
    """Base Class for Machine Components"""

    # @abstractmethod
    def required_parameters():
        pass

    def required_dimensions():
        pass

    @abstractmethod
    def required_materials():
        pass


class Winding:
    """Base Class for Machine Components"""

    def __init__(self):
        pass

    @staticmethod
    def required_winding():
        return (
            "no_of_layers",
            "layer_phases",
            "layer_polarity",
            "pitch",
            "Z_q",
            "Kov",
            "Kcu",
            "phase_current_offset"
        )

    @staticmethod
    def required_materials():
        return ("coil_mat",)

    @property
    def no_of_layers(self):
        return self._winding_dict["no_of_layers"]
    
    @property
    def name_of_phases(self):
        return self._winding_dict["name_of_phases"]

    @property
    def layer_phases(self):
        return self._winding_dict["layer_phases"]

    @property
    def layer_polarity(self):
        return self._winding_dict["layer_polarity"]

    @property
    def pitch(self):
        return self._winding_dict["pitch"]

    @property
    def Kov(self):
        return self._winding_dict["Kov"]

    @property
    def Kcu(self):
        return self._winding_dict["Kcu"]

    @property
    def coil_mat(self):
        return self._materials_dict["coil_mat"]

    @property
    def Z_q(self):
        return self._winding_dict["Z_q"]
    
    @property
    def phase_current_offset(self):
        return self._winding_dict["phase_current_offset"]


class Winding_IM(MachineComponent):
    """Base Class for Machine Components"""

    def required_parameters():
        return (
            "no_of_layers",
            "layer_phases",
            "layer_polarity",
            "pitch",
            "DriveW_zQ",
        )

    def required_materials():
        return ("coil_mat",)

    @property
    def no_of_layers(self):
        return self._machine_parameter_dict["no_of_layers"]

    @property
    def layer_phases(self):
        return self._machine_parameter_dict["layer_phases"]

    @property
    def layer_polarity(self):
        return self._machine_parameter_dict["layer_polarity"]

    @property
    def pitch(self):
        return self._machine_parameter_dict["pitch"]

    @property
    def DriveW_zQ(self):
        return self._machine_parameter_dict["DriveW_zQ"]

    @property
    def coil_mat(self):
        return self._materials_dict["coil_mat"]


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingValueError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
