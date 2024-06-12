import os
import pandas as pd
from time import time as clock_time

class FluxLinkageJMAG_Problem:
    """Problem class for processing FEA flux linkages
    Attributes:
        toolJmag: JMAG tool required for FEA scripting
        phase_names: names of phases in machine
        rated_current: rated current of machine
    """

    def __init__(self, toolJmag, phase_names, rated_current):
        self.toolJmag = toolJmag
        self.phase_names = phase_names
        self.rated_current = rated_current
    
    def add_em_study(self, dir_csv_output_folder, study_name):

        self.app = self.toolJmag.jd
        self.model = self.app.GetCurrentModel()

        # Pre-processing
        self.model.SetName("Machine_FluxLinkage_Project")

        # Initialize JMAG application
        self.app.SetCurrentStudy(study_name)
        study = self.model.GetStudy(study_name)

        # Study properties
        study.GetStudyProperties().SetValue("ApproximateTransientAnalysis", 1)
        study.GetStudyProperties().SetValue("OutputSteadyResultAs1stStep", 0)
        study.GetStudyProperties().SetValue("ConversionType", 0)

        # True: no mesh or field results are needed
        study.GetStudyProperties().SetValue("OnlyTableResults", False)
        study.GetStudyProperties().SetValue("DirectSolverType", 1)

        # Set csv folder output
        study.GetStudyProperties().SetValue("CsvOutputPath", dir_csv_output_folder)
        study.GetStudyProperties().SetValue("CsvResultTypes", "FEMCoilFlux")

        self.app.SetCurrentStudy(study_name)

        return study

    
    def zero_currents(self, study):
        # Setting current values to zero to initialize circuit

        cs_name = []
        
        for i in range(0, len(self.phase_names)):
            cs_name.append("cs_" + self.phase_names[i]) 
            f1 = self.app.FunctionFactory().Sin(0, 0.000001, 90)
            func = self.app.FunctionFactory().Composite()
            func.AddFunction(f1)
            study.GetCircuit().GetComponent(cs_name[i]).SetFunction(func)

        return cs_name


    def set_currents_sequence(self, I, study, i, cs_names):
        
        # Setting current values of single current source
        if i == 0:
            pass
        else:
            func = self.app.FunctionFactory().Composite()
            f1 = self.app.FunctionFactory().Sin(I, 0.000001, 90)
            func.AddFunction(f1)
            study.GetCircuit().GetComponent(cs_names[i-1]).SetFunction(func)


    def run_study(self, study, toc):
            
        print("-----------------------Running JMAG...")
        study.RunAllCases()
        msg = "Time spent on %s is %g s." % (study.GetName(), clock_time() - toc)
        print(msg)

        self.app.SetCurrentStudy(0)
        self.app.GetModel(0).GetStudy(0).DeleteResult()


class FluxLinkageJMAG_Analyzer:
    """Calcuates generates flux linkages from FEA

        Args:
            problem: object of type Flux_Linkage_Problem holding flux linkage simulation instructions
        Returns:
            fea_data: Data dictionary containing information for post-processing
        """
    
    def analyze(self, problem):

        ################################################################
        # 02. Create all operating points! One per phase + 0 current case
        ################################################################

        self.study_name = "Machine_FluxLinkage_Study"
        self.results_filepath = os.path.dirname(__file__) + "/run_data/"
        # Create output folder
        if not os.path.isdir(self.results_filepath):
            os.makedirs(self.results_filepath)

        if not os.path.isdir(self.results_filepath):
            os.makedirs(self.results_filepath)

        for i in range(len(problem.phase_names)+1):

            # Create transient study with two time step sections
            study = problem.add_em_study(self.results_filepath, self.study_name)

            # Zero all Currents
            self.cs_names = problem.zero_currents(study)

            # Set current phase excitation
            problem.set_currents_sequence(problem.rated_current, study, i, self.cs_names)

            ################################################################
            # 03. Run electromagnetic studies
            ################################################################
            problem.run_study(study, clock_time())

            if i == 0:
                if os.path.isfile(self.results_filepath + self.study_name + "_flux_of_fem_coil_0.csv") is True:
                    os.replace(self.results_filepath + self.study_name + "_flux_of_fem_coil.csv", 
                            self.results_filepath + self.study_name + "_flux_of_fem_coil_0.csv")
                else:
                    os.rename(self.results_filepath + self.study_name + "_flux_of_fem_coil.csv", 
                            self.results_filepath + self.study_name + "_flux_of_fem_coil_0.csv")
            else:
                if os.path.isfile(self.results_filepath + self.study_name + "_flux_of_fem_coil_phase_%s.csv" % problem.phase_names[i-1]) is True:
                    os.replace(self.results_filepath + self.study_name + "_flux_of_fem_coil.csv", 
                            self.results_filepath + self.study_name + "_flux_of_fem_coil_phase_%s.csv" % problem.phase_names[i-1])
                else:
                    os.rename(self.results_filepath + self.study_name + "_flux_of_fem_coil.csv", 
                            self.results_filepath + self.study_name + "_flux_of_fem_coil_phase_%s.csv" % problem.phase_names[i-1])
        
        ####################################################
        # 04. Extract Results
        ####################################################

        fea_data = self.extract_results(problem, self.study_name) 

        return fea_data


    def extract_results(self, problem, study_name):

        linkage_files = {}
        linkages = []
        for i in range(len(problem.phase_names)+1):
            if i == 0:
                linkage_files[i] = pd.read_csv(self.results_filepath + study_name + "_flux_of_fem_coil_0.csv", skiprows=6)
                linkages.append(linkage_files[i])
            else:
                linkage_files[i] = pd.read_csv(self.results_filepath + study_name + "_flux_of_fem_coil_phase_%s.csv" % problem.phase_names[i-1], skiprows=6)
                linkages.append(linkage_files[i])

        zero_linkages = linkages[0].to_numpy() # change csv format to readable array
        time = zero_linkages[:,0] # define x axis data as time
        rotor_angle = 360*1*time/(max(time) - min(time)),
        
        fea_data = {
                "current_peak": problem.rated_current,
                "rotor_angle": rotor_angle,
                "linkages": linkages,
                "name_of_phases": problem.phase_names,
            }

        return fea_data