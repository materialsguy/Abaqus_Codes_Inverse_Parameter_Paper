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


def generate_static_step(number_of_steps=1):
    m = mdb.models['Model-1']
    m.StaticStep(name='Step-1', previous='Initial', maxNumInc=1000000, initialInc=0.2, minInc=1e-27, maxInc=0.2, nlgeom=ON)
    m.steps['Step-1'].setValues(initialInc=0.20, maxInc=0.70, timePeriod=number_of_steps)


def time_points(number_time_points, number_of_points_per_cycle=1, sub_steps=[0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], save_points=[499, 500, 999, 1000, 1499, 1500, ]):
    data = []
    x = 0
    save_points.append(number_time_points-1)
    save_points.append(number_time_points)
    for element in np.arange(0, number_time_points,1):
        if element < 3:
            for item in sub_steps:
                data.append((x, element+item, number_of_points_per_cycle))
                x = element+item
        elif element in save_points:
            for item in sub_steps:
                data.append((x, element+item, number_of_points_per_cycle))
                x = element+item
        else:
            for item in sub_steps:
                data.append((x, element+item, number_of_points_per_cycle))
                x = element+item
    data.append((x, number_time_points, number_of_points_per_cycle))
    data = data[1:]
    print(data)
    return tuple(data)


def create_time_points(number_time_points, sub_steps):
    points = time_points(number_time_points, sub_steps = sub_steps)
    m = mdb.models['Model-1']
    m.TimePoint(name='TimePoints-1', points=points)
    m.historyOutputRequests['H-Output-1'].setValues(timePoint='TimePoints-1')
    m.historyOutputRequests['H-Output-2'].setValues(timePoint='TimePoints-1')

    m.fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'MISES','E', 'PE', 'EE', 'U'))
    m.fieldOutputRequests['F-Output-1'].setValues(timePoint='TimePoints-1')
    del m.historyOutputRequests['H-Output-1']


def create_history_output(model='Model-2', strain_controlled = True):
    m = mdb.models[model]
    a = m.rootAssembly
    if strain_controlled:
        m.HistoryOutputRequest(createStepName='Step-1', name='H-Output-2', rebar=EXCLUDE, region=
        a.sets['point_2'], sectionPoints=DEFAULT, variables=('U1', 'U2', 'U3','RF1', 'RF2', 'RF3', 'RM1', 'RM2', 'RM3'))
    else:
        m.HistoryOutputRequest(createStepName='Step-1', name='H-Output-2', rebar=EXCLUDE, region=
        a.sets['point_2'], sectionPoints=DEFAULT, variables=('U1', 'U2', 'U3','CF1', 'CF2', 'CF3', 'CM1', 'CM2', 'CM3'))
