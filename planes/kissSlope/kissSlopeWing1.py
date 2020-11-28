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

import afData_h105 as h105 
reload(h105)

import afData_mh30ModPK as mh30modpk 
reload(mh30modpk)




#===================================================================================================
#=== 
#===================================================================================================


if 1:
    #=== delete all but camera and lamp to start from a clean scene collection
    wingLib.deleteAllButNames(['outl','outl2','myWing1','myWing2'])



#
if 1:


    #=============================================================
    #example wing
    #=============================================================

    #=== basic geometry
    foilwidth=1.6
    chordlength=0.204

    a=foilwidth/2.0
    b=chordlength/2.0
    nSec=41*2
    
    #--- sickle params
    #the leading edge is shifted backwards (to negative y) starting bejond a certain distance away from the center by x⁻p
    p=4 #exponent for shift
    dyMax=(b)*2/3*1.5 #how far ist the outermost point (the wingtip) shifted
    dyMax=0.1*(b)*2/3*1.5 #how far ist the outermost point (the wingtip) shifted

    xFactStart=1.0#0.8 #shift is x^p fitted from beyond xFactStart*100%. e.g. 0.8 means that only the outer 20% of points are shifted 



    #shellthickness
    #thickness=1.0

    #=== set 2d profile to be used (gives us a function reference used later)
    func4coords=mh30modpk.coords #h105.coords
    quality='medium'    


    # get basic ellipse arc points in 1st and 2nd quadrant (the unshifted leading edge) and chordlength
    x,y=wingLib.ellipseParamV(a,b,nSec)
    ch=np.multiply(y,2.0)#


    # we shift the leading edge to get the sickle shape  -> get shifted leading edge
    #
    ysh=wingLib.elipticShift(x,y, 0.008, 0.999,-1.0)
    #ysh=wingLib.elipticShift(x,y, 0.06, 0.999,-1.0) #less sweep back
    
    # we shift the leading edge to get the sickle shape  -> get shifted leading edge
    ysh=wingLib.powerShift(x,ysh, p, 0.06, 0.28) 
    #ysh=wingLib.powerShift(x,ysh, p, 0.08, 0.28) #less sweep back

    #placeSections(x,ysh,ch)
    sectionNames=wingLib.placeSectionsMinLimited(x,ysh,ch,0.001,func4coords,quality)

if 1:

    wingLib.bridgeListOfEdgeLoopsCloseOuterWithFace(sectionNames,'myWing')
    
    #shift to origin
    bpy.context.object.location[1] = -chordlength/2.0
    bpy.context.object.location[2] = 0.0

