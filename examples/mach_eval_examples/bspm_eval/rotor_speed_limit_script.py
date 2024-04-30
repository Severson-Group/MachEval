import sys
import os

# add the directory 3 levels above this file's directory to path for module import
sys.path.append(os.path.dirname(__file__)+"/../../..")
sys.path.append(os.path.dirname(__file__))

from mach_eval.analyzers.mechanical.rotor_speed_limit import SPM_RotorSpeedLimitAnalyzer, SPM_RotorSpeedLimitProblem
    
def example():
    """Example Problem"""
    ######################################################
    # Creating the required Material Dictionary
    ######################################################
    mat_dict = {

        # Material: M19 29-gauge laminated steel
        'core_material_density': 7650,  # kg/m3
        'core_youngs_modulus': 185E9,  # Pa
        'core_poission_ratio': .3,
        'alpha_rc' : 1.2E-5,

        # Material: N40 neodymium magnets
        'magnet_material_density'    : 7450, # kg/m3
        'magnet_youngs_modulus'      : 160E9, # Pa
        'magnet_poission_ratio'      :.24,
        'alpha_pm'                   :5E-6,

        # Material: Carbon Fiber
        'sleeve_material_density'    : 1800, # kg/m3
        'sleeve_youngs_th_direction' : 125E9,  #Pa
        'sleeve_youngs_p_direction'  : 8.8E9,  #Pa
        'sleeve_poission_ratio_p'    :.015,
        'sleeve_poission_ratio_tp'   :.28,
        'alpha_sl_t'                :-4.7E-7,
        'alpha_sl_r'                :0.3E-6,

        'sleeve_max_tan_stress': 1950E6,  # Pa
        'sleeve_max_rad_stress': -100E6,  # Pa

        # Material: 1045 carbon steel
        'shaft_material_density': 7870,  # kg/m3
        'shaft_youngs_modulus': 206E9,  # Pa
        'shaft_poission_ratio': .3,  # []
        'alpha_sh' : 1.2E-5
    }

    ######################################################
    # Creating the required Material Yield Stength Dictionary
    ######################################################

    # Sources
    # Steel: https://www.matweb.com/search/DataSheet.aspx?MatGUID=e9c5392fb06542ca95dcce43149106ac
    # Magnet: https://www.matweb.com/search/DataSheet.aspx?MatGUID=b9cac0b8154f4718859da1fe3cdc3c90
    # Sleeve: https://www.matweb.com/search/datasheet.aspx?matguid=f0231febe90f4b45857f543bb3300f27
    # Shaft: https://www.matweb.com/search/DataSheet.aspx?MatGUID=b194a96080b6410ba81734b094a4537c

    mat_failure_dict = {

        # Material: M19 29-gauge laminated steel
        # Failure Mode: Yield
        'core_yield_strength': 359E6,   # Pa

        # Material: N40 neodymium magnets
        # Failure Mode: Ultimate
        'magnet_ultimate_strength': 80E6,   # Pa

        # Material: Carbon Fiber
        # Failure Mode: Ultimate
        'sleeve_ultimate_strength': 1380E6, # Pa

        # Material: 1045 carbon steel
        # Failure Mode: Yield
        'shaft_yield_strength': 405E6,  # Pa

        # Material: LOCTITE® AA 332™
        # Failure Mode: At break (Ultimate)
        'adhesive_ultimate_strength': 17.9E6,  # Pa
    }

    #####################################################################
    #Setting the machine geometry and operating conditions (NO SLEEVE)
    #####################################################################
    r_sh = 5E-3 # [m]
    d_m = 2E-3 # [m]
    r_ro = 12.5E-3 # [m]
    deltaT = 0 # [K]
    N_max = 100E3 # [RPM]
    d_sl=0 # [m]
    delta_sl=0 # [m]

#    #####################################################################
#    #Setting the machine geometry and operating conditions (W/ SLEEVE)
#    #####################################################################
#    r_sh = 5E-3 # [m]
#    d_m = 2E-3 # [m]
#    r_ro = 12.5E-3 # [m]
#    deltaT = 0 # [K]
#    N_max = 100E3 # [RPM]
#    d_sl=1E-3 # [m]
#    delta_sl=-2.4E-5 # [m]

    ######################################################
    #Creating problem and analyzer class
    ######################################################
    problem = SPM_RotorSpeedLimitProblem(r_sh, d_m, r_ro, d_sl, delta_sl, deltaT, 
                                        N_max, mat_dict, mat_failure_dict)

    analyzer = SPM_RotorSpeedLimitAnalyzer(N_step=100,node=1000)
    result = analyzer.analyze(problem)

    print(result.failure_mat)
    print(result.speed)

if __name__ == '__main__': 
    # Run this script to run the example case
    example()

