from abaqus import *
from caeModules import *
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
from odbAccess import*
from abaqusConstants import *

import os

###############################################################################
# If you use this code please cite:
# "Inverse parameter determination for metal foils in multifunctional composites"
# https://doi.org/10.1016/j.matdes.2023.111711

# Written by Claus O. W. Trost
# see https://www.researchgate.net/profile/Claus-Trost
################################################################################
# Define the Path to your Codes

PATH = "/home/c.trost/Documents/Abaqus_Python/Geometrien/2212 Review/Github/V2/Codes"
os.chdir(PATH)
from run_simulation import *

# Abaqus has a nearestNodeModule that needs to be imported in order to run all functions of analyse_model properly.
node_module_path = '/opt/abaqus/DassaultSystemes/SimulationServices/V6R2018x/linux_a64/code/python2.7/lib/abaqus_plugins/findNearestNode/'

# Current Substrate Material (M1-106) extracted from Fuchs et al.
# (see https://doi.org/10.1016/j.microrel.2012.04.019 for details)
# Put your own Substrate details here!
SUBSTRATE_MATERIAL = {"E1": 13120,
                    "E2": 13120,
                    "E3": 9020,
                    "v12": 0.19,
                    "v23": 0.33,
                    "v13": 0.33,
                    "G12": 3380,
                    "G13": 3300,
                    "G23": 3850}


SUB_STEPS = [0,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9] # Marks substeps in each step where an output is created.


# Defome your model here:
data = {'force_controlled_2': {'geometry':{

            'sample_length': 4000,
            'notch_length': 2000,
            'notch_width' : 1000,
            'width': 3000,
            'radius': None,
            'constant_line': 1000,
            'notch_insert': 1000,
            'substrate_thicknesses': [0.054*1000, 0.054*1000], # Allows for the implementation of two different thicknesses (Pre-Preg and Core thickness)
            'foil_thickness': 0.036*1000,
             'number_of_foils': 26,
            },
            'simulation_parameters': {
            'number_of_steps': 4, # 2 Steps == one Cycle
            'amplitude': 400*10**6, # Note that "Amplitude" can be both a Force- or a Strain-Amplitude dependung on the value for strain_controlled!
            'first_strain': True, # If first_strain the first cycle starts with an positive amplitude
            'strain_controlled': False, # Allows both strain_controlled and force_controlled simulations
            'sub_steps': SUB_STEPS}},


        'strain_controlled_2': {'geometry':{
            'sample_length': 4000,
            'notch_length': 2000,
            'notch_width': 1000,
            'width': 3000,
            'radius': None,
            'constant_line': 1000,
            'notch_insert': 1000,
            'substrate_thicknesses': [0.054*1000, 0.054*1000] ,
            'foil_thickness': 0.036*1000,
             'number_of_foils': 26,
            },
            'simulation_parameters': {
            'number_of_steps': 5,
            'amplitude': 0.0041,
            'first_strain': True,
            'strain_controlled': True,
            'sub_steps': SUB_STEPS}},}


simulations_dir = check_and_create_paths(os.getcwd())
os.chdir(simulations_dir)


keys = list(data.keys())
for key in keys:
    #Runs all samples defined in the data dictionary
    current_data = data[key]
    CURRENT_GEOMETRY = data[key]['geometry']
    CURRENT_SIMULATION_PARAMETERS = data[key]['simulation_parameters']
    JOB_NAME = key + "_" + str(CURRENT_SIMULATION_PARAMETERS["number_of_steps"])
    create_model(PATH, JOB_NAME, CURRENT_GEOMETRY, CURRENT_SIMULATION_PARAMETERS, SUBSTRATE_MATERIAL, run = True)
    analyse_model(simulations_dir+"/",  "job_{}".format(JOB_NAME), CURRENT_GEOMETRY, CURRENT_SIMULATION_PARAMETERS, node_module_path)
