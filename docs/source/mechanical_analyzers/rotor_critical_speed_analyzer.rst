.. _rotor_critical_speed_analyzer:


Rotor Critical Speed Analyzer
##############################
This analyzer determines the first critical speed (first bending mode natural frequency) of a given cylindrical shaft.

Model Background
****************
When designing high-speed machines, one crucial design aspect the designer must consider is the critical speed of the rotor. Under rotation, if the rotating frequency 
matches or is near its critical speed (resonance frequency/natural frequency), the rotor would undergo high amplitude vibration. These high amplitudes of vibration 
could cause permanent damage to the rotor and the machine. Hence, as a designer it is crucial to determine if the rotor design can operate at a targeted operating speed.

One method to estimate the critical speed of a rotor is by modeling it as an Euler-Bernoulli beam. By doing so, analytical equations can be used to estimate where 
the critical speed would occur for a given shaft design. The equation [1]_ used to estimate the critical speed is shown below:

.. math::

   \omega_n = \beta l \sqrt{\frac{EI}{\rho AL^4}} 

where `E` is the Young's Modulus of the shaft material, `I` is the area moment of inertia of the shaft, `A` is the cross-sectional area of the shaft and `L` is the length of the shaft.
Note,  :math:`\beta l` is a numerical constant determined based on the boundary condition of the shaft under rotation. 
For a rotor shaft levitated in a bearingless machine, the boundary conditiion is typically considered as free-free, which has a numerical value of :math:`\beta l=4.7` for first critical speed. For other boundary conditions, see Figure 1 below.


Note, the numerical subscript in :math:`\beta` in figure below denotes the n-th resonance frequency/critical speed. (i.e. :math:`\beta_3l` means 3rd critical speed.) For the purpose of designing a rotor shaft, it is recommended to stay below (or even better, 20 to 30% away)
the first critical speed. 

.. figure:: ./Images/BoundaryConditionCriticalSpeed.svg
   :alt: BoundaryConditionTable_Rao 
   :align: center
   :width: 500

   Figure 1. Value of :math:`\beta l` under various boundary conditions, adopted from Figure 8.15 of [1]

Limitations
~~~~~~~~~~~~~~~~
* This analyzer assumes the cylindrical shaft as an Euler-Bernoulli beam.
* This analyzer assumes a uniform area across the entire shaft length `L`.
* This analyzer only considers the rotor shaft itself and not the attached components (ex. sleeve, magnets, etc.)
* This analyzer should only be applied to slender shafts, where the length to diameter ratio is greater than 10, `L/D` > 10 [2]_.

Additional Notes
~~~~~~~~~~~~~~~~
* If bearings are considered, the system should be considered as a 'Support-Supported' system. Though, the result may deviate by up to 30%, as the bearing stiffness is not considered [2]_.
* It is recommended that for a more accurate result, the user should perform an FEA modal analysis for the entire rotor assembly using a lumped-mass model approach to get a conservative estimate.

.. [1]  S. Rao, Mechnical Vibrations, 5th edit, Pearson, 2011.
.. [2]  Silva, T. A. N., and N. M. M. Maia. "Modelling a rotating shaft as an elastically restrained Bernoulli-Euler beam." Experimental Techniques 37 (2013): 6-13.

Input from User
**********************************
In order to define the problem class, the user must specify the geometry of the shaft as well as the material properties for the material they intended to use. The inputs are summarized in the following tables:

.. _input-dict:
.. csv-table:: Input for rotor critical speed problem
   :file: inputs_rotor_critical_speed_analyzer.csv
   :widths: 70, 70, 30
   :header-rows: 1

For the material dictionary, the following key value pairs are needed: 

.. _mat-dict:
.. csv-table:: ``material`` dictionary for rotor critical speed problem
   :file: inputs_mat_dict_rotor_critical_speed_analyzer.csv
   :widths: 70, 70, 30
   :header-rows: 1

Example Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The following example demonstrates how to initialize instances of ``RotorCriticalSpeedProblem`` and ``RotorCriticalSpeedAnalyzer``. 
Material properties for ``S45C`` medium carbon steel are used. The first code block initializes the material dictionary:

.. code-block:: python

   import eMach.mach_eval.analyzers.mechanical.rotor_critical_speed as rcs

    ######################################################
    # Create the required Shaft Material Dictionary
    ######################################################
    mat_dict = { 
        # Material: S45C Steel
        'youngs_modulus':206E9, #Pa
        'density':7870, # kg/m3
        }

The following code then specifies the shaft geometry and numerical constant :math:`\beta_{fi}`.

.. code-block:: python

    ######################################################
    # Define rotor shaft geometry and numeric constants
    ######################################################
    r_sh = 9E-3         # shaft radius
    length = 164E-3     # shaft length
    beta_l = 4.7       # free-free boundary condition numerical constant

This last code block creates a problem and analyzer object for this analyzer:

.. code-block:: python

    ######################################################
    # Define rotor critical speed problem and create instance of problem analyzer
    ######################################################
    problem = RotorCritcalSpeedProblem(r_sh,length,beta_l,mat_dict)
    analyzer = RotorCritcalSpeedAnalyzer(problem)

Output to User
***********************************

This analyzer returns a ``RotorCritcalSpeedResult`` object containing the following attributes:

.. csv-table::  Results of rotor critical speed analyzer
   :file: results_rotor_critical_speed_analyzer.csv
   :widths: 40, 100, 30
   :header-rows: 1

Use the following code to run the example analysis:

.. code-block:: python

    result = analyzer.solve()
    print(result.omega_n)

Running the example case returns the following:

.. code-block:: python

   18908.922312969735

This results indicates that the shaft design has an estimated critical speed of 18908.92 [rad/s], or 180,566 [RPM].
