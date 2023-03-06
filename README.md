# Code to “Inverse parameter determination for metal foils in multifunctional composites”
Please cite the Paper if you use the code:
**Find the Paper here** --> https://doi.org/10.1016/j.matdes.2023.111711

The code was tested on the CentOS Linux version using Abaqus 2019 .HF6. All of the Code was written in Python 2.

This Code allows the implementation of a complex, layered sample and evaluation in the commercial Abaqus software.

*Define_and_Run_Models.py*
Here your Geometrical and Simulational Parameters have to be defined. 
You can choose between a Strain controlled and Force Controlled simulation and related Strain and Force amplitude.
Graphical representation of the geometrical parameters used in the simulation:
![alt text](https://raw.githubusercontent.com/materialsguy/Abaqus_Codes_Inverse_Parameter_Paper/main/Geometry.jpeg)

The Folder “Codes” includes the following files:
*Analyse_sample.py:*
The most important aspect of this code is that it allows the creation of field output at defined time points. The code also gives examples of extracting different paths from a model.
*Boundary_conditions.py:*
Allows the implementation of periodic boundary conditions of the sample. Can implement both force and strain-controlled conditions. 
Periodic boundary conditions are implemented in a way to run effectively in Abaqus (see https://doi.org/10.1016/j.matdes.2023.111711 for details)
It implements a serial connector to the model to deal with machine stiffness in an experiment.
*geometry_functions.py:*
Implements the sample geometry, including all substrate/foil sections.
*material_model.py:*
Here your material model can be defined. Currently, published (rounded) model parameters extracted from the paper (https://doi.org/10.1016/j.matdes.2023.111711) are implemented.
*meshing.py:*
Generates a mesh for the sample, including parameters to define the seeds for foils and substrated differently.
*run_simulation.py:*
Calls all the files correctly to generate the model and the data extraction.
*step_definition.py:*
Defines the step and history output and allows the creation of time points to guarantee data analysis always at specific points (e.g. max and min amplitude)

Codes by Claus O. W. Trost 

Published under a Creative Commons license:
https://creativecommons.org/licenses/by-nc-nd/4.0/
