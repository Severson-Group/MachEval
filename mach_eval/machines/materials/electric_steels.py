
import os

Arnon5 = {
    'core_material'              : 'AArnon55', 
    'core_material_density'      : 7650, # kg/m3
    'core_youngs_modulus'        : 185E9, # Pa
    'core_poission_ratio'        : .3, 
    'core_material_cost'         : 17087, # $/m3
    'core_ironloss_a'            : 1.58, 
    'core_ironloss_b'            : 1.17, 
    'core_ironloss_Kh'           : 78.94, # W/m3
    'core_ironloss_Ke'           : 0.0372, # W/m3
    'core_therm_conductivity'    : 28, # W/m-k
    'core_stacking_factor'       : 96, # percentage
    'core_bh_file'               : os.path.dirname(__file__) + '/Arnon5.BH',
    'alpha_rc'                   : 1.2e-5,
    }

Arnon7 = {
    'core_material'              : 'Arnon5',
    'core_material_density'      : 7650, # kg/m3
    'core_youngs_modulus'        : 185E9, # Pa
    'core_poission_ratio'        : .3,
    'core_material_cost'         : 17087, # $/m3
    'core_ironloss_a'            : 1.61551,
    'core_ironloss_b'            : 1.1144,
    'core_ironloss_Kh'           : 0.0175045 * 7650, # W/m3
    'core_ironloss_Ke'           : 1.30722e-5 * 7650, # W/m3
    'core_therm_conductivity'    : 28, # W/m-k
    'core_stacking_factor'       : 96, # percentage
    'core_bh_file'               : os.path.dirname(__file__) + '/Arnon7.BH',
    'alpha_rc'                   : 1.2e-5,
    }

M19Gauge29 = {
    'core_material'              : 'M19Gauge29',
    'core_material_density'      : 7650, # kg/m3
    'core_youngs_modulus'        : 185E9, # Pa
    'core_poission_ratio'        : .3,
    'core_material_cost'         : 17087, # $/m3
    'core_ironloss_a'            : 1.12,
    'core_ironloss_b'            : 2.10,
    'core_ironloss_Kh'           : 91.8, # W/m3
    'core_ironloss_Ke'           : 0.41, # W/m3
    'core_therm_conductivity'    : 25, # W/m-k
    'core_stacking_factor'       : 96, # percentage
    'core_bh_file'               : os.path.dirname(__file__) + '/M-19-Steel-BH-Curve-afterJMAGsmooth.BH',
    }


# os.path.abspath('')
