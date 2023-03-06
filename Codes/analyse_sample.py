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


def import_nearest_node_modul(node_module_path):
    sys.path.insert(0, node_module_path)
    from  nearestNodeModule import findNearestNode

def find_nearest_node_analysis(path, file_name, length, notch_width, constant_line, free_length, thickness, foil_thickness, substrate_thickness):
    '''
    finds nearest Nodes to specific coordinates
    '''
    session.viewports[session.currentViewportName].odbDisplay.setFrame(step='Step-1', frame=0)
    from  nearestNodeModule import findNearestNode
    node_1 = findNearestNode(xcoord=0, ycoord=length, zcoord=0, name='{}{}.odb'.format(path, file_name), instanceName='')
    node_2 = findNearestNode(xcoord=0, ycoord=constant_line, zcoord=0, name='{}{}.odb'.format(path, file_name), instanceName='')
    node_3 = findNearestNode(xcoord=-notch_width, ycoord=0, zcoord=0, name='{}{}.odb'.format(path, file_name), instanceName='')
    node_4 = findNearestNode(xcoord=0, ycoord=655, zcoord=0, name='{}{}.odb'.format(path, file_name), instanceName='')
    node_5 = findNearestNode(xcoord=0, ycoord=0, zcoord=0, name='{}{}.odb'.format(path, file_name), instanceName='')
    node_6 = findNearestNode(xcoord=0, ycoord=15000, zcoord=0, name='{}{}.odb'.format(path, file_name), instanceName='')
    node_7 = findNearestNode(xcoord=-notch_width, ycoord=constant_line, zcoord=0, name='{}{}.odb'.format(path, file_name), instanceName='')
    z_coord = thickness - foil_thickness/2 - substrate_thickness[0]/2
    node_8 = findNearestNode(xcoord=-notch_width, ycoord=constant_line, zcoord=z_coord, name='{}{}.odb'.format(path, file_name), instanceName='')
    node_9 = findNearestNode(xcoord=-notch_width, ycoord=0, zcoord=z_coord, name='{}{}.odb'.format(path, file_name), instanceName='')
    node_10 = findNearestNode(xcoord=-notch_width, ycoord=constant_line, zcoord=thickness, name='{}{}.odb'.format(path, file_name), instanceName='')
    node_11 = findNearestNode(xcoord=-notch_width, ycoord=0, zcoord=thickness, name='{}{}.odb'.format(path, file_name), instanceName='')
    nodes={"top": node_1[0], "constant_line": node_2[0], "center": node_3[0],"655": node_4[0], "down": node_5[0], "end":node_6[0], "notch":node_7[0], "foil_top" : node_8[0], "foil_down" : node_9[0], "substrate_top" : node_10[0], "substrate_down" : node_11[0]}
    return nodes


def create_paths(nodes):
    '''
    Creates the paths for the data ANALYSIS
    '''
    pth = session.Path(name='Path-1', type=NODE_LIST, expression=(('PART-1-1', (nodes["down"], nodes["top"], )), ))
    pth2 = session.Path(name='Path-2', type=NODE_LIST, expression=(('PART-1-1', (nodes["down"], nodes["constant_line"], )), ))
    pth3 = session.Path(name='Path-3', type=NODE_LIST, expression=(('PART-1-1', (nodes["down"], nodes["655"], )), ))
    pth6 = session.Path(name='Path-4', type=NODE_LIST, expression=(('PART-1-1', (nodes["down"], nodes["end"], )), ))
    pth7 = session.Path(name='Path-5', type=NODE_LIST, expression=(('PART-1-1', (nodes["center"], nodes["notch"], )), ))
    pth8 = session.Path(name='Path-6', type=NODE_LIST, expression=(('PART-1-1', (nodes["foil_down"], nodes["foil_top"], )), ))
    pth9 = session.Path(name='Path-7', type=NODE_LIST, expression=(('PART-1-1', (nodes["substrate_down"], nodes["substrate_top"], )), ))


def create_output_strain_analysis(path, number_of_frames, job_name, pths=[1,2,3,4,5,6], components={"U": ['U1', 'U2', "U3"], "PE": ["PE33", "PE22", "PE33"], "EE": ["EE22", "EE11", "EE33"]}):
    '''
    Version for timepoint extraction
    '''
    odb_name = '{}{}.odb'.format(path, job_name)
    odb= openOdb(path=odb_name)

    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    odb_view = session.viewports['Viewport: 1']

    output=[]
    keys=list(components.keys())
    print(keys)
    for pth in pths:
        pth_name = "Path-{}".format(pth)
        pth = session.paths[pth_name]
        for key in keys:
            for component in components[key]:
                for frame in np.arange(0,number_of_frames,1):
                    if key == "U":
                        odb_view.odbDisplay.setPrimaryVariable(variableLabel=key, outputPosition=NODAL, refinement=(COMPONENT, component))
                    else:
                        odb_view.odbDisplay.setPrimaryVariable(variableLabel=key, outputPosition=INTEGRATION_POINT, refinement=(COMPONENT, component))
                    odb_view.odbDisplay.setFrame(step="Step-1", frame=frame)
                    output.append(get_path_data(component, frame, pth))
                save_file(path, component, job_name, pth_name, output)
                output=[]


