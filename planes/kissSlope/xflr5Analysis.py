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

 

if 1:
    #=== delete all but camera and lamp to start from a clean scene collection
    wingLib.deleteAllButNames(['outl','outl2','myWing1','myWing2'])


if 1:
    
    
    #=== basic geometry
    foilwidth=1.6
    chAdditive=0.06             #we add this additive as constant to the chordlength to generate an (towrds tip) increasing over-elliptic ch
    chordlength=0.17

    #=== ellipse parameters
    a=foilwidth/2.0
    b=(chordlength-chAdditive)/2.0
    nSec=41*2



    #=== round factor for profile morphing
    roundTo=0.05
    
    
    #=== leading edge shift definition
    LeShiftL=[]
    LeShiftL.append(wingLib.LeShift('elliptic',0.04, 0.5, 1.0,foilwidth/2.0))
    #LeShiftL.append(wingLib.LeShift('power',0.005, 0.28,1.0, foilwidth/2.0, 4))


    #=== basic sections (which might get interpolated)
    BSectionL=[]
    
    if 0:
        # simple straight
        BSectionL.append(wingALib.BaseSection('AG25', 0.0, 0.0, 0, 1.0, False))
        BSectionL.append(wingALib.BaseSection('AG25', 5.0, 0.0, 0, 1.0, False))
        BSectionL.append(wingALib.BaseSection('AG26', 50.0, 0.0, 0, 1.0, False))
        BSectionL.append(wingALib.BaseSection('AG14', 95.0, 0.0, 0, 4.0, False))
        BSectionL.append(wingALib.BaseSection('AG14', 99.0, 0.0, 0, 1.0, False))
            

    if 0:
        # following elliptic cuve            
        BSectionL.append(wingALib.BaseSection('AG25', 0.0, 0.0, 0, 1.0, False))
        BSectionL.append(wingALib.BaseSection('AG25', 5.0, 0.0, 1, 1.0, True, 'lS'))
        BSectionL.append(wingALib.BaseSection('AG26', 50.0, 0.0, 10, 1.0, True, 'lS'))
        BSectionL.append(wingALib.BaseSection('AG14', 95.0, 0.0, 8, 1.0, False))
        BSectionL.append(wingALib.BaseSection('AG14', 99.0, 0.0, 0,1.0, False))


    if 0:
        # following elliptic cuve            
        BSectionL.append(wingALib.BaseSection('AG25', 0.0, 0.0, 0, 1.0, False))
        BSectionL.append(wingALib.BaseSection('AG25', 5.0, 0.0, 1, 1.0, True, 'lCh'))
        BSectionL.append(wingALib.BaseSection('AG26', 50.0, 0.0, 10, 1.0, True, 'lCh'))
        BSectionL.append(wingALib.BaseSection('AG14', 95.0, 0.0, 8, 1.0, False))
        BSectionL.append(wingALib.BaseSection('AG14', 99.0, 0.0, 0,1.0, False))


    if 1:
        # following elliptic cuve            
        #BSectionL.append(wingALib.BaseSection('AG25', 0.0, 0.0, 0, 1.0, False))
        #BSectionL.append(wingALib.BaseSection('AG25', 5.0, 0.0, 1, 1.0, True, 'lCh'))
        #BSectionL.append(wingALib.BaseSection('AG26', 40.0, 0.0, 10, 1.0, True, 'lCh',0.0))
        #BSectionL.append(wingALib.BaseSection('AG14', 95.0, -2.0, 8, 1.0, False,'lCh', 0.02))
        #BSectionL.append(wingALib.BaseSection('AG14', 99.0, -2.0, 0,1.0, False,'lCh', 0.02))

        #                           profile,rel span in %, twistangle, nSubsections, scale NpanelsPerM by this, tMorph, morphType, chordAditive   
        BSectionL.append(wingALib.BaseSection('AG25', 0.0, 0.0, 0, 1.0, False,'lCh',chordAdditive))
        BSectionL.append(wingALib.BaseSection('AG25', 5.0, 0.0, 1, 1.0, True, 'lCh',chordAdditive))
        BSectionL.append(wingALib.BaseSection('AG26', 40.0, 0.0, 10, 1.0, True, 'lCh',chordAdditive))
        BSectionL.append(wingALib.BaseSection('AG14', 95.0, -0.0, 8, 1.0, False,'lCh', chordAdditive))
        BSectionL.append(wingALib.BaseSection('AG14', 99.0, -0.0, 0,1.0, False,'lCh', chordAdditive))

    if 0:
        BSectionL.append(wingALib.BaseSection('AG25', 0.0, 0.0, 0, 1.0, False))
        BSectionL.append(wingALib.BaseSection('AG25', 5.0, 0.0, 1, 1.0, True, 'lCh'))
        BSectionL.append(wingALib.BaseSection('AG26', 40.0, 0.0, 10, 1.0, True, 'lCh'))
        BSectionL.append(wingALib.BaseSection('AG27', 95.0, 0.0, 8, 1.0, False))
        BSectionL.append(wingALib.BaseSection('AG27', 99.0, 0.0, 0, 1.0, False))

    #y=wingLib.ellipsePoint(a,b,x)
    #ch=2*y


    soup=wingALib.buildXPlaneTree()
    soup, factL =wingALib.xPlaneAddSectionsElliptic(soup, LeShiftL, BSectionL, foilwidth, chordlength-chordAdditive, 13, 40, roundTo)

    print(factL)

    if 0:
        with open("/qnap/flxride/construction/foil/blender/planes/kissSlope/a1_straight.xml", "w") as f:
          #f.write(str(soup.prettify()))
          f.write(str(soup))

    if 0:
        with open("/qnap/flxride/construction/foil/blender/planes/kissSlope/a1_ellipticLinear.xml", "w") as f:
          f.write(str(soup))
    if 1:
        with open("/qnap/flxride/construction/foil/blender/planes/kissSlope/a1_ellipticLinear_0.40_0.95_1.0_scA0.03.xml", "w") as f:
          f.write(str(soup))


