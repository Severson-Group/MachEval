Codebase
##########################################

In order to begin a design optimization using ``MachEval``, the end user will need to configure or write the implementation of certain classes. 

Designer
  *	``Architect``: while ``eMach`` does contain example ``Architect`` classes, oftentimes custom code will be required to match the selected free variables.
  
  *	``SettingsHandler``: Similar to the architect, this object will likely need to be adjusted to match the optimization requirements.
  
Evaluator
  *	``EvaluationStep`` s: Custom code for simple evaluations can be written directly as ``EvaluationStep`` objects. For more complicated code, the ``AnalysisStep`` object should be used with the corresponding Analyzers. 
  
    *	``ProblemDefinition``: For each ``AnalysisStep``, the user will be required to write a ``ProblemDefinition`` to convert the input state to the required Problem object.
	
    *	``PostAnalyzer``: A corresponding ``PostAnalyzer`` is required for each ``Analyzer`` used.
	
DesignSpace
  *	The user must implement the required methods as specified. This is where the objective functions are defined for the optimization.
	
Once the user has specified all of the required objects, they can be injected into the ``DesignProblem`` and utilized by the ``pygmo`` optimization code.