def get_path_data(component, frame, pth):
    num_intervals = 2

    xy=session.XYDataFromPath(name='Data_{}_frame_{}'.format(component, frame), path=pth, includeIntersections=True,
        projectOntoMesh=False, pathStyle=UNIFORM_SPACING, numIntervals=num_intervals,
        projectionTolerance=0, shape=DEFORMED, labelType=TRUE_DISTANCE,
        removeDuplicateXYPairs=True, includeAllElements=False)
    data = np.array(xy)
    return[data[-1][0], data[-1][1]]


def save_file(path, component, job_name, output_name, output):
    file_name='{}/results/{}_j_{}_{}.dat'.format(path,component, job_name, output_name)
    print("File Saved")
    np.savetxt(file_name, output)


def find_extract_force(path, file, number_of_steps, output_name="Point loads: CF2 PI: rootAssembly Node", file_extension="force"):
    from  nearestNodeModule import findNearestNode
    print(path, file)
    steps = []
    for element in np.arange(1, number_of_steps+1):
        steps.append(str(element))
    node = findNearestNode(xcoord=1, ycoord=100, zcoord=0, name='{}{}.odb'.format(path, file), instanceName='')
    o1 = session.openOdb('{}{}.odb'.format(path, file))
    session.viewports['Viewport: 1'].setValues(displayedObject=o1)
    session.linkedViewportCommands.setValues(_highlightLinkedViewports=False)
    odb = session.odbs['{}{}.odb'.format(path, file)]
    result=np.array([])
    for step in [1]:
        print(step)
        xy = xyPlot.XYDataFromHistory(odb=odb, outputVariableName='{} {} in NSET POINT_2'.format(output_name,node[0]), steps=('Step-{}'.format(step), ), suppressQuery=True, __linkedVpName__='Viewport: 1')
        y = extract(list(xy))
        data=np.array(y)
        result=np.append(result, data)
    file_name='{}/results/result_{}_{}.dat'.format(path, file, file_extension)
    np.savetxt(file_name, result)
    return len(result)


def extract(lst):
    return(list(list(zip(*lst)))[1])


def calculate_thickness(number_of_foils, foil_thickness, substrate_thickness):
    return (number_of_foils * foil_thickness + (number_of_foils/2) * substrate_thickness[0] + (number_of_foils/2-1) * substrate_thickness[1])/2


def calculate_output_points(number_of_steps, first_strain = True, number_of_substeps = 11, max = True):
    if max:
        if first_strain:
            begin = number_of_substeps
        else:
            begin = number_of_substeps * 2
    else:
        if first_strain:
            begin = number_of_substeps * 2
        else:
            begin = number_of_substeps
    return np.arange(begin, number_of_steps*number_of_substeps, number_of_substeps)


def create_field_output(path, job_name, odb, first_strain, number_of_steps, number_of_substeps):
    '''

    Writes field_output starting with the end of the first full cycle e.g. for 5 steps (2.5 cycles) and 11 sub_steps it will extract
    field output of 22, 33, 44

    '''
    nf = NumberFormat(numDigits=9, precision=0, format=ENGINEERING)
    session.fieldReportOptions.setValues(numberFormat=nf)
    #frames = calculate_output_points(number_of_steps, first_strain = first_strain, number_of_substeps = number_of_substeps)
    frames = np.arange(number_of_substeps, number_of_steps*number_of_substeps + number_of_substeps, number_of_substeps)
    print(frames)
    for frame in frames:

        session.writeFieldReport(fileName='{}/field_output/{}_mises_{}.csv'.format(path, job_name, frame), append=OFF, sortItem='Element Label', odb=odb, step=0,
        frame=frame, outputPosition=INTEGRATION_POINT, variable=(('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'), )), ), stepFrame=SPECIFY)

        session.writeFieldReport(fileName='{}/field_output/{}_S22_{}.csv'.format(path, job_name, frame), append=OFF, sortItem='Element Label', odb=odb, step=0,
        frame=frame, outputPosition=INTEGRATION_POINT, variable=(('S', INTEGRATION_POINT, ((COMPONENT, 'S22'), )), ), stepFrame=SPECIFY)

        session.writeFieldReport(fileName='{}/field_output/{}_PE22_{}.csv'.format(path, job_name, frame), append=OFF, sortItem='Element Label', odb=odb, step=0,
        frame=frame, outputPosition=INTEGRATION_POINT, variable=(('PE', INTEGRATION_POINT, ((COMPONENT, 'PE22'), )), ), stepFrame=SPECIFY)