if 0:
    #----------------------------------------------------------------------
    # enforce writing of all necessary morphed profiles 
    #----------------------------------------------------------------------
    factL=[]

    factLSubM=[]
    for i in range(0,int(1.0/roundTo)):
        factLSubM.append(roundTo*i)
        
    for iSec in range(0,len(BSectionL)):
        #print('--- '+str(iSec))
        
        if BSectionL[iSec].tMorphSub:
            factL.append(factLSubM)
        else:            
            factL.append([])
    
    
if 0:
    
    #----------------------------------------------------------------------
    # prepare profile data for morphing 
    #----------------------------------------------------------------------
    profileOutPath=libDir+'/../planes/kissSlope/aerodynAnalysis/'

    f=libDir+'/AG25_resampled.dat'
    cAG25, leAG25=wingLib.foilImport(f,'auto')

    f=libDir+'/AG26_resampled.dat'
    cAG26, leAG26=wingLib.foilImport(f,'auto')
    
    f=libDir+'/AG14_resampled.dat'
    cAG14, leAG14=wingLib.foilImport(f,'auto')
    
    f=libDir+'/AG27_resampled.dat'
    cAG27, leAG27=wingLib.foilImport(f,'auto')

    pAG25=wingLib.curveBezierFromPoints(cAG25,'ProfileAG25',True,True)
    pAG26=wingLib.curveBezierFromPoints(cAG26,'ProfileAG26',True,True)
    pAG14=wingLib.curveBezierFromPoints(cAG14,'ProfileAG14',True,True)
    pAG27=wingLib.curveBezierFromPoints(cAG14,'ProfileAG27',True,True)
    
    # interpolate the oute profile on the inner (all on same inner)
    cAG14_=wingLib.interpolateBezier2on1(pAG25, pAG14, leAG25, leAG14, 40)
    cAG26_=wingLib.interpolateBezier2on1(pAG25, pAG26, leAG25, leAG26, 40)
    cAG27_=wingLib.interpolateBezier2on1(pAG25, pAG27, leAG25, leAG27, 40)
    
    # for plotting:
    #pAG14_4M=wingLib.curveBezierFromPoints(cAG14,'ProfileAG14M',True,True)

    # compile the coord dict for easy access
    cDict={
        "AG25": cAG25,
        "AG26": cAG26_,
        "AG14": cAG14_,
        "AG27": cAG27_,
    }    
    


    #=== calculate and write morphed profiles
    
    for iSec in range(0,len(BSectionL)):
        print('--- '+str(iSec))
    
        if BSectionL[iSec].tMorphSub:
            mt=BSectionL[iSec].morphType
            
        else:
            continue    
        
    
        # open inner and outer profile
            
        # loop over orphed subsections        
        for iSub in range(0,len(factL[iSec])):
    
            print(iSub)
            
            # if close to inner / outer foil use that one
            if abs(factL[iSec][iSub])<0.01 or abs(factL[iSec][iSub]-1.0)<0.01:
                continue
            
                
            # morph
            fact=factL[iSec][iSub]
        
            pStrI=BSectionL[iSec].profile    
            pStrO=BSectionL[iSec+1].profile
            
            ci=cDict[pStrI]
            co=cDict[pStrO]
            cdelta=co-ci
            
            cMorphed=ci+fact*cdelta    
            
            rFact=round(fact/roundTo)*roundTo

            profileName=pStrI+pStrO+'_'+str(int(rFact*100.0))
            filename=profileOutPath+profileName+'.dat'
            
            wingLib.foilExport(cMorphed,profileName,filename,'xlfr54spaces')


            #print('inside '+str(iSec)+' '+str(iSub))
    
        