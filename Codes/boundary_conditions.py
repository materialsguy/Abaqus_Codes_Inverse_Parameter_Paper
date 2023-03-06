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


def create_sets_top_bottom(y_coordinate, width, thickness, foil_thickness, substrate_thickness, set_name, model_name):
    m = mdb.models[model_name]
    p = m.parts['Part-1']
    a = m.rootAssembly
    i = a.instances['Part-1-1']
    faces = i.faces.findAt(((-width/2, y_coordinate, foil_thickness/2),))
    next_foil = False
    foil_number = 1
    substrate_number_0 = 1
    substrate_number_1 = 0
    # start with thicker substrate
    z = foil_thickness + substrate_thickness[0]/2
    # next thinner substrate
    j = 2
    while z < thickness:
        faces += i.faces.findAt(((-width/2, y_coordinate, z),))
        if next_foil:
            if j % 2 == 0:
                substrate_number_1 += 1
                z = foil_thickness * foil_number + substrate_thickness[1] * (substrate_number_1 - 0.5) + substrate_thickness[0] * (substrate_number_0)
            else:
                substrate_number_0 += 1
                z = foil_thickness * foil_number + substrate_thickness[1] * (substrate_number_1) + substrate_thickness[0] * (substrate_number_0 - 0.5)
            j += 1
            next_foil = False
        else:
            foil_number += 1
            z = foil_thickness * (foil_number-0.5) + substrate_thickness[1] * substrate_number_1 + substrate_thickness[0] * substrate_number_0
            next_foil = True

    a.Set(faces=faces, name=set_name)


def create_bc_and_load(length, width, radius, notch_width, constant_line, thickness, foil_thickness, substrate_thickness, amplitude, model_name='Model-1', number_of_steps = 1, first_strain = True, strain_controlled=True):
    print("Creating boundary conditions and load")
    m = mdb.models[model_name]
    p = m.parts['Part-1']
    a = m.rootAssembly
    i = a.instances['Part-1-1']
    #create reference Point and force on point

    point=p.ReferencePoint(point=(1.0, 0.0, 0.0))
    a.Set(name='point', referencePoints=(i.referencePoints[point.id], ))
    point_2=a.ReferencePoint(point=(1.0, 100.0, 0.0))
    a.Set(name='point_2', referencePoints=(a.referencePoints[point_2.id], ))

    a.WirePolyLine(mergeType=IMPRINT, meshable=OFF, points=((a.referencePoints[point_2.id], i.referencePoints[point.id]), ))
    a.Set(edges=a.edges.getSequenceFromMask(('[#1 ]', ), ), name='Wire-1-Set-1')
    a.SectionAssignment(region=a.sets['Wire-1-Set-1'], sectionName='ConnSect-1')


    a.Set(name='point', referencePoints=(i.referencePoints[point.id], ))
    create_sets_top_bottom(0, notch_width, thickness, foil_thickness, substrate_thickness, "bottom", 'Model-1')
    create_sets_top_bottom(length, notch_width, thickness, foil_thickness, substrate_thickness, "top", 'Model-1')
    create_sets_side(length, width, radius, constant_line, thickness, substrate_thickness, foil_thickness, "side", "Model-1")


    a.regenerate()

    if first_strain:
        periodic_signal = generate_periodic_signal(-1, 1, number_of_steps)
    else:
        periodic_signal = generate_periodic_signal(1, -1, number_of_steps)

    m.TabularAmplitude(data=periodic_signal, name='Amp-1', smooth=0 , timeSpan=STEP)
    m.Equation(name='Constraint-1', terms=((1.0, 'top', 2), (-1.0, 'point', 2)))

    m.DisplacementBC(amplitude=UNSET, createStepName='Initial',
        distributionType=UNIFORM, fieldName='', localCsys=None, name='BC-1',
        region=a.sets['bottom'], u1=UNSET, u2=SET,
        u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET)

    m.DisplacementBC(amplitude=UNSET, createStepName='Initial',
        distributionType=UNIFORM, fieldName='', localCsys=None, name='BC-2',
        region=a.sets['side'], u1=SET, u2=UNSET,
        u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET)

    # create symmetry
    create_sets_symmetry(length, notch_width, constant_line, thickness, set_name = "Symmetry_set", model_name = 'Model-1')

    m.DisplacementBC(amplitude=UNSET, createStepName='Step-1',
        distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name='BC-5', region=a.sets['Symmetry_set'], u1=UNSET, u2=UNSET, u3=0.0, ur1=UNSET, ur2=UNSET, ur3=UNSET)


    if strain_controlled:
        m.DisplacementBC(amplitude=UNSET, createStepName='Step-1',
            distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name=
            'BC-4', region=a.sets['point_2'], u2=amplitude, u3 = 0)
        m.boundaryConditions['BC-4'].setValues(amplitude='Amp-1')

    else:
        amplitude = amplitude / 4 # due to used geometric symmetry!
        m.ConcentratedForce(cf2=amplitude, createStepName='Step-1', distributionType=UNIFORM, field='', localCsys=None, name='Load-1', region=a.sets['point_2'])
        m.loads['Load-1'].setValues(amplitude='Amp-1', distributionType=UNIFORM, field='')



