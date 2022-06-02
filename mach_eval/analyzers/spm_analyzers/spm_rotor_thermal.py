# -*- coding: utf-8 -*-
"""
Created on Mon May 23 09:34:29 2022

@author: Martin Johnson
"""
import numpy as np
import scipy.optimize as op
import sys
sys.path.append("..")
import analyzers.general_analyzers.thermal_network_analyzer as tb


class SPM_RotorThemalProblem:
    def __init__(self,mat_dict,r_sh,d_ri,r_ro,d_sl,r_si,l_st,l_hub,T_ref,u_z,losses,omega):
        self.mat_dict=mat_dict
        self.r_sh=r_sh
        self.d_ri=d_ri
        self.r_ro=r_ro
        self.d_sl=d_sl
        self.r_si=r_si
        self.l_st=l_st
        self.l_hub=l_hub
        
        self.losses=losses
        self.T_ref=T_ref
        self.u_z=u_z
        self.omega=omega
        
        self.R_1=self.r_sh
        self.R_2=self.R_1+self.d_ri
        self.R_3=self.r_ro
        self.R_4=self.R_3+self.d_sl


class SPM_RotorThemalAnalyzer:
    def __init__(self):
        self.base_ana=tb.ThermalNetworkAnalyzer()
    def analyze(self,problem):
        N_nodes=33
        Res= self.create_resistance_network(problem)

        ################################################
        #           Load Losses into loss Vector
        ################################################
        Q_dot = np.zeros([33, 1])
        Q_dot[1] = 0  # No shaft losses
        Q_dot[3] = problem.losses["rotor_iron_loss"]
        Q_dot[5] = problem.losses["magnet_loss"]

        # print('Magnet Losses:',Q_dot[5])
        ################################################
        #    Create Reference Temperature Vector
        ################################################
        
        T_ref=[[0,problem.T_ref],]
        
        base_prob=tb.ThermalNetworkProblem(Res,Q_dot,T_ref,N_nodes)
        T=self.base_ana.analyze(base_prob)
        return T

    def create_resistance_network(self,problem):
        ################################################
        #           Load Material Properties
        ################################################
        shaft_k = problem.mat_dict["shaft_therm_conductivity"]
        rotor_core_k = problem.mat_dict["core_therm_conductivity"]
        pm_k = problem.mat_dict["magnet_therm_conductivity"]
        sleeve_k = problem.mat_dict["sleeve_therm_conductivity"]
        air_k = problem.mat_dict["air_therm_conductivity"]
        air_mu = problem.mat_dict["air_viscosity"]
        air_cp = problem.mat_dict["air_cp"]
        hub_k = problem.mat_dict["rotor_hub_therm_conductivity"]

        ################################################
        #             Load Operating Point
        ################################################
        omega = problem.omega
        ################################################
        #           Create Material Objects
        ################################################

        ##############
        # Shaft
        ##############
        sh_mat = tb.Material(shaft_k)
        ##############
        # Rotor Core
        ##############
        rc_mat = tb.Material(rotor_core_k)
        ##############
        # PM
        ##############
        pm_mat = tb.Material(pm_k)
        ##############
        # Sleeve
        ##############
        sl_mat = tb.Material(sleeve_k)
        ##############
        # Hub
        ##############
        hub_mat = tb.Material(hub_k)
        ##############
        # Air
        ##############
        air_mat = tb.Material(air_k)
        air_mat.set_cp(air_cp)
        air_mat.set_mu(air_mu)

        ################################################
        #           Define Geometric Values
        ################################################

        ##############
        # Radial Direction
        ##############
        R_1 = problem.R_1
        R_2 = problem.R_2
        R_3 = problem.R_3
        R_4 = problem.R_4
        R_st = problem.r_si
        # delta=problem.delta
        R_rc = (R_1 + R_2) / 2
        R_pm = (R_2 + R_3) / 2
        R_sl = (R_3 + R_4) / 2
        # print(R_1,R_rc,R_2,R_pm,R_3,R_sl,R_4)
        ##############
        # Axial Direction
        ##############
        stack_length = problem.l_st
        # print('stack length is:',stack_length)
        hub_length = problem.l_hub
        shaft_out = 0.030 + hub_length + stack_length
        L_1 = stack_length / 2
        L_2 = stack_length / 2 + hub_length / 2
        L_3 = stack_length / 2 + hub_length
        L_4 = shaft_out
        u_z = problem.u_z

        ################################################
        #           Create Resistance Objects
        ################################################
        Resistances = []
        ##############
        # Path 0
        ##############
        Descr = "Shaft to rotor core interface (Approximated as Plane Wall)"
        A_sh_1 = stack_length * 2 * np.pi * R_1
        Resistances.append(tb.plane_wall(sh_mat, 1, 2, 0, R_1, A_sh_1))
        Resistances[0].Descr = Descr
        ##############
        # Path 1
        ##############
        Descr = "Shaft/RC interface to rotor core center"
        Resistances.append(tb.cylind_wall(rc_mat, 2, 3, R_1, R_rc, stack_length))
        Resistances[1].Descr = Descr
        ##############
        # Path 2
        ##############
        Descr = "Rotor core center to PM/RC interface"
        Resistances.append(tb.cylind_wall(rc_mat, 3, 4, R_rc, R_2, stack_length))
        Resistances[2].Descr = Descr
        ##############
        # Path 3
        ##############
        Descr = "PM/RC interface to PM center"
        Resistances.append(tb.cylind_wall(pm_mat, 4, 5, R_2, R_pm, stack_length))
        Resistances[3].Descr = Descr
        ##############
        # Path 4
        ##############
        Descr = "PM center to PM/sleeve Interface"
        Resistances.append(tb.cylind_wall(pm_mat, 5, 6, R_pm, R_3, stack_length))
        Resistances[4].Descr = Descr
        ##############
        # Path 5
        ##############
        Descr = "PM/Sleeve Interface to sleeve center"
        Resistances.append(tb.cylind_wall(sl_mat, 6, 7, R_3, R_sl, stack_length))
        Resistances[5].Descr = Descr
        ##############
        # Path 6
        ##############
        Descr = "Sleeve center to outer rotor edge"
        Resistances.append(tb.cylind_wall(sl_mat, 7, 8, R_sl, R_4, stack_length))
        Resistances[6].Descr = Descr
        ##############
        # Path 7
        ##############
        Descr = "Outer rotor edge to air"
        A_rotor_out = stack_length * (2 * np.pi * R_4)
        Resistances.append(
            tb.air_gap_conv(air_mat, 8, 0, omega, R_4, R_st, u_z, A_rotor_out)
        )
        print(Resistances[7].h)
        Resistances[7].Descr = Descr
        ##############
        # Path 8
        ##############
        Descr = "Rotor core center to Hub/RotorCore Interface"
        A_rcHub = np.pi * (R_2 ** 2 - R_1 ** 2)
        Resistances.append(tb.plane_wall(rc_mat, 3, 9, 0, L_1, A_rcHub))
        Resistances[8].Descr = Descr
        ##############
        # Path 9
        ##############
        Descr = "PM center to Hub/PM Interface"
        A_pmHub = np.pi * (R_3 ** 2 - R_2 ** 2)
        Resistances.append(tb.plane_wall(pm_mat, 5, 10, 0, L_1, A_pmHub))
        Resistances[9].Descr = Descr
        ##############
        # Path 10
        ##############
        Descr = "Sleeve center to Hub/Sleeve Interface"
        A_slHub = np.pi * (R_4 ** 2 - R_3 ** 2)
        Resistances.append(tb.plane_wall(sl_mat, 7, 11, 0, L_1, A_slHub))
        Resistances[10].Descr = Descr
        ##############
        # Path 11
        ##############
        Descr = "Shaft Center to shaft Inline with Hub center"
        A_sh = np.pi * (R_1 ** 2)
        Resistances.append(tb.plane_wall(sh_mat, 1, 12, 0, L_2, A_sh))
        Resistances[11].Descr = Descr
        ##############
        # Path 12
        ##############
        Descr = "Hub/Rotor Core interface to Center of Hub inline with Rotor Core"
        Resistances.append(tb.plane_wall(hub_mat, 9, 14, L_1, L_2, A_rcHub))
        Resistances[12].Descr = Descr
        ##############
        # Path 13
        ##############
        Descr = "Hub/PM interface to Center of Hub inline with PM"
        Resistances.append(tb.plane_wall(hub_mat, 10, 15, L_1, L_2, A_pmHub))
        Resistances[13].Descr = Descr
        ##############
        # Path 14
        ##############
        Descr = "Hub/Sleeve interface to Center of Hub inline with Sleeve"
        Resistances.append(tb.plane_wall(hub_mat, 11, 16, L_1, L_2, A_slHub))
        Resistances[14].Descr = Descr
        ##############
        # Path 15
        ##############
        Descr = "Shaft inline with Hub center to Hub/Shaft interface"
        A_sh_2 = 2 * np.pi * R_1 * hub_length
        Resistances.append(tb.plane_wall(sh_mat, 12, 13, 0, R_1, A_sh_2))
        Resistances[15].Descr = Descr
        ##############
        # Path 16
        ##############
        Descr = "Hub/Shaft interface to Center of Hub inline with Rotor Core"
        Resistances.append(tb.cylind_wall(hub_mat, 13, 14, R_1, R_rc, hub_length))
        Resistances[16].Descr = Descr
        ##############
        # Path 17
        ##############
        Descr = "Hub inline with Rotor Core to Hub inline with PM"
        Resistances.append(tb.cylind_wall(hub_mat, 14, 15, R_rc, R_pm, hub_length))
        Resistances[17].Descr = Descr
        ##############
        # Path 18
        ##############
        Descr = "Hub inline with PM to Hub inline with Sleeve "
        Resistances.append(tb.cylind_wall(hub_mat, 15, 16, R_pm, R_sl, hub_length))
        Resistances[18].Descr = Descr
        ##############
        # Path 19
        ##############
        Descr = "Shaft inline with Hub center to Shaft Out "
        Resistances.append(tb.plane_wall(sh_mat, 12, 17, L_2, L_4, A_sh))
        Resistances[19].Descr = Descr
        ##############
        # Path 20
        ##############
        Descr = "Hub inline with Rotor Core to Outer Hub Inline with Rotor Core "
        Resistances.append(tb.plane_wall(hub_mat, 14, 18, L_2, L_3, A_rcHub))
        Resistances[20].Descr = Descr
        ##############
        # Path 21
        ##############
        Descr = "Hub inline with PM to Outer Hub Inline with PM "
        Resistances.append(tb.plane_wall(hub_mat, 15, 19, L_2, L_3, A_pmHub))
        Resistances[21].Descr = Descr
        ##############
        # Path 22
        ##############
        Descr = "Hub inline with Sleeve to Outer Hub Inline with Sleeve"
        Resistances.append(tb.plane_wall(hub_mat, 16, 20, L_2, L_3, A_slHub))
        Resistances[22].Descr = Descr
        ##############
        # Path 23
        ##############
        Descr = "Outer Shaft to Air"
        A_sh_out = (L_4 - L_3) * (np.pi * R_1)
        Resistances.append(tb.shaft_conv(air_mat, 17, 0, omega, R_1, A_sh_out, u_z))
        Resistances[23].Descr = Descr
        ##############
        # Path 24
        ##############
        Descr = "Outer Hub inline with Rotor Core to Air"
        Resistances.append(tb.hub_conv(air_mat, 18, 0, omega, A_rcHub))
        Resistances[24].Descr = Descr
        ##############
        # Path 25
        ##############
        Descr = "Outer Hub inline with PM to Air"
        Resistances.append(tb.hub_conv(air_mat, 19, 0, omega, A_pmHub))
        Resistances[25].Descr = Descr
        ##############
        # Path 26
        ##############
        Descr = "Outer Hub inline with Sleeve to Air"
        Resistances.append(tb.hub_conv(air_mat, 20, 0, omega, A_slHub))
        Resistances[26].Descr = Descr
        ##############
        # Path 27
        ##############
        Descr = "Rotor Core center to Hub/RotorCore Interface"
        A_rcHub = np.pi * (R_2 ** 2 - R_1 ** 2)
        Resistances.append(tb.plane_wall(rc_mat, 3, 21, 0, L_1, A_rcHub))
        Resistances[27].Descr = Descr
        ##############
        # Path 28
        ##############
        Descr = "PM center to Hub/PM Interface"
        A_pmHub = np.pi * (R_3 ** 2 - R_4 ** 2)
        Resistances.append(tb.plane_wall(pm_mat, 5, 22, 0, L_1, A_pmHub))
        Resistances[28].Descr = Descr
        ##############
        # Path 29
        ##############
        Descr = "Sleeve center to Hub/Sleeve Interface"
        A_slHub = np.pi * (R_4 ** 2 - R_3 ** 2)
        Resistances.append(tb.plane_wall(sl_mat, 7, 23, 0, L_1, A_slHub))
        Resistances[29].Descr = Descr
        ##############
        # Path 30
        ##############
        Descr = "Shaft Center to shaft Inline with Hub center"
        A_sh = np.pi * (R_1 ** 2)
        Resistances.append(tb.plane_wall(sh_mat, 1, 24, 0, L_2, A_sh))
        Resistances[30].Descr = Descr
        ##############
        # Path 31
        ##############
        Descr = "Hub/Rotor Core interface to Center of Hub inline with Rotor Core"
        Resistances.append(tb.plane_wall(hub_mat, 21, 26, L_1, L_2, A_rcHub))
        Resistances[31].Descr = Descr
        ##############
        # Path 32
        ##############
        Descr = "Hub/PM interface to Center of Hub inline with PM"
        Resistances.append(tb.plane_wall(hub_mat, 22, 27, L_1, L_2, A_pmHub))
        Resistances[32].Descr = Descr
        ##############
        # Path 33
        ##############
        Descr = "Hub/Sleeve interface to Center of Hub inline with Sleeve"
        Resistances.append(tb.plane_wall(hub_mat, 23, 28, L_1, L_2, A_slHub))
        Resistances[33].Descr = Descr
        ##############
        # Path 34
        ##############
        Descr = "Shaft inline with Hub center to Hub/Shaft interface"
        A_sh_2 = 2 * np.pi * R_1 * hub_length
        Resistances.append(tb.plane_wall(sh_mat, 24, 25, 0, R_1, A_sh_2))
        Resistances[34].Descr = Descr
        ##############
        # Path 35
        ##############
        Descr = "Hub/Shaft interface to Center of Hub inline with Rotor Core"
        Resistances.append(tb.cylind_wall(hub_mat, 25, 26, R_1, R_rc, hub_length))
        Resistances[35].Descr = Descr
        ##############
        # Path 36
        ##############
        Descr = "Hub inline with Rotor Core to Hub inline with PM"
        Resistances.append(tb.cylind_wall(hub_mat, 26, 27, R_rc, R_pm, hub_length))
        Resistances[36].Descr = Descr
        ##############
        # Path 37
        ##############
        Descr = "Hub inline with PM to Hub inline with Sleeve "
        Resistances.append(tb.cylind_wall(hub_mat, 27, 28, R_pm, R_sl, hub_length))
        Resistances[37].Descr = Descr
        ##############
        # Path 38
        ##############
        Descr = "Shaft inline with Hub center to Shaft Out "
        Resistances.append(tb.plane_wall(sh_mat, 24, 29, L_2, L_4, A_sh))
        Resistances[38].Descr = Descr
        ##############
        # Path 39
        ##############
        Descr = "Hub inline with Rotor Core to Outer Hub Inline with Rotor Core "
        Resistances.append(tb.plane_wall(hub_mat, 26, 30, L_2, L_3, A_rcHub))
        Resistances[39].Descr = Descr
        ##############
        # Path 40
        ##############
        Descr = "Hub inline with PM to Outer Hub Inline with PM "
        Resistances.append(tb.plane_wall(hub_mat, 27, 31, L_2, L_3, A_pmHub))
        Resistances[40].Descr = Descr
        ##############
        # Path 41
        ##############
        Descr = "Hub inline with Sleeve to Outer Hub Inline with Sleeve"
        Resistances.append(tb.plane_wall(hub_mat, 28, 32, L_2, L_3, A_slHub))
        Resistances[41].Descr = Descr
        ##############
        # Path 42
        ##############
        Descr = "Outer Shaft to Air"
        A_sh_out = (L_4 - L_3) * (np.pi * R_1)
        Resistances.append(tb.shaft_conv(air_mat, 29, 0, omega, R_1, A_sh_out, u_z))
        # print(Resistances[42].resistance_value)
        Resistances[42].Descr = Descr
        ##############
        # Path 43
        ##############
        Descr = "Outer Hub inline with Rotor Core to Air"
        Resistances.append(tb.hub_conv(air_mat, 30, 0, omega, A_rcHub))
        Resistances[43].Descr = Descr
        ##############
        # Path 44
        ##############
        Descr = "Outer Hub inline with PM to Air"
        Resistances.append(tb.hub_conv(air_mat, 31, 0, omega, A_pmHub))
        Resistances[44].Descr = Descr
        ##############
        # Path 45
        ##############
        Descr = "Outer Hub inline with Sleeve to Air"
        Resistances.append(tb.hub_conv(air_mat, 32, 0, omega, A_slHub))
        Resistances[45].Descr = Descr

        return Resistances
    


