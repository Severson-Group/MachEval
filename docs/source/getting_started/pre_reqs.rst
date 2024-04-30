
Pre-requisites
============================================

This document goes through the pre-requisites required for using ``eMach`` and also guides users on setting up their systems to get
started. 

Python
---------------------------------------------

The first, and perhaps most obvious, requirement is for users to install Python on their systems. Version upwards of Python 3.8
are required for ``eMach``. Furthermore, it is highly recommended that users install Python via `Anaconda <https://www.anaconda.com/products/individual>`_ 
or `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ as the conda package manager is required in subsequent steps for
installing ``eMach`` dependencies. In general, new users of Python are recommended to install ``Anaconda`` as it comes with adittional
auxillary packages, the Spyder IDE (integrated development environment), Jupyter, and other features which make it very easy to get 
started with Python out of the box. Users who are comfortable with Python, know exactly which IDE they want to use, and wish to 
selectively install only the packages they require can go with the ``Miniconda`` installation. This `link 
<https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html#anaconda-or-miniconda>`_ succintly summarizes when
either installer should be used.

After installing ``Anaconda`` / ``Miniconda``, please ensure that paths to the Python and conda installations are included in the 
``Path`` ``User Variables`` (for Windows systems). This is required for your system to know how to run Python scripts, find relavent
Python packages, run ``conda`` commands, etc. To verify this, 

1. Search ``environment variables`` in the Windows search bar.
2. Select ``Edit the system environment variables``.
3. Now click on the ``Environment Variables...`` button from the ``System Properties`` window.
4. Within ``User Variables``, double click on ``Path``.
5. A list of directories should now be visible, among which the directories where the newly install ``python.exe`` and
   ``conda.exe`` files reside should be included. It will most likely be in the folder ``C:\Users\YourName\anaconda3`` and 
   ``C:\Users\YourName\anaconda3\Scripts`` respectively.
6. If the directories are not included, manually add them by clicking the ``New`` button and adding the above mentioned 
   installation paths to the ``Path`` ``User Variable``.

.. warning:: Be careful when modifying ``Environment Variables``. Inadvertent modifications can corrupt your system.
   

IDEs for Python
----------------------------------------------

There are a large number of IDEs available out there for Python. Spyder, which comes along with the ``Anaconda`` installation,
is most likely the path of least resistance for new users looking to quickly get started with Python. Spyder is however limited in 
a lot of ways, its biggest disadvantage being the lack of flexibility to switch between different Python interpreters (versions) 
and virtual environments. More information on Python virtual environments is provided below. Beginners will most likely not be 
employing these features of Python anytime soon and therefore can continue with Spyder. 

Other, more flexible IDEs for Python include `Visual Studio Code <https://code.visualstudio.com/>`_ and `PyCharm 
<https://www.jetbrains.com/help/pycharm/installation-guide.html>`_. These IDEs have a lot of additional features, including syntax 
highlighting, auto-formatting, debugging capabilities, git integration, seamless transfer between virtual environments etc. However, 
there is a learning curve associated with these platforms.

.. note:: It is recommended that users switch to VS Code or PyCharm as soon as they are comfortable with Python as these IDEs 
   enable much improved workflows.


Packages
------------------------------------------------

The final step involved before one can begin using ``eMach`` is to install the Python packages required by the module. Prior to 
this stage, users should clone the ``eMach`` git repository to their local system. A ``environment.yml`` file has been provided at 
the root directory of the repo. This file enables the re-creation of a Python conda environment which has been proven to work with 
``eMach``. Users are recommended to open this file and briefly glance through it to get an idea of the additional packages required
for ``eMach``, apart from what comes standard with Python.

There are 3 possible approaches users can follow to install the packages required by ``eMach``. Each of these approaches result in
a Python environment that is fully capable of working with each of ``eMach``'s different modules, however, each option does have 
its own benefits / shortcomings.

Approach 1: Create a new ``eMach`` Conda Environment
+++++++++++++++++++++++++++++++++++++++++++++++++++++

The primary purpose of the ``environment.yml`` file is to automate the creation of new conda environments. Code developers can ensure
uniformity across systems by making use this feature as each developer will be working on the same Python virtual environment. 
Beginners to Python are recommended to go through the Virtual Environments section before proceding with this 
approach. Here, the procedure by which a new ``eMach`` conda environment, having all the required dependecies and the right Python 
version, can be created is provided.

