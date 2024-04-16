import copy
import numpy as np
import os
import sys

from mach_eval.analyzers.torque_data import (
    ProcessTorqueDataProblem,
    ProcessTorqueDataAnalyzer,
)
from mach_eval.analyzers.mechanical.windage_loss import (
    WindageLossProblem,
    WindageLossAnalyzer,
)

class Vision_SynR_Opt_PostAnalyzer:
    def copper_loss(self):
        return 3 * (self.I ** 2) * (self.R_wdg + self.R_wdg_coil_ends + self.R_wdg_coil_sides)

    def get_next_state(results, in_state):
        state_out = copy.deepcopy(in_state)
        machine = state_out.design.machine
        op_pt = state_out.design.settings

        ############################ Extract required info ###########################
        no_of_steps = results["no_of_steps"]
        no_of_rev = results["no_of_rev"]
        operating_speed = results["new_speed"]
        max_stress = results["max_stress"]
        yield_stress = results["yield_stress"]
        number_of_total_steps = results["current"].shape[0]
        i1 = number_of_total_steps - no_of_steps
        i2 = - int(no_of_steps / no_of_rev * 0.25)
        omega_m = results["new_speed"] * 2 * np.pi / 60
        m = 3
        R_wdg = results["stator_wdg_resistances"][0]

        results["current"] = results["current"].iloc[i1:]
        results["torque"] = results["torque"].iloc[i1:]
        results["iron_loss"] = results["iron_loss"]
        results["hysteresis_loss"] = results["hysteresis_loss"]
        results["eddy_current_loss"] = results["eddy_current_loss"]

        ############################ calculating volumes ###########################
        machine = state_out.design.machine
        V_sh = np.pi*(machine.r_sh**2)*machine.l_st
        V_rfe = machine.l_st * (np.pi * (machine.r_ro ** 2 - machine.r_ri**2) - 2 * machine.p * (machine.w_b1 * (2 * machine.l_b1 + machine.l_b4) + machine.w_b2 * (2 * machine.l_b2 + machine.l_b5) + machine.w_b3 * (2 * machine.l_b3 + machine.l_b6)))
        V_machine = machine.l_st * np.pi * (machine.r_si + machine.d_sp + machine.d_st + machine.d_sy) ** 2

        ############################ Post-processing #################################
        rotor_mass = (
            V_rfe * 1e-9 * machine.rotor_iron_mat["rotor_iron_material_density"]
            + V_sh * 1e-9 * machine.shaft_mat["shaft_material_density"]
        )
        machine_volume = (V_machine) * 1e-9

        ############################ post processing ###########################
        # Torque
        torque_prob = ProcessTorqueDataProblem(results["torque"]["TorCon"])
        torque_analyzer = ProcessTorqueDataAnalyzer()
        torque_avg, torque_ripple = torque_analyzer.analyze(torque_prob)
        TRW = torque_avg / rotor_mass
        TRV = torque_avg / machine_volume
        PRW = TRW * omega_m
        PRV = TRV * omega_m

        # Windage
        windage_loss_prob = WindageLossProblem(
            Omega=omega_m, R_ro=machine.r_ro/1000, stack_length=machine.l_st/1000,
            R_st=machine.r_si/1000, u_z=0, T_air=op_pt.ambient_temp
            )
        [windage_loss_radial, windage_loss_endFace, windage_loss_axial] = WindageLossAnalyzer.analyze(windage_loss_prob)

        # Losses
        # From JMAG
        stator_iron_loss = results["iron_loss"]["StatorCore"][0]
        rotor_iron_loss = results["iron_loss"]["RotorCore"][0]
        stator_eddy_current_loss = results["eddy_current_loss"]["StatorCore"][0]
        rotor_eddy_current_loss = results["eddy_current_loss"]["RotorCore"][0]
        stator_hysteresis_loss= results["hysteresis_loss"]["StatorCore"][0]
        rotor_hysteresis_loss = results["hysteresis_loss"]["RotorCore"][0]
        stator_ohmic_loss = results["ohmic_loss"]["Coils"].iloc[i2:].mean()
        windage_loss = windage_loss_axial + windage_loss_endFace + windage_loss_radial
        
        # Calculate stator winding ohmic losses
        I_hat = machine.rated_current
        stator_calc_ohmic_loss = R_wdg * m / 2 * I_hat ** 2

        # Total losses, output power, and efficiency
        total_losses = (
            stator_hysteresis_loss + rotor_hysteresis_loss + stator_calc_ohmic_loss + windage_loss)
        P_out = torque_avg * omega_m
        efficiency = P_out / (P_out + total_losses)

        ############################ Output #################################
        post_processing = {}
        post_processing["torque_avg"] = torque_avg
        post_processing["torque_ripple"] = torque_ripple
        post_processing["TRW"] = TRW
        post_processing["TRV"] = TRV
        post_processing["PRW"] = PRW
        post_processing["PRV"] = PRV
        post_processing["l_st"] = machine.l_st
        post_processing["rotor_mass"] = rotor_mass
        post_processing["machine_volume"] = machine_volume
        post_processing["stator_iron_loss"] = stator_iron_loss
        post_processing["rotor_iron_loss"] = rotor_iron_loss
        post_processing["stator_eddy_current_loss"] = stator_eddy_current_loss
        post_processing["rotor_eddy_current_loss"] = rotor_eddy_current_loss
        post_processing["stator_hysteresis_loss"] = stator_hysteresis_loss
        post_processing["rotor_hysteresis_loss"] = rotor_hysteresis_loss
        post_processing["stator_ohmic_loss"] = stator_ohmic_loss
        post_processing["stator_calc_ohmic_loss"] = stator_calc_ohmic_loss
        post_processing["total_losses"] = total_losses
        post_processing["output_power"] = P_out
        post_processing["efficiency"] = efficiency

        state_out.conditions.em = post_processing

        print("\n************************ LOSSES ************************")
        print("Stator = ", stator_hysteresis_loss, " W")
        print("Rotor = ", rotor_hysteresis_loss, " W")
        print("Ohmic = ", stator_calc_ohmic_loss, " W",)
        print("Windage = ", windage_loss, " W")
        print("*************************************************************************\n")

        print("\n************************ ELECTROMAGNETIC RESULTS ************************")
        print("Operating speed = ", operating_speed, " RPM")
        print("Max Stress = ", max_stress/(10**6), " MPa")
        if max_stress > yield_stress:
            print("The maximum stress EXCEEDS the yield stress!")
        else:
            print("The maximum stress does not exceed the yield stress!")
        print("Torque density = ", TRV, " Nm/m3",)
        print("Torque ripple = ", torque_ripple)
        print("Power density = ", PRV, " W/m3",)
        print("Efficiency = ", efficiency * 100, " %")
        print("*************************************************************************\n")

        return state_out