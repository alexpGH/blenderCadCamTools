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
    chAdditive=0.06             #we add this additive as constant to the chordlength to generate an (towrds tip) increasing over-elliptic ch
    chordlength=0.17

    #=== ellipse parameters
    a=foilwidth/2.0
    b=(chordlength-chAdditive)/2.0
    nSec=41*2


    #shellthickness
    #thickness=1.0

    #=== set 2d profile to be used (gives us a function reference used later)
    func4coords=mh30modpk.coords #h105.coords
    quality='medium'    


    # get basic ellipse arc points in 1st and 2nd quadrant (the unshifted leading edge) and chordlength
    x,y=wingLib.ellipseParamV(a,b,nSec)
    ch=np.multiply(y,2.0)#



    #plot Re(span)
    if 0:
        v=7.68# determined from stall velocity, see e.g. https://alexpgh.github.io/foss-toolchain-mpcnc/blenderKissSlope/#wing-loading-and-re
        v2=9.23
        
        #v3=15.0
        #v4=30.0
        #v5=45.0
                
        nu=1.52E-05
        outFile=bpy.path.abspath("//Fig_ReSpan_fast.png")
        Re=[]
        Re.append(np.multiply(ch,v/nu))
        Re.append(np.multiply(ch,v2/nu))
        #Re.append(np.multiply(ch,v3/nu))
        #Re.append(np.multiply(ch,v4/nu))
        #Re.append(np.multiply(ch,v5/nu))
        numpy_array = np.array(Re)
        transpose = numpy_array.T

        #legend=[str(v)+' m/s', str(v2), str(v3),str(v4),str(v5)]
        legend=[]
        #n=int(len(Re)/2)+1
        n=int(transpose.shape[0]/2)+1
        
        #import ipdb
        #ipdb.set_trace()
        #ipdb.set_trace(context=5)

        #wingLib.plotArray(x[0:n],Re[0:n],'Re(span)',outFile)
        #wingLib.plotArray(x,Re,'Re(span)',outFile)
        wingLib.plotArray(x[0:n],transpose[0:n,:],'Re(span)', legend, outFile)

        
    #=== leading edge shift definition
    #    we shift the leading edge to get the sickle shape  -> get shifted leading edge
    LeShiftL=[]
    LeShiftL.append(wingLib.LeShift('elliptic',0.008, 0.999,-1.0,foilwidth/2.0))
    LeShiftL.append(wingLib.LeShift('power',0.06, 0.28,1.0 ,foilwidth/2.0, 4))


    #LeShiftL.append(wingLib.LeShift('elliptic',0.06, 0.999,-1.0))
    #LeShiftL.append(wingLib.LeShift('power',, 0.08, 0.28,1.0 ,4))

    ysh=wingLib.applyLeShifts(x,y, LeShiftL)



    #placeSections(x,ysh,ch)
    sectionNames=wingLib.placeSectionsMinLimited(x,ysh,ch,0.001,func4coords,quality)


if 1:

    wingLib.bridgeListOfEdgeLoopsCloseOuterWithFace(sectionNames,'myWing')
    
    #shift to origin
    bpy.context.object.location[1] = -chordlength/2.0
    bpy.context.object.location[2] = 0.0


