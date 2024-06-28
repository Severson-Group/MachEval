BSPM Machine Constants Analyzer
########################################################################

This analyzer determines the machine constants (:math:`k_t, k_f, k_\delta,` and :math:`k_\Phi`) of a given BSPM machine design.

Model Background
****************

This analyzer utilizes scripts within eMach to generate ``BSPM_Machine`` and ``BSPM_Machine_Oper_Pt`` objects for performing machine constant analysis. 
In each analysis, linear polynomials are fitted to torque (or force) data as the current (or displacement) varies in order to obtain the corresponding machine constant.

Torque Contant :math:`k_t`
------------------------------------
The machine torque constant, :math:`k_t`, can be computed using the following expression:

.. math::

   \tau = k_t i_q

where :math:`\tau` is torque and :math:`i_q` is the torque current. 

Suspension Force :math:`k_f` & Displacement Stiffness Constant :math:`k_\delta`
--------------------------------------------------------------------------------------------------
The suspension force constant, :math:`k_f`, and displacement stiffness constant, :math:`k_\delta`, can be computed using the following expression:

.. math::

   \vec{F} = k_f \vec{i_s}+k_\delta \vec{\delta}

where :math:`\vec{i_s}` is the suspension current, and :math:`\vec{\delta}` is the displacement of the rotor from the magnetic center.


Back-EMF Constant :math:`k_\Phi`
------------------------------------
The machine back-EMF constant :math:`k_\Phi` can be expressed using the following equation:

.. math::

   \vec{v_m} = k_\Phi\omega

where, :math:`\omega` is angular velocity in rad/s and :math:`\vec{v_m}` is the peak value of the induced phase voltage.

Input from User
*********************************

To define the problem class, the user needs to provide the ``BSPM_Machine`` and ``BSPM_Machine_Oper_Pt`` objects, which specify both the properties and the operating 
point of the BSPM machine intended for evaluation. For defining these objects, the user can refer to the :doc:`BSPM Design <../machines/bspm/index>` page. The inputs 
for each are summarized below:

.. csv-table::  Input for BSPM machine constants problem class
   :file: input_bspm_mach_constants_problem.csv
   :widths: 20, 20, 30
   :header-rows: 1

.. csv-table::  Input for BSPM machine constants analyzer class
   :file: input_bspm_mach_constants_analyzer.csv
   :widths: 20, 20, 30
   :header-rows: 1

Import Modules
------------------------------------
The following code imports all the required modules for performing a BSPM machine constants analysis. Users can paste this code into their scripts and execute it 
to ensure the modules can imported properly:

.. code-block:: python

    import mach_eval.analyzers.electromagnetic.bspm.machine_constant.bspm_mach_constants as bmc
    from mach_eval.machines.materials.electric_steels import Arnon5
    from mach_eval.machines.materials.jmag_library_magnets import N40H
    from mach_eval.machines.materials.miscellaneous_materials import (
        CarbonFiber,
        Steel,
        Copper,
        Hub,
        Air,
    )
    from mach_eval.machines.bspm import BSPM_Machine
    from mach_eval.machines.bspm.bspm_oper_pt import BSPM_Machine_Oper_Pt
    from mach_eval.analyzers.electromagnetic.bspm.jmag_2d_config import JMAG_2D_Config
    import os

Define and Create ``BSPM Machine`` Object
------------------------------------------

The user can paste the following sample BSPM machine design to create the ``BSPM_machine`` object:

