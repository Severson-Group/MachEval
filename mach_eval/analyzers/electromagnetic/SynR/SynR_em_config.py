class SynR_EM_Config:
    def __init__(self, **kwargs) -> None:
        # attributes for the number of rev and steps
        self.no_of_rev = kwargs["no_of_rev"] # number of revolutions
        self.no_of_steps = kwargs["no_of_steps"] # number steps

        self.mesh_size = kwargs["mesh_size"] # generic mesh size for overall model [mm]
        self.mesh_size_rotor = kwargs["mesh_size_rotor"] # mesh size for rotor [mm]
        self.airgap_mesh_radial_div = kwargs["airgap_mesh_radial_div"] # radial divisions of airgap mesh
        self.airgap_mesh_circum_div = kwargs["airgap_mesh_circum_div"] # circumferential divisions of airgap mesh
        self.mesh_air_region_scale = kwargs["mesh_air_region_scale"] # factor by which air region is scaled beyond machine model

        # results and paths
        self.only_table_results = kwargs["only_table_results"] # if True: no mesh or field results are extracted
        self.csv_results = kwargs["csv_results"] # data to be extracted from JMAG in csv format
        self.del_results_after_calc = kwargs["del_results_after_calc"] # Flag to delete result plot files after calculation
        self.run_folder = kwargs["run_folder"] # folder in which JMAG files will reside
        self.jmag_csv_folder = kwargs["jmag_csv_folder"] # folder in which csv files from solve are extracted to
        
        # other settings
        # set maximum iteration number of nonlinear calculation required until solution converges
        self.max_nonlinear_iterations = kwargs["max_nonlinear_iterations"] 
        self.multiple_cpus = kwargs["multiple_cpus"] # True if multiple cores are required
        self.num_cpus = kwargs["num_cpus"] # number of cpus or cores used. Only value if multiple_cpus = True
        self.jmag_scheduler = kwargs["jmag_scheduler"] # True if it is desired to schedule jobs instead of solving immediately
        self.jmag_visible = kwargs["jmag_visible"] # JMAG application visible if true
        self.scale_axial_length = kwargs["scale_axial_length"] # True: scale axial length to get the required rated torque
        self.jmag_version = kwargs["jmag_version"] # JMAG application version