#%% Airflow Analyzer

class AirflowAnalyzer:
    def analyze(self,problem):
        nlc1 = op.NonlinearConstraint(problem.magnet_temp, 0, problem.max_temp)
        const = nlc1
        sol = op.minimize(
            problem.cost, 0, tol=1e-6, constraints=const, bounds=[(0.00001, 1.0)]
        )
        #print(sol.success)
        #print(sol)
        if sol.success == True:
            results = {
                "valid": sol.success,
                "magnet Temp": problem.magnet_temp(sol.x),
                "Required Airflow": sol.x,
            }
            return results
        else:
            results = {
                "valid": sol.success,
                "magnet Temp": problem.magnet_temp(sol.x),
                "Required Airflow": sol.x,
            }

            return results


class AirflowProblem:
    def __init__(
        self,
        r_sh,
        d_ri,
        r_ro,
        d_sl,
        r_si,
        l_st,
        l_hub,
        T_ref,
        losses,
        omega,
        max_temp,
        mat_dict,
    ):
        self.r_sh = r_sh
        self.d_ri = d_ri
        self.r_ro = r_ro
        self.d_sl = d_sl
        self.r_si = r_si
        self.l_st = l_st
        self.l_hub = l_hub

        self.losses = losses
        self.T_ref = T_ref
        self.omega = omega
        self.max_temp = max_temp
        self.mat_dict=mat_dict
        self.therm_prob_def = SPM_RotorThemalProblem
        self.therm_ana = SPM_RotorThemalAnalyzer()

    def magnet_temp(self, u_z):
        prob = self.therm_prob_def(
            self.mat_dict,
            self.r_sh,
            self.d_ri,
            self.r_ro,
            self.d_sl,
            self.r_si,
            self.l_st,
            self.l_hub,
            self.T_ref,
            u_z,
            self.losses,
            self.omega,
        )
        T = self.therm_ana.analyze(prob)
        return T[5]

    def cost(self, u_z):
        return u_z


