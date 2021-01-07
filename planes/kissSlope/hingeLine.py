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

#=== import scripts modules
import wingAnalysisLib as wingALib
reload(wingALib)

#import afData_h105 as h105 
#reload(h105)

#=== end of default header
#==================================================================================================

# open debugging terminal
#__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})




# debugger
if 0:
    import ipdb
    ipdb.set_trace()
    ipdb.set_trace(context=5)

    

if 1:
    #=== delete all but camera and lamp to start from a clean scene collection
    wingLib.deleteAllButNames(['outl','outl2','myWing1','myWing2'])



if 1:

    #====================================================================    
    #=== basic geometric definitions
    #====================================================================    
    
    #=== basic geometry
    foilwidth=1.6
    chAdditive=0.06             #we add this additive as constant to the chordlength to generate an (towrds tip) increasing over-elliptic ch
    chordlength=0.17

    #=== ellipse parameters
    a=foilwidth/2.0
    b=(chordlength-chAdditive)/2.0
    nSec=41*2
    
    
    #=== hinge line for ailerons    
    Adxi=0.04                       # distance from root 
    Adxo=0.09                       # distance from tip
    alpha=0.35*np.pi/180.           # angle for rotation of line
    AyRelLoc=0.22                   # relative location from trailing edge (for inner point)

    # -> span and chord-wise lengths    
    Adx=foilwidth/2.0-Adxi-Adxo     
    Ady=np.tan(alpha)*Adx

    #approx ch-wise location from trailing edge
    Adyi=chordlength*(1.0-AyRelLoc)


    halfSpan=foilwidth/2.0


    #====================================================================    
    #=== plot curves
    #====================================================================    


    #=== unshifted
    # get basic ellipse arc points in 1st and 2nd quadrant (the unshifted leading edge) and chordlength
    x,y=wingLib.ellipseParamV(a,b,nSec)
    ch=np.multiply(y,2.0)#

    
    z=np.zeros_like(x)
    coords1=np.array([x,y,z]).T
    coords1b=np.array([x,-y,z]).T


    #=== plot unshifted/unextended ellipse
    if 0:
        coo1=np.concatenate((coords1,coords1b),axis=0)
        c1=wingLib.curveBezierFromPoints(coo1,'cEllipse',False,False)
    

    
    #=== define section-wise ch extension    
    dChL=[]
    dChL.append({"s": 0.0*halfSpan, "dy": chAdditive})
    dChL.append({"s": 0.4*halfSpan, "dy": chAdditive})
    dChL.append({"s": 0.95*halfSpan, "dy": chAdditive})
    dChL.append({"s": 1.0*halfSpan, "dy": chAdditive})

    chEx=wingLib.chordExtensionLinear(ch, x, dChL)


    
    #=== add extra leading edge shift 
    LeShiftL=[]
    LeShiftL.append(wingLib.LeShift('elliptic',0.04, 0.5, 1.0,foilwidth/2.0))

    ysh1=wingLib.applyLeShifts(x,y, LeShiftL)

    #=== plot shifted extended ellipse
    if 0:
        coords2=np.array([x,ysh1,z]).T
        coords2b=np.array([x,ysh1-chEx,z]).T
        coo2=np.concatenate((coords2,np.flip(coords2b,axis=0)),axis=0)
        c2=wingLib.curveBezierFromPoints(coo2,'cEllipse1stShiftEx',True,True)

    #c2=wingLib.curveBezierFromPoints(coords2,'c2',False,False)
    #c2b=wingLib.curveBezierFromPoints(coords2b,'c2b',False,False)


    # extra power shift
    LeShiftL=[]
    #LeShiftL.append(wingLib.LeShift('power',0.005, 0.28,1.0, foilwidth/2.0, 4))
    #LeShiftL.append(wingLib.LeShift('power',0.01, 0.99,-1.0, foilwidth/2.0, 4))
    
    ysh2=wingLib.applyLeShifts(x,ysh1, LeShiftL)


    coords3=np.array([x,ysh2,z]).T
    coords3b=np.array([x,ysh2-chEx,z]).T

    coo3=np.concatenate((coords3,np.flip(coords3b,axis=0)),axis=0)
    c3=wingLib.curveBezierFromPoints(coo3,'cEllipseShiftEx',True,True)


#    c3=wingLib.curveBezierFromPoints(coords3,'c3',False,False)
    #c3b=wingLib.curveBezierFromPoints(coords3b,'c3b',False,False)
#    c3bEx=wingLib.curveBezierFromPoints(coords3bEx,'c3bEx',False,False)

    
    
    #=== plot hinge line (approx)
    Ayi=ysh2[int(len(ysh2)/2)]-Adyi
    Axi=Adxi
    
    Ayo=Ayi+Ady
    Axo=Axi+Adx    
        
    coHl=[[Axi, Ayi, 0.0],[Axo, Ayo, 0.0]]
    cHl=wingLib.curveBezierFromPoints(coHl,'cHingeLine',False,False)
    
    
    
if 0:
    import ipdb
    ipdb.set_trace()
    ipdb.set_trace(context=5)


        