1. Launch Windows ``Command Prompt``.
2. Navigate to the location of the ``environment.yml`` file or the root of ``eMach`` git repository within ``Command Prompt``.
3. Run command ``conda env create -f environment.yml``.
4. Wait for the packages to install, enter ``y`` wherever required.
5.  Run ``rectangle_example.py`` from ``examples/mach_opt_examples`` to confirm everything is in order.



Approach 2: Global Install of Select Packages
+++++++++++++++++++++++++++++++++++++++++++++++++++++

This approach is primarily recommended for users who want to install ``eMach`` dependecies to their base Python install, but are
unable to do so with approach 3. Instead of updating the entire environment and trying to install all packages at once, each package 
provided in the ``environment.yml`` can be installed individually. The steps for doing so are:

1. Launch Windows ``Command Prompt`` 
2. Begin installing the ``pygmo`` package by running ``conda install -c conda-forge pygmo=2.18.0``
3. Try running the ``rectangle_example.py`` script from ``examples/mach_opt_examples`` folder
4. Run ``conda install pkg_name==pkg_ver`` on missing packages, if there are any

Approach 3: Global Install of All Packages
+++++++++++++++++++++++++++++++++++++++++++++++++++++

In this approach, the base Python installation is updated to include the packages required by ``eMach``. 
Users can follow the steps provided below to install ``eMach`` packages as per this approach.

1. Launch Windows ``Command Prompt``.
2. Navigate to the location of the ``environment.yml`` file or the root of ``eMach`` git repository within ``Command Prompt``.
3. Run the following command : ``conda env update --name base --file environment.yml --prune``.
4. Wait for the packages to install, enter ``y`` if required.
5. Run ``rectangle_example.py`` from ``examples/mach_opt_examples`` to confirm everything is in order.

.. warning:: ``Anaconda`` comes with a **large** Python ``base``. Updating such environments can take a very long time. If you are 
   running into this issue, consider following approach 1 or 2. 


Congratulations! You have successfully completed all installations required to start using ``eMach``. You can now try running other 
examples provided within the ``examples`` folder to confirm everything is working as expected.

.. note:: Users following approach 1 should ensure the example scripts are being executed from the right Python environment.


More Information on Using Virtual Environments with Python (Approach 1)
------------------------------------------------------------------------

This section has been added to help approach 1 users be more "Python savvy". This section gives an overview of Python virtual
environments and provides necessary links to enable users to work with virtual environments using VS code.
 
Virtual environments are isolated environments for Python projects. These environments become extremely useful when users start 
dealing with multiple Python projects, each of which might have different, and at times, confilcting dependencies. For eg: if one 
project requires ``numpy=0.13`` whereas another requires ``numpy=1.22``, we would have to re-install the desired version of ``numpy`` 
each time we switch between projects. Python overcomes this problem with virtual environments. By using different 
environments for different projects, users can not only change the packages used, but can even change the very version of Python 
employed between projects. This `link <https://realpython.com/python-virtual-environments-a-primer/>`__ provides a more detailed
explaination of Python virtual environments. 

While virtual environments themselves are IDE agnostic, using IDEs such as Visual Studio Code or PyCharm makes it far easier to 
leverage their potential than using others such as Spyder. Tips and tricks for using VS Code with virtual environments:

- Beginners should follow this `video <https://www.youtube.com/watch?v=-nh9rCzPJ20>`__ for an easy to understand, step-by-step guide of using VS Code with Python virtual environments. 
- To render any graphical elements, like graphs or charts, `run in interactive window mode <https://code.visualstudio.com/docs/python/jupyter-support-py#_using-the-python-interactive-window>`__.
- If you run into issues with running your scripts from a virtual environment even after following the above tutorial, try adding the following entries to the ``settings.json`` file.

.. code-block:: JSON

    {
      "python.terminal.activateEnvironment": true,
      "terminal.integrated.defaultProfile.windows": "Command Prompt"
    }

.. tip:: When using virtual environments, it is always a good idea to confirm which paths your scripts are looking at to run Python
   and access packages. This can be done by importing the ``sys`` package and running ``print(sys.path)``. Make sure that all paths 
   agree with your expectations based on the location of your virtual environment.