class WindageProblem:
    def __init__(
        self, Omega, R_ro, stack_length, R_st, air_gap, m_dot_air, TEMPERATURE_OF_AIR=25
    ):
        self.Omega = Omega
        self.R_ro = R_ro
        self.stack_length = stack_length
        self.R_st = R_st
        self.air_gap = air_gap
        self.m_dot_air = m_dot_air
        self.TEMPERATURE_OF_AIR = TEMPERATURE_OF_AIR


class WindageLossAnalyzer:
    def analyze(problem):
        # Omega, R_ro ,stack_length,R_st,air_gap,m_dot_air, TEMPERATURE_OF_AIR=25):

        # %Air friction loss calculation
        nu_0_Air = 13.3e-6  # ;  %[m^2/s] kinematic viscosity of air at 0
        rho_0_Air = 1.29  # ;     %[kg/m^3] Air density at 0
        Shaft = [
            problem.stack_length,  # 1;         %End position of the sections mm (Absolut)
            problem.R_ro,  # 1;         %Rotor Radius
            1,  # 0;         %Shrouded (1) or free surface (0)
            problem.air_gap,
        ]  # 0];        %Airgap in mm
        # Num_shaft_section = 1
        T_Air = (
            problem.TEMPERATURE_OF_AIR
        )  # 20:(120-20)/((SpeedMax-SpeedMin)/SpeedStep):120         #; % Air temperature []

        nu_Air = nu_0_Air * ((T_Air + 273) / (0 + 273)) ** 1.76
        rho_Air = rho_0_Air * (0 + 273) / (T_Air + 273)
        windage_loss_radial = 0

        # Calculation of the section length ...
        L = Shaft[0]  # in meter
        R = Shaft[1]  # radius of air gap
        delta = Shaft[3]  # length of air gap

        # Reynolds number
        Rey = R ** 2 * (problem.Omega) / nu_Air

        if Shaft[2] == 0:  # free running cylinder
            if Rey <= 170:
                c_W = 8.0 / Rey
            elif Rey > 170 and Rey < 4000:
                c_W = 0.616 * Rey ** (-0.5)
            else:
                c_W = 6.3e-2 * Rey ** (-0.225)
            windage_loss_radial = (
                c_W * np.pi * rho_Air * problem.Omega ** 3 * R ** 5 * (1.0 + L / R)
            )

        else:  # shrouded cylinder by air gap from <Loss measurement of a 30 kW High Speed Permanent Magnet Synchronous Machine with Active Magnetic Bearings>
            Tay = (
                R * (problem.Omega) * (delta / nu_Air) * np.sqrt(delta / R)
            )  # Taylor number
            if Rey <= 170:
                c_W = 8.0 / Rey
            elif Rey > 170 and Tay < 41.3:
                # c_W = 1.8 * Rey**(-1) * delta/R**(-0.25) * (R+delta)**2 / ((R+delta)**2 - R**2) # Ye gu's codes
                c_W = (
                    1.8 * (R / delta) ** (0.25) * (R + delta) ** 2 / (Rey * delta ** 2)
                )  # Ashad over Slack 2019/11/21
            else:
                c_W = 7e-3
            windage_loss_radial = (
                c_W * np.pi * rho_Air * problem.Omega ** 3 * problem.R_ro ** 4 * L
            )

        # end friction loss added - 05192018.yegu
        # the friction coefficients from <Rotor Design of a High-Speed Permanent Magnet Synchronous Machine rating 100,000 rpm at 10 kW>
        Rer = rho_Air * (problem.R_ro) ** 2 * problem.Omega / nu_Air
        if Rer <= 30:
            c_f = 64 / (3 * Rer)
        elif Rer > 30 and Rer < 3 * 10 ** 5:
            c_f = 3.87 * Rer ** (-0.5)
        else:
            c_f = 0.146 * Rer ** (-0.2)

        windage_loss_endFace = (
            0.5 * c_f * rho_Air * problem.Omega ** 3 * (problem.R_ro) ** 5
        )

        # Axial air flow of 0.001 kg/sec for cooling based on B. Riemer, M. Leßmann and K. Hameyer, "Rotor design of a high-speed Permanent Magnet Synchronous Machine rating 100,000 rpm at 10kW," 2010 IEEE Energy Conversion Congress and Exposition, Atlanta, GA, 2010, pp. 3978-3985.
        Q_flow = problem.m_dot_air / rho_Air
        A_delta = np.pi * (problem.R_st ** 2 - problem.R_ro ** 2)
        vm = Q_flow / A_delta
        um = 0.48 * problem.Omega * problem.R_ro
        windage_loss_axial = (
            (2 / 3)
            * np.pi
            * rho_Air
            * (problem.R_st ** 3 - (problem.R_ro) ** 3)
            * vm
            * um
            * problem.Omega
        )

        windage_loss_total = (
            windage_loss_radial + windage_loss_endFace + windage_loss_axial
        )
        return windage_loss_total
    
    
