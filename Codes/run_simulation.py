 # -*- coding: mbcs -*-
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

import numpy as np
import re
import os
import math

# custom imports
from material_model import *
from meshing import *
from geometry_functions import *
from step_definition import *
from boundary_conditions import *
from analyse_sample import *


def check_and_create_paths(current_dir):
    # Create the 'simulation' folder
    simulation_folder = os.path.join(current_dir, 'simulation')
    if not os.path.exists(simulation_folder):
        os.makedirs(simulation_folder)

    # Create the 'results' folder inside the 'simulation' folder
    results_folder = os.path.join(simulation_folder, 'results')
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    results_folder = os.path.join(simulation_folder, 'field_output')
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    return simulation_folder



def create_model(path, job_name, geometry, simulation_parameters, substrate_material, run = True):
    Mdb()
    # unpack geometry parameters
    length = float(geometry["notch_length"])
    constant_line = float(geometry["constant_line"] )
    foil_thickness = float(geometry["foil_thickness"] )
    notch_width = float(geometry["notch_width"])
    free_length = float(geometry["sample_length"])
    notch_width = float(geometry["notch_width"])
    width = float(geometry["width"])
    radius = geometry["radius"]
    constant_line = float(geometry["constant_line"])
    notch_insert = float(geometry["notch_insert"])
    substrate_thicknesses = geometry["substrate_thicknesses"]
    foil_thickness = geometry["foil_thickness"]
    number_of_foils = geometry["number_of_foils"]
    thickness = (number_of_foils * foil_thickness + (number_of_foils/2) * substrate_thicknesses[0] + (number_of_foils/2-1) * substrate_thicknesses[1])/2
    print("Calculated thickness:", thickness)

    # unpack simulation parameters
    number_of_steps = simulation_parameters['number_of_steps']
    amplitude = simulation_parameters['amplitude']
    first_strain = simulation_parameters ['first_strain']
    strain_controlled = simulation_parameters['strain_controlled']
    sub_steps =  simulation_parameters['sub_steps']

    width, angle, top_line, radius = create_geometry(length, notch_width, notch_insert, thickness, radius, constant_line, width=width, calculate_radius=True, top_line_diff=free_length)

    print("Width:", width)

    length += top_line

    create_datum_planes(length, width,notch_width, radius, thickness, foil_thickness, substrate_thicknesses, constant_line, free_length = free_length)
    create_cyclic_material_model('Model-1', "Copper")
    generate_substrate_material(E1=substrate_material["E1"], E2=substrate_material["E2"], E3=substrate_material["E3"], v12=substrate_material["v12"], v23=substrate_material["v23"], v13=substrate_material["v13"], G12=substrate_material["G12"], G13=substrate_material["G13"], G23=substrate_material["G23"])

    foil_cells, substrate_cells= create_sections(length, width, notch_width, thickness, constant_line, substrate_thicknesses, foil_thickness)
    all_cells = foil_cells+substrate_cells

    generate_static_step(number_of_steps = number_of_steps)
    create_connector()
    create_bc_and_load(length, width, radius, notch_width, constant_line, thickness, foil_thickness, substrate_thicknesses, amplitude, model_name='Model-1', number_of_steps = number_of_steps, first_strain = first_strain, strain_controlled = strain_controlled)
    create_history_output(model='Model-1', strain_controlled = strain_controlled)
    create_time_points(number_of_steps, sub_steps)
    create_mesh(length, width, notch_width, notch_insert, thickness, radius, constant_line, foil_thickness, substrate_thicknesses, all_cells, angle, top_line, free_length = free_length)
    if run:
        job_name="job_{}".format(job_name)

        mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF,
            explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF,
            memory=90, memoryUnits=PERCENTAGE, model='Model-1', modelPrint=OFF,
            multiprocessingMode=DEFAULT, name=job_name, nodalOutputPrecision=SINGLE,
            numCpus=14, numDomains=14, numGPUs=0, queue=None, resultsFormat=ODB,
            scratch='', type=ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
        mdb.jobs[job_name].submit(consistencyChecking=OFF)
        mdb.jobs[job_name].waitForCompletion()


def analyse_model(path, job_name, geometry, simulation_parameters, node_module_path, field_output = True):
    length = float(geometry["notch_length"])
    notch_width = float(geometry["notch_width"])
    constant_line = float(geometry["constant_line"] )
    free_length = float(geometry["sample_length"])
    foil_thickness = geometry["foil_thickness"]
    substrate_thicknesses = geometry["substrate_thicknesses"]
    number_of_foils = geometry["number_of_foils"]

    number_of_steps = simulation_parameters['number_of_steps']
    strain_controlled = simulation_parameters["strain_controlled"]
    first_strain = simulation_parameters["first_strain"]
    sub_steps =  simulation_parameters['sub_steps']

    DIR0 = os.path.abspath(path)
    odb = session.openOdb(name = "{}.odb".format(job_name))

    import_nearest_node_modul(node_module_path)


    if strain_controlled:
        output_name = "Reaction force: RF2 PI: rootAssembly Node"
    else:
        output_name = "Point loads: CF2 PI: rootAssembly Node"

    number_of_frames = find_extract_force(path, job_name, number_of_steps, output_name = output_name,  file_extension="force")

    _ = find_extract_force(path, job_name, number_of_steps, output_name="Spatial displacement: U2 PI: rootAssembly Node", file_extension="U2")
    thickness = calculate_thickness(number_of_foils, foil_thickness, substrate_thicknesses)
    nodes = find_nearest_node_analysis(path, job_name, length, notch_width, constant_line, free_length, thickness, foil_thickness, substrate_thicknesses)
    create_paths(nodes)
    create_output_strain_analysis(path, number_of_frames, job_name, pths=[6], components={"PE":["PE33","PE22","PE33"], "EE":[ "EE22","EE11", "EE33"]})
    create_output_strain_analysis(path, number_of_frames, job_name, pths=[7], components={"S":[ "S22","S11", "S33"]})
    if field_output:
        create_field_output(path, job_name, odb, first_strain, number_of_steps, number_of_substeps = len(sub_steps))