.. code-block:: python

    #########################################################
    # CREATE BSPM MACHINE OBJECT
    #########################################################

    ################ DEFINE BP4 ################
    bspm_dimensions = {
        "alpha_st": 31.7088,   #[deg]
        "d_so": 2.02334e-3,     #[m]
        "w_st": 5.95805e-3,     #[m]
        "d_st": 18.4967e-3,     #[m]
        "d_sy": 5.81374e-3,     #[m]
        "alpha_m": 180,         #[m]
        "d_m": 3e-3,            #[m]
        "d_mp": 0,              #[m]
        "d_ri": 0.1e-3,         #[m]
        "alpha_so": 15.5,       #[deg] 
        "d_sp": 2.05e-3,        #[m]
        "r_si": 16.9737e-3,     #[m]
        "alpha_ms": 180,        #[deg]
        "d_ms": 0,              #[m]    
        "r_sh": 8.9e-3,         #[m] 
        "l_st": 25e-3,          #[m]
        "d_sl": 1e-3,           #[m]
        "delta_sl": 9.63e-5,    #[m] 
    }

    bspm_parameters = {
        "p": 1,     # number of pole pairs
        "ps": 2,    # number of suspension pole pairs
        "n_m": 1,   # 
        "Q": 6,     # number of slots
        "rated_speed": 16755.16,    #[rad/s] 
        "rated_power": 8e3,         # [W]   
        "rated_voltage": 8e3/18,   # [V_rms] 
        "rated_current": 18,      # [I_rms] 
        "name": "BP4"
    }

    bspm_materials = {
        "air_mat": Air,
        "rotor_iron_mat": Arnon5,
        "stator_iron_mat": Arnon5,
        "magnet_mat": N40H,
        "rotor_sleeve_mat": CarbonFiber,
        "coil_mat": Copper,
        "shaft_mat": Steel,
        "rotor_hub": Hub,
    }

    bspm_winding = {
        "no_of_layers": 2,
        # layer_phases is a list of lists, the number of lists = no_of_layers
        # first list corresponds to coil sides in first layer
        # second list corresponds to coil sides in second layer
        # the index indicates the slot opening corresponding to the coil side
        # string characters are used to represent the phases
        "layer_phases": [["U", "W", "V", "U", "W", "V"], 
                        ["V", "U", "W", "V", "U", "W"]],
        # layer_polarity is a list of lists, the number of lists = no_of_layers
        # first list corresponds to coil side direction in first layer
        # second list corresponds to coil side direction in second layer
        # the index indicates the slot opening corresponding to the coil side
        # + indicates coil side goes into the page, - indicates coil side comes out of page
        "layer_polarity": [["+", "-", "+", "-", "+", "-"], 
                        ["+", "-", "+", "-", "+", "-"]],
        # coil_groups are a unique property of DPNV windings
        # coil group is assigned corresponding to the 1st winding layer
        "coil_groups": ["b", "a", "b", "a", "b", "a"],
        "pitch": 1,
        "Z_q": 45,
        "Kov": 1.8,
        "Kcu": 0.5,
        # add phase current offset to know relative rotor / current angle for creating Iq
        "phase_current_offset": -30  
    }

    bp4 = BSPM_Machine(
        bspm_dimensions, bspm_parameters, bspm_materials, bspm_winding
    )

Define and Create ``BSPM_Machine_Oper_Pt`` Object
-------------------------------------------------

The users can paste the provided sample BSPM operating point code to instantiate the ``BSPM_Machine_Oper_Pt`` object:

.. code-block:: python

    #########################################################
    # DEFINE BSPM OPERATING POINT
    #########################################################
    bp4_op_pt = BSPM_Machine_Oper_Pt(
        Id=0,               # I_pu
        Iq=0.95,            # I_pu
        Ix=0,               # I_pu
        Iy=0.05,            # I_pu
        speed=160000,       # RPM
        ambient_temp=25,    # C
        rotor_temp_rise=55, # K
    )

Define and Create ``JMAG_2D_Config`` Object
-------------------------------------------

For performing simualtion in JMAG, an instance of ``JMAG_2D_Config`` must be provided (For more information, see :doc:`BSPM JMAG 2D FEA Analyzer <bspm_jmag2d_analyzer>`.) 
Users can paste the provided sample pf the JMAG configuration code to instantiate the ``JMAG_2D_Config`` object:

.. code-block:: python

    #########################################################
    # DEFINE BSPM JMAG SETTINGS
    #########################################################
    jmag_config = JMAG_2D_Config(
        no_of_rev_1TS=1,
        no_of_rev_2TS=2,
        no_of_steps_per_rev_1TS=36,
        no_of_steps_per_rev_2TS=360,
        mesh_size=2e-3,
        magnet_mesh_size=1e-3,
        airgap_mesh_radial_div=7,
        airgap_mesh_circum_div=720,
        mesh_air_region_scale=1.15,
        only_table_results=False,
        csv_results=r"Torque;Force;FEMCoilFlux;LineCurrent;TerminalVoltage;JouleLoss;TotalDisplacementAngle;JouleLoss_IronLoss;IronLoss_IronLoss;HysteresisLoss_IronLoss",
        del_results_after_calc=False,
        run_folder=os.path.dirname(__file__) + "/run_data/",
        jmag_csv_folder=os.path.dirname(__file__) + "/run_data/JMAG_csv/",
        max_nonlinear_iterations=50,
        multiple_cpus=True,
        num_cpus=4,
        jmag_scheduler=False,
        jmag_visible=False,
        jmag_version = '23',
    )

