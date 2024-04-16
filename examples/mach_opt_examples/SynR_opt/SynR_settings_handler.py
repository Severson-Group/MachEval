import os
import sys

from mach_eval.machines.SynR.Vision_SynR_machine_oper_pt import Vision_SynR_Machine_Oper_Pt


class SynR_Settings_Handler:
    """This is a wrapper class designed to contain all relevant information
    on the operting point for obtaining eletrical performance evaluation of
    additively manufactured synchronous reluctance machines
    """

    def __init__(self):
        pass

    def get_settings(self, x):
        em_op = Vision_SynR_Machine_Oper_Pt(
            speed=70000,
            speed_ratio=x[10],
            phi_0=0,
            ambient_temp=25,
            rotor_temp_rise=0,
            )

        return em_op