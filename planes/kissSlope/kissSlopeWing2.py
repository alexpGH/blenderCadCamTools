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




#===================================================================================================
#=== 
#===================================================================================================
if 0:
    import ipdb
    ipdb.set_trace()
    ipdb.set_trace(context=5)
    


if 1:
    #=== delete all but camera and lamp to start from a clean scene collection
    wingLib.deleteAllButNames(['outl','outl2','myWing1','myWing2'])


#===================================================================================================
#=== basic geometry definition
#===================================================================================================
foilwidth=1.6
chAdditive=0.06             #we add this additive as constant to the chordlength to generate an (towrds tip) increasing over-elliptic ch
chordlength=0.17

nSec=41*2

halfSpan=foilwidth/2.0


if 1:

    #=============================================================
    #=== prepare profiles 
    #=============================================================
    f=libDir+'/AG25_resampled.dat'
    cAG25, leAG25=wingLib.foilImport(f,'auto')
    
    f=libDir+'/AG26_resampled.dat'
    cAG26, leAG26=wingLib.foilImport(f,'auto')
    
    f=libDir+'/AG14_resampled.dat'
    cAG14, leAG14=wingLib.foilImport(f,'auto')
    
    #f=libDir+'/AG27_resampled.dat'
    #cAG27, leAG27=wingLib.foilImport(f,'auto')


    #=== downsampling of the root profile - we don't nee a too fine resolution for the CAM model    
    nPoints=100
    cAG25r, leAG25r=wingLib.foildDataReduceToNpoints(cAG25,nPoints, True) #True: save trailing edge (kep 1st and last point)
    pAG25r=wingLib.curveBezierFromPoints(cAG25r,'PAG25r',True,True)
    

    
    #=== get & interpolate the outer profile on the root (necessary for morphing)
    pAG26=wingLib.curveBezierFromPoints(cAG26,'PAG26',True,True)
    pAG14=wingLib.curveBezierFromPoints(cAG14,'PAG14',True,True)
    #pAG27=wingLib.curveBezierFromPoints(cAG27,'PAG27',True,True)

    cAG14r=wingLib.interpolateBezier2on1(pAG25r, pAG14, leAG25r, leAG14, 40)
    cAG26r=wingLib.interpolateBezier2on1(pAG25r, pAG26, leAG25r, leAG26, 40)
    #cAG27_=wingLib.interpolateBezier2on1(pAG25, pAG27, leAG25, leAG27, 40)
    
    
    #=== plot for check:
    if 0:
        pAG25=wingLib.curveBezierFromPoints(cAG25,'PAG25',True,True)        
        pAG14r=wingLib.curveBezierFromPoints(cAG14_,'PG14r',True,True)
        pAG26r=wingLib.curveBezierFromPoints(cAG26_,'ProfileAG26r',True,True)
    
    #=== clean-up
    if 1:
        wingLib.deleteByName('PAG25r')
        wingLib.deleteByName('PAG14')
        wingLib.deleteByName('PAG26')



    # compile the coord dict for easy access
    cDict={
        "AG25": cAG25r,
        "AG26": cAG26r,
        "AG14": cAG14r,
        #"AG27": cAG27_,
    }



    #=============================================================
    #=== prepare base sections settings
    #=============================================================
    baseSectionsL=[]
    baseSectionsL.append({"p":'AG25', "s":0.00*halfSpan, "tA":0.0, "tMorph":True, "morphT":'lCh'})
    baseSectionsL.append({"p":'AG25', "s":0.05*halfSpan, "tA":0.0, "tMorph":True, "morphT":'lCh'})
    baseSectionsL.append({"p":'AG26', "s":0.40*halfSpan, "tA":0.0, "tMorph":True, "morphT":'lCh'})
    baseSectionsL.append({"p":'AG14', "s":0.95*halfSpan, "tA":0.0, "tMorph":False, "morphT":'lCh'})
    baseSectionsL.append({"p":'AG14', "s":1.00*halfSpan, "tA":0.0, "tMorph":False, "morphT":'lCh'})



    #=============================================================
    #=== chordlength distribution
    #=============================================================

    #=== define section-wise ch extension    
    dChL=[]
    dChL.append({"s": 0.00*halfSpan, "dy": chAdditive})
    dChL.append({"s": 0.40*halfSpan, "dy": chAdditive})
    dChL.append({"s": 0.95*halfSpan, "dy": chAdditive})
    dChL.append({"s": 1.00*halfSpan, "dy": chAdditive})


    #=== ellipse parameters
    a=halfSpan
    b=(chordlength-chAdditive)/2.0
      


    #=== get/init the wing Data object
                                    # for morphed profiles, le is the same
    wingData=wingLib.WingFromSections(cDict, leAG25r, baseSectionsL, halfSpan, a, b, dChL)  



    
if 1:

    #=== get data for indivudual CAM sections
    # get basic ellipse arc points in 1st and 2nd quadrant (the unshifted leading edge) and chordlength
    x,y=wingLib.ellipseParamV(a,b,nSec)
    ch=np.multiply(y,2.0)#
        
    #==adapted chordlength
    ch=wingLib.chordExtensionLinear(ch, x, dChL)




    #shellthickness
    #thickness=1.0

    #=== set 2d profile to be used (gives us a function reference used later)
    func4coords=wingData.coords
    quality='none'    





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
    LeShiftL=[]
    LeShiftL.append(wingLib.LeShift('elliptic',0.04, 0.5, 1.0,foilwidth/2.0))

    ysh=wingLib.applyLeShifts(x,y, LeShiftL)


    #placeSections(x,ysh,ch)
    sectionNames=wingLib.placeSectionsMinLimited(x,ysh,ch,0.001,func4coords,quality)


if 1:

    wingLib.bridgeListOfEdgeLoopsCloseOuterWithFace(sectionNames,'myWing')
    
    #shift to origin
    bpy.context.object.location[1] = -chordlength/2.0
    bpy.context.object.location[2] = 0.0


