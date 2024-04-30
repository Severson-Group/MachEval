.. _rotor_speed_analyzer:


SPM Rotor Speed Analyzer
##############################

This analyzer determines the failure speed of a surface-mounted permanent magnet (SPM) rotor design.  

Model Background
****************

This analyzer utilizes the **SPM Rotor Structural Analyzer** to calculate the rotor's internal stresses over a specified range of rotational speeds. From this, the analyzer determines whether 
the rotor will fail structurally using either maximum shear stress theory (MSST) or von Mises failure criterion based on the rotor material as follows:

* von Mises is used for ductile materials, such as rotor shafts and rotor laminations
* MSST is used for brittle materials [#]_ , such as adhesives and permanent magnets.

Detailed descriptions of the **SPM Rotor Structural Analyzer** can be found on the analyzer page 
`here <https://emach.readthedocs.io/en/latest/mechanical_analyzers/SPM_structural_analyzer.html#inputs-from-user>`_.

.. [#]  Ideally, for brittle materials, Mohr–Coulomb theory should be used in determining failure. However, due to the lack of material data avaliable, MSST is used instead.

Input from User
**********************************

The SPM rotor speed problem class requires the dimensions of the rotor shaft, the rotor material dictionary ``mat_dict``, the maximum evaluated speed in RPM 
``N_max``, and the material failure dictionary ``mat_failure_dict``. For the required rotor shaft dimensions and rotor material dictionary ``mat_dict``, please refer 
to the `Input from User  <https://emach.readthedocs.io/en/latest/mechanical_analyzers/SPM_structural_analyzer.html>`_ section in the **SPM Rotor Structural Analyzer** 
documentation page.

For the material failure strength dictionary ``mat_failure_dict``, the following key value pairs are needed. Notice that ductile materials require yield strength 
while brittle materials require ultimate strength for failure criterion. The main table containing the necessary input variables can be seen in the inputs section of 
the **SPM Rotor Structural Analyzer**, found `here <https://emach.readthedocs.io/en/latest/mechanical_analyzers/SPM_structural_analyzer.html#inputs-from-user>`_. The 
additional parameters necessary for the yield and ultimate strengths can be found in the table below:

.. _mat-failure-dict:
.. csv-table:: ``mat_failure_dict`` input to SPM rotor speed limit problem
   :file: inputs_mat_failure_dict_rotor_speed_limit.csv
   :widths: 70, 70, 30
   :header-rows: 1

Additionally, the user must provide information to this analyzer's initializer, as indicated in the table below:

.. _mat-failure-dict:
.. csv-table:: input to SPM rotor speed limit analyzer
   :file: inputs_rotor_speed_limit_analyzer.csv
   :widths: 70, 70, 30
   :header-rows: 1


The analyzer runs through the code at incremental speed increases (``N_step``) to determine the failure speed and material. Since this analyzer only provides an estimate of RPM failure speed, the user is advised to use a coarse ``N_step`` value (such as 1000 RPM) to speed up the analysis. 
For the ``node`` value, the user can also adjust accordingly based on their machine rotor size. In addition, the user should consider implementating a factor of safety 
for the machine speed limit in their design.

The following code demonstrates how to initialize the ``SPM_RotorSpeedLimitProblem`` class. The values used by the ``mat_dict`` are representative of typical values 
used by this analyzer. This assumes 1045 carbon steel for the rotor shaft, M19 29-gauge laminated steel for the rotor core, N40 neodymium magnets, and carbon fiber 
for the sleeve.

.. code-block:: python

   import numpy as np
   from matplotlib import pyplot as plt
   import eMach.mach_eval.analyzers.mechanical.rotor_speed_limit as rsl
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

Example with Rotor Sleeve
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The following code provides an example of a rotor without a rotor sleeve:

.. code-block:: python

   ######################################################
   #Setting the machine geometry and operating conditions
   ######################################################
   r_sh = 5E-3 # [m]
   d_m = 2E-3 # [m]
   r_ro = 12.5E-3 # [m]
   deltaT = 0 # [K]
   N_max = 100E3 # [RPM]
   d_sl=1E-3 # [m]
   delta_sl=-2.4E-5 # [m]

   ######################################################
   #Creating problem
   ######################################################
   problem = rsl.SPM_RotorSpeedLimitProblem(r_sh, d_m, r_ro, d_sl, delta_sl, deltaT, 
                                        N_max, mat_dict, mat_failure_dict)

   ######################################################
   #Creating analyzer class
   ######################################################
   analyzer = rsl.SPM_RotorSpeedLimitAnalyzer(N_step=100,node=1000)


Example with No Rotor Sleeve
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To analyze a rotor with no sleeve, a simple set of ``d_sl``, ``delta_sl``, and ``deltaT`` are required when creating the problem. This is shown in the following code:

.. code-block:: python

   ######################################################
   #Setting the machine geometry and operating conditions
   ######################################################
   r_sh = 5E-3 # [m]
   d_m = 2E-3 # [m]
   r_ro = 12.5E-3 # [m]
   deltaT = 0 # [K]
   N_max = 100E3 # [RPM]
   d_sl=0 # [m]
   delta_sl=0 # [m]

   ######################################################
   #Creating problem
   ######################################################
   problem = rsl.SPM_RotorSpeedLimitProblem(r_sh, d_m, r_ro, d_sl, delta_sl, deltaT, 
                                        N_max, mat_dict, mat_failure_dict)

   ######################################################
   #Creating analyzer class
   ######################################################
   analyzer = rsl.SPM_RotorSpeedLimitAnalyzer(N_step=100,node=1000)


Output to User
***********************************

The attributes of the results class can be summarized in the table below:

.. csv-table::  results of SPM rotor speed limit analyzer
   :file: results_SPM_rotor_speed_limit_analyzer.csv
   :widths: 70, 70, 30
   :header-rows: 1

Use the following code to run the aforementioned example analysis:

.. code-block:: python

   result = analyzer.analyze(problem)
   print(result.failure_mat)
   print(result.speed)

When a certain material in the rotor reaches the failure criterion, the script will break out of the loop and return an instance of the results class with the attributes
diagrammed in the table above. Within the results class, ``failure_mat`` is the failure material (type: str) and ``speed`` is the failure speed (type: float).

Example with Rotor Sleeve
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Running the example case with a rotor sleeve returns the following:

.. code-block:: python

   None
   None

indicating no failure is found in speeds tested below the maximum speed ``N_max`` given by the user.


Example with No Rotor Sleeve
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Running the example case with no rotor sleeve returns the following:

.. code-block:: python

   'Adhesive'
   77700.0

indicating a failure with the adhesive at 77700 RPM.