.. note::

    The step and mesh size could significantly affect the results. The user should consider making these values to be more fine. 

Define Problem and Analyzer Object
------------------------------------

Use the following code to define the problem and analyzer object:

.. code-block:: python

    #########################################################
    # DEFINE BSPM OPERATING POINTS
    #########################################################

    # List of BSPM operating points for Kf evaluation
    Kf_op_pt = [
        BSPM_Machine_Oper_Pt(
            Id=0,
            Iq=0,
            Ix=0,
            Iy=Is_pu,
            speed=160000,
            ambient_temp=25,
            rotor_temp_rise=55,
        )

        for Is_pu in np.linspace(0,1,10)
    ]

    # List of BSPM operating points for Kt evaluation
    Kt_op_pt = [
        BSPM_Machine_Oper_Pt(
            Id=0,
            Iq=Iq_pu,
            Ix=0,
            Iy=0,
            speed=160000,
            ambient_temp=25,
            rotor_temp_rise=55,
        )
        for Iq_pu in np.linspace(0,1,10)
    ]

    # List of BSPM operating points for Kphi evaluation
    Kphi_op_pt = [
        BSPM_Machine_Oper_Pt(
            Id=0,
            Iq=0,
            Ix=0,
            Iy=0,
            speed=speed,
            ambient_temp=25,
            rotor_temp_rise=55,
        )
        for speed in np.linspace(0,160000,10)
    ]

    # List of coordinates for Kdelta evaluation
    Kdelta_coords = [
        [x, y] 
        for x in np.linspace(-0.3,0.3,3) 
        for y in np.linspace(-0.3,0.3,3)
    ]

    #########################################################
    # DEFINE BSPM MACHINE CONSTANTS PROBLEM
    #########################################################
    problem = BSPMMachineConstantProblem(
        machine=bp4,
        nominal_op_pt=bp4_op_pt,
        Kf_op_pt,
        Kt_op_pt,
        Kphi_op_pt,
        Kdelta_coords
    )

    #########################################################
    # DEFINE BSPM MACHINE CONSTANTS ANALYZER
    #########################################################
    analyzer = bmc.BSPMMachineConstantAnalyzer(jmag_config)


Output to User
**********************************

The attributes of the results class can be summarized in the table below:

.. csv-table::  Results of BSPM machine constants analyzer
   :file: result_bspm_mach_constants.csv
   :widths: 30, 70, 30
   :header-rows: 1

Use the following code to run the example analysis:

.. code-block:: python

    #########################################################
    # SOLVE BSPM MACHINE CONSTANTS PROBLEM
    #########################################################
    result = analyzer.analyze(problem)
    print(f"Kf = {result.Kf}")
    print(f"Kt = {result.Kt}")
    print(f"Kdelta = {result.Kdelta}")
    print(f"Kphi = {result.Kphi}")

.. note::

    The user can install the ``tqdm`` library for a visual progress bar on your terminal when the simulations are running. 

.. note::

    Depending on the number of evaluation steps specified, a full analysis could take upwards of **one to two hours** to complete.

Running the example case returns the following:

.. code-block:: python

    1.8052182451902197
    0.01911529534112125
    6935.763575553303
    0.006449054670613704

The results indicate that the example BSPM machine design has a suspension force constant of :math:`k_f = 1.805\;  [\frac{N}{A_{pk}}]`, a torque constant of 
:math:`k_t = 0.0191 \; [\frac{Nm}{A_{pk}}]`, a displacement stiffness constant of :math:`k_\delta = 6935.76\;  [\frac{N}{m}]`, and back-EMF constant of 
:math:`k_\phi = 0.00645\;  [\frac{V_{pk}}{rad/s}]`.