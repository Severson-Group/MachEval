import copy
import numpy as np
import os
import sys

# add the directory 3 levels above this file's directory to path for module import
sys.path.append(os.path.dirname(__file__)+"/../../..")
print(os.path.dirname(__file__)+"/../../..")

from mach_eval.analyzers.force_vector_data import (
    ProcessForceDataProblem,
    ProcessForceDataAnalyzer,
)
from mach_eval.analyzers.torque_data import (
    ProcessTorqueDataProblem,
    ProcessTorqueDataAnalyzer,
)


class BSPM_EM_PostAnalyzer:
    def copper_loss(self):
        return 6 * ((self.current_trms / 2) ** 2 + self.current_srms**2) * self.R_coil

    def get_next_state(results, in_state):
        state_out = copy.deepcopy(in_state)
        machine = state_out.design.machine

        ############################ extract required info ###########################
        length = results["current"].shape[0]
        i = length - results["range_fine_step"]
        results["current"] = results["current"].iloc[i:]

        results["torque"] = results["torque"].iloc[i:]
        results["force"] = results["force"].iloc[i:]
        results["voltage"] = results["voltage"].iloc[i:]
        results["hysteresis_loss"] = results["hysteresis_loss"]
        results["iron_loss"] = results["iron_loss"]
        results["eddy_current_loss"] = results["eddy_current_loss"].iloc[i:]

        ############################ calculating volumes ###########################
        # volumes = {}
        # # shaft volume
        # machine = state_out.design.machine
        # r_sh = machine.r_sh
        l_st = machine.l_st
        # volumes['V_sh'] = np.pi*(r_sh**2)*l_st

        # # rotor iron volume
        # r_ro    = machine.r_ro
        # alpha_m = machine.alpha_m*np.pi/180
        # d_m     = machine.d_m
        # d_mp    = machine.d_mp
        # p       = machine.p
        # volumes['V_rfe'] = np.pi*((r_ro-d_m)**2-r_sh**2)*l_st + (np.pi - p*alpha_m)*((r_ro-d_mp)**2 -
        # (r_ro-d_m)**2)*l_st

        # # magnet volume
        # volumes['V_rpm'] = p*alpha_m*(r_ro**2 - (r_ro-d_m)**2)*l_st

        # # sleeve volume
        # d_sl    = machine.d_sl
        # volumes['V_rsl'] = np.pi*((r_ro+d_sl)**2 - r_ro**2)*l_st

        # # Copper volume
        s_slot = machine.s_slot
        # V_scu = machine.Q * self.l_coil * machine.Kcu * machine.s_slot /machine.no_of_layers

        # # Stator volume
        r_so = machine.r_so
        r_si = machine.r_si
        V_sfe = np.pi * (r_so**2 - r_si**2) * l_st - machine.Q * s_slot * l_st

        ############################ post processing #################################
        torque_prob = ProcessTorqueDataProblem(results["torque"]["TorCon"])
        torque_analyzer = ProcessTorqueDataAnalyzer()
        torque_avg, torque_ripple = torque_analyzer.analyze(torque_prob)

        force_prob = ProcessForceDataProblem(
            Fx=results["force"][r"ForCon:1st"],
            Fy=results["force"][r"ForCon:2nd"],
        )
        force_ana = ProcessForceDataAnalyzer()
        f_x, f_y, force_avg, Em, Ea = force_ana.analyze(force_prob)

        post_processing = {}
        post_processing["torque_avg"] = torque_avg
        post_processing["torque_ripple"] = torque_ripple

        post_processing["Fx"] = f_x
        post_processing["Fy"] = f_y
        post_processing["force_avg"] = force_avg
        rotor_weight = (
            machine.V_rfe * machine.rotor_iron_mat["core_material_density"]
            + machine.V_sh * machine.shaft_mat["shaft_material_density"]
            + machine.V_rPM * machine.magnet_mat["magnet_material_density"]
        )
        post_processing["FRW"] = force_avg / rotor_weight
        post_processing["Em"] = Em
        post_processing["Ea"] = Ea

        post_processing["copper_loss"] = results["copper_loss"]
        post_processing["rotor_iron_loss"] = (
            results["iron_loss"]["NotchedRotor"][0]
            + results["eddy_current_loss"]["NotchedRotor"].mean()
        )
        post_processing["stator_iron_loss"] = (
            results["iron_loss"]["StatorCore"][0]
            + results["eddy_current_loss"]["StatorCore"].mean()
        )
        post_processing["magnet_loss"] = results["eddy_current_loss"]["Magnet"].mean()

        post_processing["phase_voltage_rms"] = compute_vrms(results["voltage"])
        post_processing["power_factor"] = compute_power_factor(
            results["voltage"],
            results["current"],
            target_freq=machine.mech_omega * machine.p / (2 * np.pi),
        )

        state_out.conditions.em = post_processing

        # define parameters for stator thermal
        state_out.conditions.g_sy = post_processing["stator_iron_loss"] / V_sfe
        state_out.conditions.g_th = post_processing["stator_iron_loss"] / V_sfe
        state_out.conditions.Q_coil = post_processing["copper_loss"] / machine.Q

        print("\n************************ EM RESULT ************************")
        print("Torque = ", torque_avg, " Nm")
        print(
            "Torque density = ",
            torque_avg
            / (machine.V_rfe + machine.V_sh + machine.V_rPM),
            " Nm/m3",
        )
        print("Power = ", torque_avg * 160000 * np.pi / 30, " W")

        FRW = force_avg / (rotor_weight * 9.8)

        print("Force = ", force_avg, " N")
        print("Force per rotor weight = ", FRW, " pu")
        print("Force error angle = ", Ea, " deg")
        print("************************************************************\n")

        return state_out


