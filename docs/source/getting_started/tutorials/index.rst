Tutorials
==========================================

Users introduced to ``eMach`` for the first time can find it daunting to work with. The module has 3 sub-modules, each of which
can work as standalone modules by themselves or can be interfaced with one another to get a neat implementation of what the overarching
goal of the repository is -- electric machine optimization. 

The goal of the tutorials section is to help users understand the code base one layer at a time, and gradually move to problems of
increasing difficulty with each example.  First, tutorials for individual ``submodules`` are provided after which examples involving
interfaces between multiple ``eMach`` functions are discussed. At the end of each tutorial, users are expected to understand how
to use the different functionalities of ``eMach`` and understand what is happening under the hood to a certain extent as well.
All tutorials have been written in a manner that assumes users treat the ``eMach`` repo as a Python package and ``import`` into 
their own custom scripts for using its functionalities.

+---------------+----------------------------------------------------------------------------------------+--------------------------------------------------------------+
| Module        | Tutorial Name                                                                          | Goal                                                         |
+===============+========================================================================================+==============================================================+
| ``mach_cad``  | :doc:`Making an Electric Machine using eMach <make_electric_machine_tutorial/index>`   | Familarize with ``mach_cad`` classes and capabilities        |
+---------------+----------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``mach_eval`` | :doc:`Analytical Machine Design Tutorial <analytical_machine_des_tutorial/index>`      | Familarize with ``mach_eval`` classes and protocols          |
+               +----------------------------------------------------------------------------------------+--------------------------------------------------------------+
|               | :doc:`BSPM Evaluation Tutorial <bspm_eval_tutorial/index>`                             | Multi-physics evaluation of BSPM designs                     |
+---------------+----------------------------------------------------------------------------------------+--------------------------------------------------------------+
| ``mach_opt``  | :doc:`Rectangle Optimization Tutorial <rectangle_tutorial/index>`                      | Run a basic optimization using ``mach_opt``                  |
+               +----------------------------------------------------------------------------------------+--------------------------------------------------------------+
|               | :doc:`Analytical Machine Optimization Tutorial <analytical_machine_opt_tutorial/index>`| Use ``mach_eval`` and ``mach_opt`` together for optimization |
+               +----------------------------------------------------------------------------------------+--------------------------------------------------------------+
|               | :doc:`BSPM Optimization Tutorial <bspm_opti_tutorial/index>`                           | Run multi-objective, multi-physics BSPM optimization         |
+---------------+----------------------------------------------------------------------------------------+--------------------------------------------------------------+


.. toctree::
    :hidden:
    :numbered:

    Rectangle Optimization <rectangle_tutorial/index>
    Analytical Machine Design <analytical_machine_des_tutorial/index>
    Analytical Machine Optimization <analytical_machine_opt_tutorial/index>
    Making an Electric Machine using eMach <make_electric_machine_tutorial/index>
    BSPM Evaluation <bspm_eval_tutorial/index>
    BSPM Optimization <bspm_opti_tutorial/index>

