
Contribution Guidelines
==========================================

This guide is intended to provide guidelines for contributors to *eMach*. All contributors are expected to follow these 
guidelines with exceptions allowed only in cases as specified within the references. 

Code Style
-------------------------------------------

Using a consistent writing style makes shared code more maintainable, useful, and understandable. Contributors to *MachEval*
should follow the `Google Python Style Guidelines for naming <https://google.github.io/styleguide/pyguide.html#s3.16-naming>`_ 
and code documentation. More information on code documentation will be provided in a later section.

A brief summary of guidelines for names in Python includes:

* Avoid using excessively short names: instead, favor full words to convey meaning
* File, function, and variable names: lowercase with words separated by underscores as necessary to improve readability
* Class names: start upper case and then move to camel case
* Keep in mind that certain characters add special functionality: for instance, prepending class methods and variable names with double underscore (__) make them private to that class

Naming guidelines derived from PEP 8, used in the Google format as well, are provided below:

.. figure:: images/pep8.PNG
   :alt: Trial1 
   :align: center
   :scale: 80 %
   

Docstrings in Python
--------------------------------------------

A Python docstring is a string literal that occurs as the first statement in a module, function, class, or method definition.
Such a docstring becomes the __doc__ special attribute of that object which can be easily accessed outside the module, 
greatly improving code readability, especially in projects like *MachEval* with multiple module interdependencies.

For the purposes of *MachEval*, contriubutors are expected to follow the `Google Comments and Docstrings guidelines for code
documentation <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_. A general guideline which 
helps in greatly improving the usefulness of code documentation is to ensure that docstrings are provided for functions / 
methods and give enough information for users to write a call to any function without having to read the function’s code.

In addition to the benefits mentioned above, the Google docstrings format is also compatible with the Python Documentation 
Generator tool `Sphinx <https://www.sphinx-doc.org/en/master/>`_. As a result, maintaining the above suggested format also 
results directly in the automatic creation of pretty, well indexed documentation of the code base. These documents can be 
hosted online on the Read the Docs platform which supports real-time document updation, or on Github pages via HTML files. It 
should be noted that free document hosting with Read the Docs is supported only for public Git repositories.


Git/GitHub Usage
-------------------------------------------

All code development should occur within the Git version control environment. When code is ready to be contributed back 
to eMach, developers should open a Pull Request (PR) on GitHub which explains their contribution. 

Pull Requests and Issues
++++++++++++++++++++++++++++++++++++++++++++
The PR must close at least one issue
and all important aspects of the PR need to be described in one or more issues closed by the PR. 
PRs should not partially complete issues, and developers may need to break issues up into multiple issues to ensure that this is true. 
The developer should schedule each issue being closed onto the appropriate release by updating the issue status on the `eMach Release Planner <https://github.com/orgs/Severson-Group/projects/26/views/1>`_.

Developers should also consider which branch their PR should merge into based on eMach's Maintainer Guidelines :any:`branches-in-git`. PRs should nearly always be merged into ``develop``.

Branch Names
++++++++++++++++++++++++++++++++++++++++++++
The branch naming conventions are as follows:

- **User branch:** ``user/my_user_name/foo_bar`` -- "private" development sandbox per user
- **Feature branch:** ``feature/foo_bar`` -- shared feature development

**Hint:** Most development will occur in user branches! If multiple developers are working on an eMach feature concurrently, use a feature branch.

Contributors can expect that their user branches will not be commited to by other users---this is "private" space. On the other hand,
feature branches are "public" space and should be treated as such---at any time, another developer can commit new code onto the branch.

For example, if a big feature is being developed by several developers, a common feature branch will be created. Then, developers can
branch from this common feature branch to their own private user branch. Once they are ready to share their code back with the other
developers of the new feature, they can open a PR (or simply merge) their user branch back to the feature branch.

Valid branch name examples: ``user/johndoe/motor_tests``, ``user/janestil2/issue_652``, ``feature/regression_tests``, ``feature/tutorial_femm``

Reviewer Instructions
-------------------------------------------

PRs must be reviewed by official eMach reviewers prior to being merged into the ``develop`` branch. When making a PR, the contributor must identify and request at least one ``Level 1`` reviewer and at least one ``Level 2`` reviewer.
A list of the existing Level 1 and Level 2 reviewers can be found
`here <https://github.com/Severson-Group/eMach/blob/develop/CONTRIBUTING.md>`_.

Instructions for reviewers are now provided. Developers are encouraged to read these instructions to understand how to successfully navigate the review process.

Level 1 Review 
++++++++++++++++++++++++++++++++++++++++++++

A Level 1 reviewer is responsible for verifying that the code works and that both the code and documentation are compliant with the eMach architecture.

In conducting the review, the reviewer should perform the following steps:

1. Pull/fetch the branch being reviewed onto their device and confirm that the code runs and produces the expected results
2. Ensure the code complies with the code guidelines as described `here <https://emach.readthedocs.io/en/latest/code.html>`_
3. Ensure the documentation complies with the documentation guidelines as described `here <https://emach.readthedocs.io/en/latest/documentation.html>`_
4. Closely read of the grammar and syntax of the language to ensure that it reads clearly; if small edits are needed, consider committing them directly on to the branch
5. Evaluate if the changeset is generally compliant with the eMach architecture
6. If the reviewer has the necessary expertise, determine if the physics are correct
7. Confirm that the PR is closing one or more issues and that the issues are scheduled correctly onto the `eMach Release Planner <https://github.com/orgs/Severson-Group/projects/26/views/1>`_.
8. Confirm that the PR is merging into the correct branch (this should nearly always be ``develop``) based on how the issues are scheduled for release. 

