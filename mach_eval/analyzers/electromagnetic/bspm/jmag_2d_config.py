class JMAG_2D_Config:
    def __init__(self, **kwargs) -> None:
        # attributes for rev and steps per rev
        self.no_of_rev_1TS = kwargs["no_of_rev_1TS"] # number of revolutions for 1st time step
        self.no_of_rev_2TS = kwargs["no_of_rev_2TS"] # number of revolutions for 2nd time step
        self.no_of_steps_per_rev_1TS = kwargs["no_of_steps_per_rev_1TS"] # number steps per rev for 1st time step
        self.no_of_steps_per_rev_2TS = kwargs["no_of_steps_per_rev_2TS"] # number steps per rev for 2nd time step

        # mesh attributes in meters
        self.mesh_size = kwargs["mesh_size"] # generic mesh size for overall model
        self.magnet_mesh_size = kwargs["magnet_mesh_size"] # mesh size for permanent magnets
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
        self.jmag_version = kwargs["jmag_version"] # JMAG application version