def compute_vrms(voltage_df):
    phase_voltage = voltage_df["Terminal_Wt"]
    rms_voltage = np.sqrt(sum(np.square(phase_voltage)) / len(phase_voltage))
    return rms_voltage


def compute_power_factor(
    voltage_df, current_df, target_freq, numPeriodicalExtension=1000
):
    mytime = current_df.index
    voltage = voltage_df["Terminal_Wt"]
    current = current_df["coil_Wb"]

    power_factor = compute_power_factor_from_half_period(
        voltage,
        current,
        mytime,
        targetFreq=target_freq,
        numPeriodicalExtension=numPeriodicalExtension,
    )
    return power_factor


# https://dsp.stackexchange.com/questions/11513/estimate-frequency-and-peak-value-of-a-signals-fundamental
# define N_SAMPLE ((long int)(1.0/(0.1*TS))) // Resolution 0.1 Hz = 1 / (N_SAMPLE * TS)
class GoertzelDataStruct(object):
    """docstring for GoertzelDataStruct"""

    def __init__(
        self,
        id=None,
    ):
        self.id = id
        self.bool_initialized = False
        self.sine = None
        self.cosine = None
        self.coeff = None
        self.scalingFactor = None
        self.q = None
        self.q2 = None
        self.count = None
        self.k = None  # k is the normalized target frequency
        self.real = None
        self.imag = None
        self.accumSquaredData = None
        self.ampl = None
        self.phase = None

    # /************************************************
    #  * Real time implementation to avoid the array of input double *data[]
    #  * with Goertzel Struct to store the variables and the output values
    #  *************************************************/
    def goertzel_realtime(gs, targetFreq, numSamples, samplingRate, data):
        # gs is equivalent to self
        try:
            len(data)
        except:
            pass
        else:
            raise Exception(
                "This is for real time implementation of Goertzel, hence data must be a scalar rather than array."
            )

        if not gs.bool_initialized:
            gs.bool_initialized = True

            gs.count = 0
            gs.k = 0.5 + ((numSamples * targetFreq) / samplingRate)
            omega = (2.0 * np.pi * gs.k) / numSamples
            gs.sine = np.sin(omega)
            gs.cosine = np.cos(omega)
            gs.coeff = 2.0 * gs.cosine
            gs.q1 = 0
            gs.q2 = 0
            gs.scalingFactor = 0.5 * numSamples
            gs.accumSquaredData = 0.0

        q0 = gs.coeff * gs.q1 - gs.q2 + data
        gs.q2 = gs.q1
        gs.q1 = (
            q0  # // q1 is the newest output vk[N], while q2 is the last output vk[N-1].
        )

        gs.accumSquaredData += data * data

        gs.count += 1
        if gs.count >= numSamples:
            # // calculate the real and imaginary results with scaling appropriately
            gs.real = (
                gs.q1 * gs.cosine - gs.q2
            ) / gs.scalingFactor  # // inspired by the python script of sebpiq
            gs.imag = (gs.q1 * gs.sine) / gs.scalingFactor

            # // reset
            gs.bool_initialized = False
            return True
        else:
            return False

    def goertzel_offline(gs, targetFreq, samplingRate, data_list):
        # gs is equivalent to self
        numSamples = len(data_list)
        if not gs.bool_initialized:
            gs.bool_initialized = True

            gs.count = 0
            gs.k = 0.5 + ((numSamples * targetFreq) / samplingRate)
            omega = (2.0 * np.pi * gs.k) / numSamples
            gs.sine = np.sin(omega)
            gs.cosine = np.cos(omega)
            gs.coeff = 2.0 * gs.cosine
            gs.q1 = 0
            gs.q2 = 0
            gs.scalingFactor = 0.5 * numSamples
            gs.accumSquaredData = 0.0

        for data in data_list:
            q0 = gs.coeff * gs.q1 - gs.q2 + data
            gs.q2 = gs.q1
            gs.q1 = q0  # // q1 is the newest output vk[N], while q2 is the last output vk[N-1].

            gs.accumSquaredData += data * data

            gs.count += 1
            if gs.count >= numSamples:
                # // calculate the real and imaginary results with scaling appropriately
                gs.real = (
                    gs.q1 * gs.cosine - gs.q2
                ) / gs.scalingFactor  # // inspired by the python script of sebpiq
                gs.imag = (gs.q1 * gs.sine) / gs.scalingFactor

                # // reset
                gs.bool_initialized = False
                return True
        return None


