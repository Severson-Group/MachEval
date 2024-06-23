Code Guidelines
-------------------------------------------

Developers of eMach should read this document to understand expectations of code contributed to the eMach codebase. This document outlines the 
code requirements for ``analyzers`` and ``machine_designs``. Understanding of proper Python coding practices are necessary to contribute to each 
section of ``eMach``.

Analyzers
++++++++++++++++++++++++++++++++++++++++++++

Analyzer modules should be located within ``mach_eval/analyzers`` and then placed within the appropriate subdirectory.

An analyzer module may contain multiple analyzers if they are interdependent. Each analyzer must consist of the following classes:

1. One Analyzer class
2. At least one Problem class  
3. One Results class

Analyzer Class
*******************************************

The Analyzer class is where the analysis operation is expected to occur. Aspects to consider:

1. Required functions:
    a. Each analyzer must provide an ``analyze(problem p)`` function that takes exactly one argument, a Problem object, and returns a Results object.
2. Optional initializer
    a. An initializer may be used to configure the analyzer's state in a manner that will be re-used across multiple problems. 
    b. The developer must have a compelling reason for why this information is not instead provided to the problem object.
3. Code comments 
    a. Provide short description of each argument / return value
    b. When appropriate, indicate sources or context for important physics expressions.

Problem Class
*******************************************

The purpose of the Problem class is to provide the Analyzer class the necessary information to analyze a problem. Aspects to consider:

1. Naming
    a. The problem class name should begin similarly to the analyzer class's name, i.e. ``ReallyGreatProblem`` for ``ReallyGreatAnalyzer``.
2. Code comments on user input
    a. Provide short description of each argument 
    b. Specify argument units
3. Recommended practices
    a. Provide user data through the problem class initalizer 
    b. Multiple problem classes can be defined for use with a single analyzer so that users can provide differing formats or conceptualizations of the necessary information (perhaps even requiring some computation within the problem class itself prior to being used in the analyzer).

Results Class
*******************************************

The purpose of the Results class is to encapsulate the results of the analysis operation as a single object. Aspects to consider:

1. Naming
    a. The Results class name should begin similarly to the Analyzer class's name, i.e. ``ReallyGreatResult`` for ``ReallyGreatAnalyzer``.
2. Attributes and functions:
    a. These are expected to be used to expose the analysis results to the user. 
    b. At least one attribute or function must be used.
    c. If functions are used, it is expected that these will return a value in a reasonable amount of computation time (i.e., primary computation should occur in the Analyzer's ``analyze`` function.)
3. Code comments 
    a. Provide short description of each argument (for a function) and return value (or attribute)
    b. Specify argument / return value / attribute units

Machines
++++++++++++++++++++++++++++++++++++++++++++

Machine modules should be located within ``mach_eval/machines`` and then placed within the appropriate subdirectory.

Each machine module must consist of only **one** of each of the following classes:

1. Machine Class
2. Machine Operating Point Class

Machine Class
*******************************************

The Machine class is where the machine definition is expected to occur, and it should also specify any machine variable desired in processing or post-processing. Aspects to consider:

1. Requirements to fully define machine
    a. Each machine must contain parameters (such as rotor, stator, winding, etc.) defined in the ``machine`` and ``radial_machine`` classes located in the  ``mach_eval/machines`` directory.
    b. Initialize dictionaries for ``dimensions``, ``parameters``, ``materials``, and ``winding`` to fully define a ``machine`` or ``radial_machine``.
    c. Check defined dictonaries against machine requirements, and throw error if machine is not fully defined.
2. Machine characteristic dictionaries
    a. Dictionaries must be initialized such that a ``machine`` or ``radial_machine`` is fully defined
    b. Required dictionaries are ``dimensions``, ``parameters``, ``materials``, and ``winding``
3. Checks
    a. Required to validate if machine is fully defined
    b. Check defined dictonaries against machine requirements
    c. Throws error if machine is not fully defined
4. Machine properties
    a. Required for any machine variable desired in processing or post-processing
5. Code comments on user input
    a. Provide short description of each argument for each dictionary 
    b. Specify argument units if applicable

Machine Operating Point Class
*******************************************

The purpose of the Machine Operating Point class is to define a the operating point for the machine defined in the previous step. Aspects to consider:

1. Requirements to fully define operating point
    a. Operating point definitions will differ with applications
    b. All necessary information about the operating state of the machine must be defined here
2. Code comments on user input
    a. Provide short description of each operating point argument 
    b. Specify argument units if applicable
3. Recommended practices
    a. Provide machine specific definitions in machine class 
    b. Profide only operating point specific definitions in operating point class