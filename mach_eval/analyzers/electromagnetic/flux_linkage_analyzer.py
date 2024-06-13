import os
import pandas as pd
import numpy as np
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
    
    def add_em_study(self, study_name):

        self.app = self.toolJmag.jd
        self.model = self.app.GetCurrentModel()

        # Pre-processing
        self.model.SetName("Machine_FluxLinkage_Project")

        # Initialize JMAG application
        self.app.SetCurrentStudy(study_name)
        study = self.model.GetStudy(study_name)

        # Set csv folder output
        self.results_filepath = os.path.dirname(__file__) + "/run_data/"

        # Create output folder
        if not os.path.isdir(self.results_filepath):
            os.makedirs(self.results_filepath)

        # Create csv output file loction
        study.GetStudyProperties().SetValue("CsvOutputPath", self.results_filepath)
        study.GetStudyProperties().SetValue("CsvResultTypes", "FEMCoilFlux")

        self.app.SetCurrentStudy(study_name)

        return study

    
    def del_op_pts(self, study):
        
        # Creating circuit function and zeroing all values
        cs_name = []
        for i in range(0, len(self.phase_names)):
            cs_name.append("cs_" + self.phase_names[i]) 
            f1 = self.app.FunctionFactory().Sin(0, 0.000001, 90)
            func = self.app.FunctionFactory().Composite()
            func.AddFunction(f1)
            study.GetCircuit().GetComponent(cs_name[i]).SetFunction(func)
            self.app.GetModel(0).GetStudy(0).GetDesignTable().AddParameterVariableName("cs_%s (CurrentSource): 1 (Composite Function): Amplitude" % self.phase_names[i])
            self.app.GetModel(0).GetStudy(0).GetDesignTable().AddCase()
            self.app.GetModel(0).GetStudy(0).GetDesignTable().SetValue(0, i, 0)

    def new_op_pt(self, I_hat, i):

        # Setting current values of single current source depending on phase excitation
        if i == 0:
            pass
        else:
            self.app.GetModel(0).GetStudy(0).GetDesignTable().SetValue(i, i-1, I_hat)


    def run_all_studies(self, study, toc):

        print("-----------------------Running JMAG...")
        study.RunAllCases()
        msg = "Time spent on %s is %g s." % (study.GetName(), clock_time() - toc)
        print(msg)
                

    def extract_results(self, study_name):

        # Read data from output file
        linkage_files = {}
        linkages = []
        for i in range(len(self.phase_names)+1):
            linkage_files[i] = pd.read_csv(self.results_filepath + study_name + "_flux_of_fem_coil.csv", skiprows=6+len(self.phase_names), usecols=[0]+np.arange(len(self.phase_names)*i+1,len(self.phase_names)*i+len(self.phase_names)+1).tolist())
            linkages.append(linkage_files[i])

        # Find rotor angle array from time data
        zero_linkages = linkages[0].to_numpy()
        time = zero_linkages[:,0]
        rotor_angle = 360*time/(max(time) - min(time)),
        
        # Write output data of analyzer
        fea_data = {
                "current_peak": self.rated_current,
                "rotor_angle": rotor_angle,
                "linkages": linkages,
                "name_of_phases": self.phase_names,
            }

        return fea_data


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

        # Add necessary FEA definitions & parameters based on FEA tool
        self.study_name = "Machine_FluxLinkage_Study"
        study = problem.add_em_study(self.study_name)

        # Zero all Currents
        problem.del_op_pts(study)

        # Create cases for each operating point
        for m in range(len(problem.phase_names)+1):
            problem.new_op_pt(problem.rated_current, m)

        ################################################################
        # 03. Run electromagnetic studies
        ################################################################

        problem.run_all_studies(study, clock_time())
        
        ####################################################
        # 04. Extract Results
        ####################################################

        fea_data = problem.extract_results(self.study_name) 

        return fea_data