def compute_power_factor_from_half_period(
    voltage, current, mytime, targetFreq=1e3, numPeriodicalExtension=1000
):
    gs_u = GoertzelDataStruct("Goertzel Struct for Voltage\n")
    gs_i = GoertzelDataStruct("Goertzel Struct for Current\n")

    TS = mytime[-1] - mytime[-2]

    if type(voltage) != type([]):
        voltage = voltage.tolist() + (-voltage).tolist()
        current = current.tolist() + (-current).tolist()
    else:
        voltage = voltage + [-el for el in voltage]
        current = current + [-el for el in current]

    voltage *= numPeriodicalExtension
    current *= numPeriodicalExtension

    gs_u.goertzel_offline(targetFreq, 1.0 / TS, voltage)
    gs_i.goertzel_offline(targetFreq, 1.0 / TS, current)

    gs_u.ampl = np.sqrt(gs_u.real * gs_u.real + gs_u.imag * gs_u.imag)
    gs_u.phase = np.arctan2(gs_u.imag, gs_u.real)

    gs_i.ampl = np.sqrt(gs_i.real * gs_i.real + gs_i.imag * gs_i.imag)
    gs_i.phase = np.arctan2(gs_i.imag, gs_i.real)

    phase_difference_in_deg = (gs_i.phase - gs_u.phase) / np.pi * 180
    power_factor = np.cos(gs_i.phase - gs_u.phase)
    return power_factor
