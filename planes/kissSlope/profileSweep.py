import bpy
import math
import numpy as np

#=== add scripts dir to path
import sys
import os

import mathutils

#=== define path of scripts dir
libDir=bpy.path.abspath("//../../scripts/") # version1: relative to current file
#libDir="/where/you/placed/blenderCadCam/scripts/" #version 2: usa an absolute path

if not libDir in sys.path:
    sys.path.append(libDir)

#=== add local dir to path
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

#print(sys.path)


#=== blender imports only once even if the file change. if we edit outsde, we need to force a reload
from importlib import reload

#=== import scripts modules
import wingLib
reload(wingLib)

#import afData_h105 as h105 
#reload(h105)

import afData_mh30ModPK as mh30modpk 
reload(mh30modpk)

import afData_h105 as h105 
reload(h105)
#=== end of default header
#==================================================================================================





if 1:
    #=== delete all but camera and lamp to start from a clean scene collection
    wingLib.deleteAllButNames(['outl','outl2','myWing1','myWing2'])



if 0:
    coords=mh30modpk.coords('full',1.0,[0.0,0.0,0.0])
    wingLib.curveBezierFromPoints(coords,'Profile1',True,True)
    

if 0:    
    coords1=h105.coords('full',1.0,[0.0,0.0,0.0])
    nPoints=len(coords1)

    coords2=mh30modpk.coords('full',1.0,[0.0,0.0,0.0])

    coords2r, leIdx2=wingLib.foildDataReduceToNpoints(coords2,nPoints)


    prof1=wingLib.curveBezierFromPoints(coords1,'Profile1',True,True)
    prof2=wingLib.curveBezierFromPoints(coords2r,'Profile2',True,True)


    

        
if 0:
    
    coords=h105.coords('full',1.0,[0.0,0.0,0.0])
    prof1=wingLib.curveBezierFromPoints(coords,'Profile1',True,True)
    n1=len(prof1.data.splines.active.bezier_points)

    coords=mh30modpk.coords('full',1.0,[0.0,0.0,0.0])
    prof2=wingLib.curveBezierFromPoints(coords,'Profile2',True,True)
    n2=len(prof2.data.splines.active.bezier_points)

    print("nPoints: "+str(n1)+", "+str(n2))


    #nPoints=55
    prof2red, _ =wingLib.bezierCurveReduceToNpoints(prof2,n1,'Profile2red') 
    
    print('Devel')
    
    
if 0:

    coords1=h105.coords('full',1.0,[0.0,0.0,0.0])
    prof1=wingLib.curveBezierFromPoints(coords1,'Profile1',True,True)
    
    bps2=prof1.data.splines.active.bezier_points
    idx=19

    print(bps2[idx].handle_left)

    #handle1 = bps2[idx].handle_left
    #knot1 = bps2[idx].co
    #knot2 = bps2[idx-1].co
    #handle2 = bps2[idx-1].handle_left

    handle1 = bps2[idx].handle_right
    knot1 = bps2[idx].co
    knot2 = bps2[idx+1].co
    handle2 = bps2[idx+1].handle_left


    nInterpol=10
    p_list = mathutils.geometry.interpolate_bezier(knot1, handle1, handle2, knot2, nInterpol)

    wingLib.curveBezierFromPoints(p_list,'ProfDebug',False,False)

    
    
if 0:
    coords1=h105.coords('full',1.0,[0.0,0.0,0.0])
    idxLe1=h105.leadingEdgeIdx('full')
    prof1=wingLib.curveBezierFromPoints(coords1,'Profile1',True,True)

    coords=mh30modpk.coords('full',1.0,[0.0,0.0,0.0])
    idxLe2=mh30modpk.leadingEdgeIdx('full')

    prof2=wingLib.curveBezierFromPoints(coords,'Profile2',True,True)

    coordSampled=wingLib.interpolateBezier2on1(prof2, prof1, idxLe2, idxLe1, 40)
    prof3=wingLib.curveBezierFromPoints(coordSampled[:],'Profile2Sampled',True,True)


    print("FUT")
    print(coords1[0])
    print(coordSampled[0])
    
    print("FUT")
    print(coords1[-1])
    print(coordSampled[-1])
    
    
    
if 1:
    
    # get coords
    f=libDir+'/AG25_resampled.dat'
    coordsAG25, leAG25=wingLib.foilImport(f,'auto')

    f=libDir+'/AG26_resampled.dat'
    coordsAG26, leAG26=wingLib.foilImport(f,'auto')
    
    f=libDir+'/AG14_resampled.dat'
    coordsAG14, leAG14=wingLib.foilImport(f,'auto')
    
    #nPoints=100
    #coordsAG25r, leIdxAg25r=wingLib.foildDataReduceToNpoints(coordsAG25,nPoints) check: do not remove tail!
    
    
    pAG25=wingLib.curveBezierFromPoints(coordsAG25,'ProfileAG25',True,True)
    pAG26=wingLib.curveBezierFromPoints(coordsAG26,'ProfileAG26',True,True)
    pAG14=wingLib.curveBezierFromPoints(coordsAG14,'ProfileAG14',True,True)
    
    coordAG14On25=wingLib.interpolateBezier2on1(pAG25, pAG14, leAG25, leAG14, 40)
    
    pAG14Morph=wingLib.curveBezierFromPoints(coordsAG14,'ProfileAG14M',True,True)
    
    #half way
    cdelta=coordAG14On25-coordsAG25
    cM1=coordsAG25+0.5*coordAG14On25
    pM=wingLib.curveBezierFromPoints(cM1,'ProfileM1',True,True)
        