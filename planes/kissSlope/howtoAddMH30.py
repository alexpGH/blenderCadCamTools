import bpy
import math
import numpy as np

#=== add scripts dir to path
import sys
import os

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

#=== end of default header
#==================================================================================================



if 0:
    #=== delete all but camera and lamp to start from a clean scene collection
    wingLib.deleteAllButNames(['outl','outl2','myWing1','myWing2'])


#block 'reduce quality'
if 0:
    coords=mh30modpk.coords('super',1.0,[0.0,0.0,0.0])
    #wingLib.foilDataGenerateReducedQuality(coords,0.0002,False) #False=don't delete the curves
    #wingLib.foilDataGenerateReducedQuality(coords,0.0004,False) #False=don't delete the curves
    wingLib.foilDataGenerateReducedQuality(coords,0.0008,False) #False=don't delete the curves
    
    
#block 'check result'
if 0:
    coords=mh30modpk.coords('full',1.0,[0.0,0.0,0.0])
    #coords=mh30modpk.coords('medium',1.0,[0.0,0.0,0.0])
    #coords=mh30modpk.coords('low',1.0,[0.0,0.0,0.0])
    wingLib.curveBezierFromPoints(coords,'testcurveFin',True,True)

#block 'export 4 xlfr5'
if 1:
    coords=mh30modpk.coords('super',1.0,[0.0,0.0,0.0])
    filename=bpy.path.abspath("//MH30pk_xlfr5.dat")
    #wingLib.foilExport(coords,'MH30pk',filename,'selig4spaces')
    wingLib.foilExport(coords,'MH30pk',filename,'xlfr54spaces')
    
