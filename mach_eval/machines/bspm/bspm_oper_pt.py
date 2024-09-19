__all__ = ["BSPM_Machine_Oper_Pt"]


class BSPM_Machine_Oper_Pt:
    """This is a wrapper class designed to contain all relevant information
    on the operating point for obtaining electrical performance evaluation of
    bearingless permanent magnet electric machines
    """

    def __init__(
        self,
        Id=0,
        Iq=0.95,
        Ix=0,
        Iy=0.05,
        speed=5250,
        ambient_temp=20,
        rotor_temp_rise=0,
    ):
        """
        Args:
            Id: PU value of d-axis current.
            Iq: PU value of q-axis current.
            Ix: PU value of x-axis current.
            Iy: PU value of y-axis current.
            speed: Machine rotational speed in RPM.
            ambient_temp: ambient temperature in celsius.
            rotor_temp_rise: allowed rotor temperature rise in K

        """

        self.__Id = Id
        self.__Iq = Iq
        self.__Ix = Ix
        self.__Iy = Iy
        self.__speed = speed
        self.__ambient_temp = ambient_temp
        self.__rotor_temp_rise = rotor_temp_rise

    @property
    def Id(self):
        return self.__Id

    @property
    def Iq(self):
        return self.__Iq

    @property
    def Ix(self):
        return self.__Ix

    @property
    def Iy(self):
        return self.__Iy

    @property
    def speed(self):
        return self.__speed

    @property
    def magnet_temp(self):
        return self.__magnet_temp

    @property
    def ambient_temp(self):
        return self.__ambient_temp

    @property
    def rotor_temp_rise(self):
        return self.__rotor_temp_rise