if __name__ == "__main__":
    # mat_dict=fea_config_dict
    mat_dict= {'shaft_therm_conductivity': 51.9, # W/m-k ,
               'core_therm_conductivity': 28, # W/m-k
               'magnet_therm_conductivity': 8.95, # W/m-k ,
               'sleeve_therm_conductivity': 0.71, # W/m-k,
               'air_therm_conductivity'     :.02624, #W/m-K
               'air_viscosity'              :1.562E-5, #m^2/s
               'air_cp'                     :1, #kJ/kg
               'rotor_hub_therm_conductivity':205.0}#W/m-K}

    r_sh=5E-3 # [m]
    d_m=3E-3 # [m]
    r_ro=12.5E-3 # [m]
    d_ri=r_ro-r_sh - d_m # [m]
    d_sl=1E-3 # [m]
    l_st=50E-3 # [m]
    l_hub=3E-3 # [m]
    T_ref=25 # [C]
    r_si=r_ro+d_sl+1E-3 # [m]
    omega=120E3*2*np.pi/60 # [rad/s]
    max_temp=80
    losses={'rotor_iron_loss':.001,'magnet_loss':135}
    afp=AirflowProblem(r_sh, d_ri, r_ro, d_sl, r_si, l_st, l_hub, T_ref,
                       losses, omega,max_temp, mat_dict)
    ana=AirflowAnalyzer()
    sleeve_dim=ana.analyze(afp)
    print(sleeve_dim)