def create_connector(elasticity = 8000000.0):
    m = mdb.models['Model-1']
    m.ConnectorSection(name='ConnSect-1', translationalType=CARTESIAN)
    m.sections['ConnSect-1'].setValues(behaviorOptions=(ConnectorElasticity(table=((elasticity, ), ), independentComponents=(),
    components=(2, )), ))
    m.sections['ConnSect-1'].behaviorOptions[0].ConnectorOptions()


def create_sets_symmetry(length, notch_width, constant_line, thickness, set_name, model_name):
    m = mdb.models[model_name]
    p = m.parts['Part-1']
    a = m.rootAssembly
    i = a.instances['Part-1-1']
    x = -notch_width/2
    y = length/2
    faces = i.faces.findAt(((x, y, thickness),))
    x = -notch_width/2
    y = constant_line/2
    faces += i.faces.findAt(((x, y, thickness),))
    a.Set(faces=faces, name=set_name)


def create_sets_side(length, width, radius, constant_line, thickness, substrate_thickness, foil_thickness, set_name, model_name):
    '''
    Creates sections and assigns materials/orientation.
    '''
    m = mdb.models[model_name]
    p = m.parts['Part-1']
    a = m.rootAssembly
    i = a.instances['Part-1-1']
    #Initialise segmentation_thickness
    next_foil = False
    # Initialise Cooridnates of Cells
    foil_number = 1
    substrate_number_0 = 0
    substrate_number_1 = 0
    x = 0
    y = constant_line/2
    #y_2 = (length - 11000 - constant_line)/2 + constant_line
    y_3 = (length)/2
    z = foil_thickness / 2

    faces = i.faces.findAt(((x, y, z),))
    #faces += i.faces.findAt(((x, y_2, z),))
    j = 1
    while z < thickness-foil_thickness:
        if next_foil:
            if j % 2 ==0:
                substrate_number_1 += 1
                z = substrate_number_0 * substrate_thickness[0] + (substrate_number_1 - 0.5) * substrate_thickness[1] + foil_number * foil_thickness
            else:
                substrate_number_0 += 1
                z = (substrate_number_0-0.5) * substrate_thickness[0] + (substrate_number_1) * substrate_thickness[1] + foil_number * foil_thickness
            j += 1
            next_foil = False
        else:
            foil_number += 1
            z = substrate_number_0 * substrate_thickness[0] + substrate_number_1 * substrate_thickness[1]+ (foil_number-0.5) * foil_thickness
            next_foil = True
        faces += i.faces.findAt(((x, y, z),))
        #faces += i.faces.findAt(((x, y_2, z),))
        faces += i.faces.findAt(((x, y_3, z),))
    a.Set(faces=faces, name=set_name)


def generate_periodic_signal(minimal_value, maximal_value, number_of_steps):
    '''
    generates data for periodic generate_periodic_signal by returning tuple of stepnumber and corresponding value
    '''
    data = []
    for element in range(number_of_steps+1):
        if element == 0:
            data.append((0,0))
        elif element % 2 == 1:
            data.append((element, maximal_value))
        else:
            data.append((element, minimal_value))
    return tuple(data)
