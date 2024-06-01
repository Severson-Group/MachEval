import os
import pandas as pd
from time import time as clock_time

class Flux_Linkage_Problem:
    """Problem class for processing FEA flux linkages
    Attributes:
        app: application required for FEA scripting
        model: model required for FEA reference
        results_filepath: local file path where results of FEA data are stored
        phase_names: names of phases in machine
        rated_current: rated current of machine
    """

    def __init__(self, app, model, results_filepath, phase_names, rated_current):
        self.app = app
        self.model = model
        self.results_filepath = results_filepath
        self.phase_names = phase_names
        self.rated_current = rated_current

    
    def add_em_study(self, dir_csv_output_folder, study_name):

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


class Flux_Linkage_Analyzer:
    """Calcuates generates flux linkages from FEA

        Args:
            problem: object of type Flux_Linkage_Problem holding flux linkage simulation instructions
        Returns:
            fea_data: Data dictionary containing information for post-processing
        """
    
    def analyze(self, problem):
        self.app = problem.app
        self.model = problem.model
        self.phase_names = problem.phase_names
        self.rated_current = problem.rated_current
        self.results_filepath = problem.results_filepath

        ################################################################
        # 02. Create all operating points! One per phase + 0 current case
        ################################################################

        self.study_name = "Machine_FluxLinkage_Study"

        for i in range(len(self.phase_names)+1):

            # Create transient study with two time step sections
            study = problem.add_em_study(self.results_filepath, self.study_name)

            # Zero all Currents
            self.cs_names = problem.zero_currents(study)

            # Set current phase excitation
            problem.set_currents_sequence(self.rated_current, study, i, self.cs_names)

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
                if os.path.isfile(self.results_filepath + self.study_name + "_flux_of_fem_coil_phase_%s.csv" % self.phase_names[i-1]) is True:
                    os.replace(self.results_filepath + self.study_name + "_flux_of_fem_coil.csv", 
                            self.results_filepath + self.study_name + "_flux_of_fem_coil_phase_%s.csv" % self.phase_names[i-1])
                else:
                    os.rename(self.results_filepath + self.study_name + "_flux_of_fem_coil.csv", 
                            self.results_filepath + self.study_name + "_flux_of_fem_coil_phase_%s.csv" % self.phase_names[i-1])
        
        ####################################################
        # 04. Extract Results
        ####################################################

        fea_data = self.extract_results(self.results_filepath, self.study_name) 

        return fea_data


    def extract_results(self, path, study_name):

        zero_linkages = pd.read_csv(path + study_name + "_flux_of_fem_coil_0.csv", skiprows=6)
        zero_linkages = zero_linkages.to_numpy() # change csv format to readable array
        time = zero_linkages[:,0] # define x axis data as time
        rotor_angle = 360*1*time/(max(time) - min(time)),
        
        fea_data = {
                "current_peak": self.rated_current,
                "rotor_angle": rotor_angle,
                "csv_folder": path,
                "study_name": study_name,
                "name_of_phases": self.phase_names,
            }

        return fea_data