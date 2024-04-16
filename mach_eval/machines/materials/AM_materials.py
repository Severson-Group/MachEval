import os

Fe3Si = {
    'rotor_iron_material'              : 'Fe3Si', 
    'rotor_iron_material_density'      : 7650, # kg/m3
    'rotor_iron_youngs_modulus'        : 185E9, # Pa
    'rotor_iron_poission_ratio'        : .3, 
    'rotor_iron_shear_modulus'         : 185E9 / (2 * (1 + .3)),
    'rotor_iron_material_cost'         : 17087, # $/m3
    'rotor_iron_ironloss_a'            : 1.58,
    'rotor_iron_ironloss_b'            : 1.17,
    'rotor_iron_ironloss_Kh'           : 78.94, # W/m3
    'rotor_iron_ironloss_Ke'           : 0.0372, # W/m3
    'rotor_iron_therm_conductivity'    : 28, # W/m-k
    'rotor_iron_stacking_factor'       : 96, # percentage
    'rotor_iron_bh_file'               : os.path.dirname(__file__) + '/Fe3Si.BH',
    'alpha_Fe3Si'                      : 1.2e-5,
    }

L316 = {
    'rotor_barrier_material'             : 'L316',
    'rotor_barrier_material_density'     : 7870, # kg/m3
    'rotor_barrier_permeability'         : 1,
    'rotor_barrier_youngs_modulus'       : 206E9, #Pa
    'rotor_barrier_poission_ratio'       : .3, #[]
    'rotor_barrier_shear_modulus'        : 206E9 / (2 * (1 + .3)),
    'rotor_barrier_yield_stress'         : 500E9,
    'rotor_barrier_therm_conductivity'   : 51.9, # W/m-k  
    'alpha_L316'                         : 1.2e-5
    }