Reviewers are expected to leave feedback directly on files within the changeset and to provide summary review comments. Level 1 reviewers are asked to copy-paste this template into their review:

.. code-block:: markdown
   
    Level 1 review summary:

    - Does the code run without error and produce the expected result? [Yes or No]
    - Does the code comply with the [code guidelines](https://emach.readthedocs.io/en/latest/code.html)? [Yes or No]
    - Does the code documentation comply with the [documentation guidelines](https://emach.readthedocs.io/en/latest/documentation.html)? [Yes or No]
    - Is the writing, grammar, and syntax correct and clear? [Yes or No]
    - Is the changeset compliant with the eMach architecture? [Yes or No]
    - Does this review consider whether this physics are accurate? [Yes or No]
    - Are the correct issues being closed (and are there no partially completed issues)? [Yes, or if No: either fix this or give the developer instructions to fix]
    - Did the reviewer change [the release schedule](https://github.com/orgs/Severson-Group/projects/26/views/1) for the issues bing closed? [If yes, briefly explain why]
    - Did the reviewer change the branch the PR is being merged into? [If yes, briefly explain why]
    - Is PR approved to Level 2? [Yes or No]

For any answers of "No," please provide an explanation.

Level 2 Review Requirements
++++++++++++++++++++++++++++++++++++++++++++

A Level 2 reviewer should be someone with expert understanding of the eMach codebase. This reviewer is expected to consider the following in their review:

1. Review the remarks from the Level 1 reviewer and determine if anything from this review requires further investigation
2. Review whether the approach, code, and documentation is compliant with the eMach architecture
3. Identify whether the physics are correct (seek outside help as needed, including from the developer)
4. Request changes/give final approval for merge.
5. Finalize the release schedule for the issues being closed on the `eMach Release Planner <https://github.com/orgs/Severson-Group/projects/26/views/1>`_.
6. Finalize the branch that the PR is being merged into.

Level 2 reviewers are asked to copy-paste this template into their review:

.. code-block:: markdown
   
    Level 2 review summary:
    
    - Does the code comply with the [code guidelines](https://emach.readthedocs.io/en/latest/code.html)? [Yes or No]
    - Does the code documentation comply with the [documentation guidelines](https://emach.readthedocs.io/en/latest/documentation.html)? [Yes or No]
    - Is the writing, grammar, and syntax correct and clear? [Yes or No]
    - Is the changeset compliant with the eMach architecture? [Yes or No]
    - Are the physics accurate? [Yes or No]
    - Did the reviewer change [the release schedule](https://github.com/orgs/Severson-Group/projects/26/views/1) for the issues bing closed? [If yes, briefly explain why]
    - Did the reviewer change the branch the PR is being merged into? [If yes, briefly explain why]
    - Level 1 re-review instructions (if revisions are requested):
    - When your PR is approved, **remember to merge via `Squash and Merge`**. Please ask if you are unsure of how to do this.
	
For any answers of "No," please provide an explanation.

Documentation
-------------------------------------------

The ``eMach`` repository uses both ``Sphinx`` and ``Read the Docs`` for generating and hosting documentation online. The link to 
this documentation is provided `here <https://emach.readthedocs.io/en/latest/>`_. This section provides guidelines on practices
contributors are expected to follow to make edits / add to ``eMach`` documentation.

How it Works
++++++++++++++++++++++++++++++++++++++++++++

All of ``eMach``'s documentation resides within the ``docs\source`` folder. This folder contains all the information required by 
``Sphinx`` to generate HTML files in the manner we desire. The workflow currently used in ``eMach`` off-loads the actual generation
of the HTML to the ``Read the Docs`` platform. Contributors, therefore, need to only make changes to the files within the 
``docs\source`` folder and ``Read the Docs`` will take care of actually running ``Sphinx`` and generating the HTML files. A push to the 
``develop`` branch acts as a trigger for ``Read the Docs`` to re-generate HTML files. Therefore, the onus falls on contributors to
ensure everything is in order, documentation wise, prior to merging changes to ``develop``.

Recommended Workflow
++++++++++++++++++++++++++++++++++++++++++++

For small changes involving just edits to existing documents and such, contributors can simply push the edits directly to ``develop``. 
For more involved changes, such as adding figures or entirely new files, it is recommended that contributors ensure everything looks
as expected locally before attempting to merge changes. The steps involved in generating HTML files locally are as follows:

1. Ensure the required Python packages are installed (they will be if you followed the pre-reqs document)
2. Navigate to the ``eMach\docs`` folder from within ``Anaconda Prompt``
3. Ensure the ``eMach`` environment is activated (run ``conda activate eMach`` if not certain)
4. Run ``make clean`` followed by ``make html`` command to generate the docs
5. Open up the ``index.html`` file from within ``docs\build\html`` folder and make sure everything is in order

``eMach`` also supports ``Sphinx`` autodocs feature, by which ``Sphinx`` is able to automatically generate documentation
from Python docstrings. Modifications to existing Python files will be reflected on ``Read the Docs`` by default. However, if new 
Python files whose docstrings should be included on ``Read the Docs`` are created, contributors will have to run a sequence of 
commands to create the .rst files required to autogenerate the Python docstring HTML file, or manually create / make modifications to 
existing .rst files themselves. For more information, please refer to this `link <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`__.