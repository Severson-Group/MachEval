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
    
    def add_study_parameters(self, study_name):

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

    
    def delete_operating_points(self):
        
        self.app = self.toolJmag.jd
        self.model = self.app.GetCurrentModel()

        self.app.SetCurrentStudy("Machine_FluxLinkage_Study")
        study = self.model.GetStudy("Machine_FluxLinkage_Study")
        # Creating circuit function and zeroing all values
        cs_name = []
        for i in range(0, len(self.phase_names)):
            cs_name.append("cs_" + self.phase_names[i]) 
            f1 = self.app.FunctionFactory().Sin(0, 0.000001, 90)
            func = self.app.FunctionFactory().Composite()
            func.AddFunction(f1)
            study.GetCircuit().GetComponent(cs_name[i]).SetFunction(func)
            self.app.GetModel(0).GetStudy(0).GetDesignTable().AddParameterVariableName("cs_%s (CurrentSource): 1 (Composite Function): Amplitude" % self.phase_names[i])

    def new_operating_point(self):

        # Creating new operating points
        self.app.GetModel(0).GetStudy(0).GetDesignTable().AddCase()
        op_pt = self.app.GetModel(0).GetStudy(0).GetDesignTable()
        
        return op_pt


    def set_phase_currents(self, op_pt, m, i, I_hat):

        # Setting current values of single current source depending on phase excitation
        op_pt.SetValue(m+1, i, I_hat)

        return I_hat


    def run_all_studies(self):

        study = self.add_study_parameters("Machine_FluxLinkage_Study")
        print("-----------------------Running JMAG...")
        study.RunAllCases()
                

    def get_flux_linkages(self, study_name):

        # Read data from output file
        linkage_files = {}
        linkages = []
        for i in range(len(self.phase_names)+1):
            linkage_files[i] = pd.read_csv(self.results_filepath + study_name + "_flux_of_fem_coil.csv", skiprows=4+len(self.phase_names), usecols=[0]+np.arange(len(self.phase_names)*i+1,len(self.phase_names)*i+len(self.phase_names)+1).tolist())
            linkages.append(linkage_files[i])

        # Find rotor angle array from time data
        zero_current_linkage = linkages[0].to_numpy()
        time = zero_current_linkage[:,0]
        rotor_angle = 360*time/(max(time) - min(time)),

        # Create current vector
        current_vector = np.full((1, len(self.phase_names)), self.rated_current, dtype=int)
        
        # Write output data of analyzer
        fea_data = {
                "phase_currents": current_vector,
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

        # Zero all Currents
        problem.delete_operating_points()

        currents = []
        op_pt = {}
        m = 0
        # Create cases for each operating point
        #for m in range(len(problem.phase_names)+1):
        #    op_pt[m] = problem.new_operating_point(m)
        #    problem.set_phase_currents(op_pt[m], problem.rated_current, m)
        while m < len(problem.phase_names):
            op_pt[m] = problem.new_operating_point()
            i = 0
            currents.append([])
            while i < len(problem.phase_names):
                if i == m:
                    currents[m].append([i])
                    currents[m][i] = problem.set_phase_currents(op_pt[m], m, i, problem.rated_current)
                else:
                    currents[m].append([i])
                    currents[m][i] = problem.set_phase_currents(op_pt[m], m, i, 0)
                i = i + 1
            m = m + 1
            
        ################################################################
        # 03. Run electromagnetic studies
        ################################################################

        problem.run_all_studies()
        
        ####################################################
        # 04. Extract Results
        ####################################################

        flux_linkages = problem.get_flux_linkages("Machine_FluxLinkage_Study") 

        return flux_linkages, currents