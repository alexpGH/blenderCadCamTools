#MIT License
#Copyright 2020 Alexander Poddey
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#For the curve simplification check to have edit>preferences>add-ons> Add curve: simplfy curves+ activated

from __future__ import division      
import bpy
import math
import numpy as np
import matplotlib.pyplot as plt

import mathutils

from dataclasses import dataclass

    

#--------------------------------------------------------------
#--- helper routines for selection etc.
#--------------------------------------------------------------
def deselectAll():
    #for ob in bpy.context.selected_objects:
    #    ob.select = False
    bpy.ops.object.select_all(action='DESELECT')

        
        
def selectAndActivateByName(name):
    #bpy.data.objects[name].select=True
    #deprecated since 2.8 bpy.context.scene.objects.active = bpy.data.objects[name]
    bpy.context.view_layer.objects.active = bpy.data.objects[name]
    bpy.context.active_object.select_set(state=True)


    #--------------------------------------------------------------

def selectOne(name):
    deselectAll()
    selectAndActivateByName(name)    
  
def copyByName(name, nameNew):
    selectOne(name)
    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0.0, 0.0, 0.0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
    bpy.context.selected_objects[0].name=nameNew

  
def selectFromList(nameList):
    deselectAll()
    for i in range(0,len(nameList)):
        selectAndActivateByName(nameList[i])


def reName(nameNew):
    bpy.context.selected_objects[0].name=nameNew


def deleteAllButName(name):
    for ob in bpy.data.objects:
        if ob.name!=name and ob.name!='Camera' and ob.name!='Lamp':
            selectOne(ob.name)
            bpy.ops.object.delete() 


def deleteAllButNames(names):
    for ob in bpy.data.objects:
        if ob.name not in names and ob.name!='Camera' and ob.name!='Lamp':
            selectOne(ob.name)
            bpy.ops.object.delete() 

            
def deleteAll():
    for ob in bpy.data.objects:
        if ob.name!='Camera' and ob.name!='Lamp':
            selectOne(ob.name)
            bpy.ops.object.delete() 


def deleteByName(name):
    selectOne(name)
    bpy.ops.object.delete()
    
#--------------------------------------------------------------
#--- curve fitting through points
#--------------------------------------------------------------


#--- Bezier -> matches the points exactly (not like NURBS)
def curveDataBezierFromPoints(coords,name,tClosed,tSharpClosed):
    # create the Curve Datablock
    curveData = bpy.data.curves.new(name, type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 2

    # map coords to spline
    polyline = curveData.splines.new('BEZIER')
    polyline.bezier_points.add(len(coords)-1)
    
    for i, coord in enumerate(coords):
        x,y,z = coord
        #polyline.bezier_points[i].co = (x, y, z, 1)
        polyline.bezier_points[i].co = (x, y, z)
        polyline.bezier_points[i].handle_left = (x, y, z)
        polyline.bezier_points[i].handle_right = (x, y, z)
        
        
        #Set automatic
        polyline.bezier_points[i].handle_right_type = 'AUTO'
        polyline.bezier_points[i].handle_left_type = 'AUTO'
        
        #Now set handle type to aligned
        #polyline.bezier_points[i].handle_right_type = 'ALIGNED'
        #polyline.bezier_points[i].handle_left_type = 'ALIGNED'
        

    if(tClosed):
        polyline.use_cyclic_u = True
        #polyline.use_cyclic_v = True

    if(tSharpClosed):
        #results e.g. in a poined tail for airfoils
        polyline.bezier_points[0].handle_right_type = 'VECTOR'
        polyline.bezier_points[0].handle_left_type = 'VECTOR'

        polyline.bezier_points[-1].handle_right_type = 'VECTOR'
        polyline.bezier_points[-1].handle_left_type = 'VECTOR'

    return curveData

    

def curveBezierFromPoints(coords,name,tClosed,tSharpClosed):
    # create the Curve Datablock
    curveData = curveDataBezierFromPoints(coords,name,tClosed,tSharpClosed)

    # create Object
    curveOB = bpy.data.objects.new(name, curveData)

    # attach to scene and validate context
    scn = bpy.context.scene
    #scn.objects.link(curveOB) - deprecated since 2.8 use the command below
    bpy.context.collection.objects.link(curveOB)
    #scn.objects.active = curveOB
    bpy.context.view_layer.objects.active = curveOB

    #curveOB.select = True
    curveOB.select_set(state=True)
    #bpy.context.active_object.select_set(state=True)

    return curveOB


    
 
#--- NURBS -> beware: resulting curve will not exactly match the points 
def curveDataFromPoints(coords,name,tClosed):
    # create the Curve Datablock
    curveData = bpy.data.curves.new(name, type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 2

    # map coords to spline
    polyline = curveData.splines.new('NURBS')
    polyline.points.add(len(coords)-1)
    for i, coord in enumerate(coords):
        x,y,z = coord
        polyline.points[i].co = (x, y, z, 1)

    if(tClosed):
        polyline.use_cyclic_u = True

    return curveData

def curveFromPoints(coords,name,tClosed):

    curveData=curveDataFromPoints(coords,name,tClosed)

    # create Object
    curveOB = bpy.data.objects.new(name, curveData)

    # attach to scene and validate context
    scn = bpy.context.scene
    #scn.objects.link(curveOB) - deprecated since 2.8 use the command below
    bpy.context.collection.objects.link(curveOB)
    #scn.objects.active = curveOB
    bpy.context.view_layer.objects.active = curveOB

    #curveOB.select = True
    curveOB.select_set(state=True)
    #bpy.context.active_object.select_set(state=True)


#----------------------------------------------------------------------------------------
#--- geometric routines (e.g. for calculating shrinked hull as local perpendicular shift
#----------------------------------------------------------------------------------------
        

#from https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines-in-python 2nd answer   
def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

def intersection(L1, L2):
    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x,y
    else:
        return False


#----------------------------------------------------------------------------------------
#--- ellipse helpers
#----------------------------------------------------------------------------------------

#---------------------------------------------


def ellipseParamV(a,b,npoints):
    dalpha=np.pi/(npoints)
    t=np.multiply(range(0,npoints+1),dalpha)
    x=np.multiply(np.cos(t),a)
    y=np.multiply(np.sin(t),b)
    return x,y


def ellipsePoint(a,b,x):
    t=np.arccos(x/a)
    y=np.multiply(np.sin(t),b)

    return y





#---------------------------------------------
def elipticShift(x,y, dyMax, xFactStart,dirFact, xmax):
    thick=0.0
    ysh=np.copy(y)
    #xmax=np.max(x)
    #xStart=xmax*(1.0-xFactStart)+thick/2
    xStart=(xmax-thick)*(1.0-xFactStart)
    a=xmax-xStart
    b=dyMax

    for i in range(0,len(x)):
        xabs=np.absolute(x[i])
        if(xabs>xStart):
            xloc=xabs-xStart
            #if((xloc/a)<1.0):
            if((xloc/a)<1.0):
                dy=np.sqrt(b*b*(1-xloc*xloc/(a*a)))-b
            else:
                dy=np.sqrt(b*b*(xloc*xloc/(a*a)-1))-b
                
            ysh[i]=y[i]+dirFact*dy            
            print("-> "+str(x[i])+" "+str(xloc)+" "+str(dy)+" "+str(a))
        
    return ysh




#----------------------------------------------------------------------------------------
#--- helpers for placing leading edge etc.
#----------------------------------------------------------------------------------------

#takes the x/y points (e.g. leading edge), center is at x=0
#shifts those points (towards large x) beyond  xFactStart back (negative y)
#e.g xFactStart=0.8 -> the outer 20% of points will be shifted backwards
#the shift is given by x^p with the maximal shift (the outermost point) is dyMax 
#---------------------------------------------
def powerShift(x,y, p, dyMax, xFactStart, xmax):
    ysh=powerShiftDir(x,y,p,dyMax, xFactStart,1.0,xmax) # dirfact fix
    return ysh    


def powerShiftDir(x,y, p, dyMax, xFactStart,dirFact, xmax):
    thick=0.0 # formerly used for reducing the geometry (e.g. for laminating) new version uses shrink
              # in placeSetcions
    ysh=np.copy(y)
    #xmax=np.max(x)
    #xStart=xmax*(1.0-xFactStart)+thick/2
    xStart=(xmax-thick)*(1.0-xFactStart)
    
    dxmax=xmax-thick-xStart
    a=dyMax/math.pow(dxmax,p)
    
    for i in range(0,len(x)):
        xabs=np.absolute(x[i])
        if(xabs>xStart):
            xloc=xabs-xStart
            dy=math.pow(xloc,p)*a                
            ysh[i]=y[i]-dy*dirFact            
            print("-> "+str(x[i])+" "+str(xloc)+" "+str(dy)+" "+str(a))
        
    return ysh    





#---------------------------------------------

def placeSections(xV,yV,chV,func4coords,quality):

    for i in range(0,len(x)):
        scale=chV[i]
        shiftV=[xV[i],yV[i],0.0]
        hCoord=func4coords(quality,scale,shiftV)
        curveBezierFromPoints(hCoord,'2dsection_'+str(i),True,True) #sharp closed
        #print('fut a')
        #print(str(hCoord))
        #print('fut b')
#---------------------------------------------


def placeSectionsMinLimited(xV,yV,chV,minCh,func4coords,quality):

    sectionNames=[]
    
    for i in range(0,len(xV)):
        if chV[i]<minCh:
            print('Skipping')
        else:
            scale=chV[i]
            shiftV=[xV[i],yV[i],0.0]
            hCoord=func4coords(quality,scale,shiftV)
            name='2dsection_'+str(i)
            curveBezierFromPoints(hCoord,name,True,True)#sharp closed
            sectionNames.append(name)
            
        #print('fut a')
        #print(str(hCoord))
        #print('fut b')
    return sectionNames
#---------------------------------------------



def placeSectionsShrinked(xV,yV,chV,dShrink,func4coords,func4idx,quality):
    xnV=np.array([-1.0,0.0,0.0])
    nV=np.array([0,0,0])
    locV=np.array([0,0,0])
    
    leIdx=func4idx(quality)
     
    for i in range(0,len(x)):

        #skip too small chordlength
        if (chV[i]<3*dShrink):
            print('Skipping '+str(i))
            continue
            
        idx2Kill=np.array([0])
        scale=chV[i]
        shiftV=[xV[i],yV[i],0.0]
        hCoord=func4coords(quality,scale,shiftV) #original chord

        #skip so small thicknes (crude)
        if (max(hCoord[:,2])-min(hCoord[:,2])<3*dShrink):
            print('Skipping due to thickness '+str(i))
            continue

        hCoordShrinked=np.copy(hCoord) #make a real copy of the array
        for j in range(0,len(hCoord)-2):
            locV=hCoord[j+2]-hCoord[j] #
            nV=np.cross(xnV,locV) #norm direction
            nV=nV/np.linalg.norm(nV) #normalized 

            #print('checkthis')
            #print(str(j+1))
            #print(str(hCoordShrinked[j+1]))
            hCoordShrinked[j+1]=hCoordShrinked[j+1]+dShrink*nV
            #print(str(hCoordShrinked[j+1]))
        #print('+++')
        #print(str(hCoord[24]))
        #print(str(hCoordShrinked[24]))
        #print('+++')
        
        #first point
        locV=hCoord[1]-hCoord[-1] #
        nV=np.cross(xnV,locV) #norm direction
        nV=nV/np.linalg.norm(nV) #normalized 
        hCoordShrinked[0]=hCoordShrinked[0]+dShrink*nV
                 
        #-2 point
        locV=hCoord[-1]-hCoord[-3] #
        nV=np.cross(xnV,locV) #norm direction
        nV=nV/np.linalg.norm(nV) #normalized 
        hCoordShrinked[-2]=hCoordShrinked[-2]+dShrink*nV
                       
        #last point
        locV=hCoord[0]-hCoord[-2] #
        nV=np.cross(xnV,locV) #norm direction
        nV=nV/np.linalg.norm(nV) #normalized 
        hCoordShrinked[-1]=hCoordShrinked[-1]+dShrink*nV



        #check for sanity of upper half via estimated mid line
        for ii in range(1,leIdx):

            L1 = line(hCoord[ii,1:3], hCoordShrinked[ii,1:3]) #y,z coordinate
            tfound=False
            
            # loop over possible intersection on other side of profile
            for jj in range(leIdx,len(hCoord)-1):
                L2 = line(hCoord[jj,1:3],hCoord[jj+1,1:3])
                R=intersection(L1, L2)                
                if R:
                    #distance from intersectin to one point is smaller than distance between points
                    if (np.power(R[0]-hCoord[jj,1],2)+np.power(R[1]-hCoord[jj,2],2)<=np.power(hCoord[jj+1,1]-hCoord[jj,1],2)+np.power(hCoord[jj+1,2]-hCoord[jj,2],2)):
                        tfound=True
                        #check half distance between original point and intersection
                        if(np.sqrt(np.power(R[0]-hCoord[ii,1],2)+np.power(R[1]-hCoord[ii,2],2))/2<dShrink*1.1): #we add 10% to be sure
                            idx2Kill=np.append(idx2Kill,[ii])
                        break
            #also delete point in case we did not find a matching intersection
            if(not tfound):
                idx2Kill=np.append(idx2Kill,[ii])
            
        #print('idx2Kill CHECK THIS ONE AFTER UPPER HALF-------------------')
        #print(str(idx2Kill))

        #check for sanity of lower half via estimated mid line
        for ii in range(leIdx+1,len(hCoord)):

            L1 = line(hCoord[ii,1:3], hCoordShrinked[ii,1:3]) #y,z coordinate
            tfound=False
            
            # loop over possible intersection on other side of profile
            for jj in range(1,leIdx):
                L2 = line(hCoord[jj,1:3],hCoord[jj+1,1:3])
                R=intersection(L1, L2)                
                if R:
                    #distance from intersectin to one point is smaller than distance between points
                    if (np.power(R[0]-hCoord[jj,1],2)+np.power(R[1]-hCoord[jj,2],2)<=np.power(hCoord[jj+1,1]-hCoord[jj,1],2)+np.power(hCoord[jj+1,2]-hCoord[jj,2],2)):
                        tfound=True
                        #check half distance between original point and intersection
                        if(np.sqrt(np.power(R[0]-hCoord[ii,1],2)+np.power(R[1]-hCoord[ii,2],2))/2<dShrink*1.1): #we add 10% to be sure
                            idx2Kill=np.append(idx2Kill,[ii])
                        break
            #also delete point in case we did not find a matching intersection
            if(not tfound):
                idx2Kill=np.append(idx2Kill,[ii])
            
            
        #print('idx2Kill CHECK THIS ONE AFTER lower HALF-------------------')
        #print(str(idx2Kill))
            
            
        #now check sanity of points in the leading edge region
        for j in range(1,len(hCoord)-1):
        #for j in range(20,35):
            #print('===========')
            #print(str(j))
            #print('===========---')
            #print(str(hCoord[j-1][2]))
            #print(str(hCoord[j][2]))
            #print(str(np.sign(hCoord[j][2]-hCoord[j-1][2])))
            #print('----')
            #print(str(hCoordShrinked[j-1][2]))
            #print(str(hCoordShrinked[j][2]))
            #print(str(np.sign(hCoordShrinked[j][2]-hCoordShrinked[j-1][2])))
            
            #if(np.sign(hCoord[j][2]-hCoord[j-1][2])!=np.sign(hCoordShrinked[j][2]-hCoordShrinked[j-1][2])):
                #idx2Kill=np.append(idx2Kill,[j])
            if(np.sign(hCoord[j][2])!=np.sign(hCoordShrinked[j][2])):                        
                idx2Kill=np.append(idx2Kill,[j])

        #now sort idx
        idx2Kill=np.sort(idx2Kill)
        #print('idx2Kill -------------------')
        #print(str(idx2Kill))


        #print('DETAILS -------------------')
        #print(str(hCoordShrinked))
        #print('idx2Kill -------------------')
        #print(str(idx2Kill))

        #delete trailing point in any case
        hCoordShrinked=np.delete(hCoordShrinked,idx2Kill[0],0)
        idx2Kill=idx2Kill-1

        #print('DETAILS after-------------------')
        #print(str(hCoordShrinked))
        #print('idx2Kill -------------------')
        #print(str(idx2Kill))





        #start from 1 as we do not delete idx2Kill entries!
        lastIdx=-1
        for j in range(1,len(idx2Kill)):
            #delete messed up point, correct indices (as we deleted a row in hCoordShrinked
            #prevent multiples
            if(idx2Kill[j]!=lastIdx):
                hCoordShrinked=np.delete(hCoordShrinked,idx2Kill[j],0)
                idx2Kill=idx2Kill-1
                lastIdx=idx2Kill[j]
                
        curveBezierFromPoints(hCoordShrinked,'2dsectionShrinked_'+str(i),True,True)#sharp closed



# fits a hull over the wing sections provided
def bridgeListOfEdgeLoopsCloseOuterWithFace(sectionNames,targetName):

    #make faces ad end loops
    selectOne(sectionNames[0])
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.editmode_toggle()

    selectOne(sectionNames[-1])
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.editmode_toggle()


    #reselect all , join an dbridge edge loops
    selectFromList(sectionNames)

    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()
    bpy.ops.object.editmode_toggle()
    #select really all in mesh
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.bridge_edge_loops()

    bpy.context.selected_objects[0].name=targetName
    bpy.ops.object.editmode_toggle()
        


# takes the 'super' coordinate set which are way to much points for us (e.g. 200)and generates
# a set of candidate sets which can be copied over from command line to the af_xy file with reduced
# number of points, following from curve simplification (reduces number of points with least possible error)
# For the curve simplification check to have edit>preferences>add-ons> Add curve: simplfy curves+ activated
#
# A example to get the super set is:
# coords=mh30modpk.coords('super',1.0,[0.0,0.0,0.0])
# errPara here is in curve simplyfy parameter - a ggod value for normal is 0.0002
# tDelete - should the curves be deleted? (keep for optical inspection of error)
def foilDataGenerateReducedQuality(coords,errPara,tDelete):

    curve1=curveBezierFromPoints(coords,'testcurve',True,True)#sharp closed
    curve2=bpy.ops.curve.simplify(error=errPara)
    
    
    #bpy.ops.curve.simplify(error=0.0002)
    ob=bpy.context.object
    
    #we keep the most positive in y as leading edge idx
    lastDist=-1e42
    idx=0
    idxLe=0
    for p in ob.data.splines.active.bezier_points:
        print("["+str(p.co[0])+", "+str(p.co[1])+", "+str(p.co[2])+"],")
        #print(p.co)
        #print(str(p.co[1]))
        if(p.co[1]>lastDist):
            lastDist=p.co[1]
            idxLe=idx

        idx=idx+1

    #print("NOTE: check to not have 2 points (to close) on the trailing edge!")
    print("Number of points: "+str(len(ob.data.splines.active.bezier_points)))
    print("Leading edge index: "+str(idxLe)+" with value: "+str(lastDist))

    # cleanup
    if tDelete:
        deleteByName('Simple_testcurve')
        deleteByName('testcurve')



        
def bezierCurveReduceToNpoints(curveIn,nPoints,name):
    iterMax=100

    n1=len(curveIn.data.splines.active.bezier_points)
    print("Initial number of points: "+str(n1))

    #sanity check
    if n1<nPoints:
        raise Exception('Bisectioning not converged!Can not increase number of points')
        

    #init bisctioning
    tDouble=True
    err=0.0001
    dErr=0.0001


    tDone=False
    i=0
    while not tDone:
        i+=1

        selectAndActivateByName(curveIn.name)
        bpy.ops.curve.simplify(error=err)
        curve2=bpy.context.object
        n=len(bpy.context.object.data.splines.active.bezier_points)

        
        s="Iteration: "+str(i)+ " is / should be: "+str(n)+"/"+str(nPoints)
    
        if n==nPoints:
            tDone=True
            break

        if i==iterMax:
            break

        #not yet: strategy
        deleteByName(bpy.context.object.name)
        if n>nPoints:
            if tDouble:
                dErr=dErr*2
                err=err+dErr
                print(s+" *2: "+str(err)+" dErr="+str(dErr))
            else:
                dErr=dErr*0.5
                err=err+dErr
                print(s+" +: "+str(err)+" dErr="+str(dErr))
        else:
            #first time smaller
            tDouble=False
            dErr=dErr*0.5
            err=err-dErr
            print(s+" -: "+str(err)+" dErr="+str(dErr))

    #check
    if not tDone:
        deleteByName(bpy.context.object.name)
        raise Exception('Bisectioning not converged!')

    print(s)
    
    #we keep the most positive in y as leading edge idx
    lastDist=-1e42
    idx=0
    idxLe=0
    for p in bpy.context.object.data.splines.active.bezier_points:
        if(p.co[1]>lastDist):
            lastDist=p.co[1]
            idxLe=idx

        idx=idx+1
    
    #print("NOTE: check to not have 2 points (to close) on the trailing edge!")
    print("Finally:")
    print("Number of points: "+str(len(bpy.context.object.data.splines.active.bezier_points)))
    print("Leading edge index: "+str(idxLe)+" with value: "+str(lastDist))


    #close curve (curve simplify opens it again)
    polyline=curve2.data.splines.active
    if True:
        polyline.use_cyclic_u = True

    if True: #tSharpClosed
        #results e.g. in a poined tail for airfoils
        polyline.bezier_points[0].handle_right_type = 'VECTOR'
        polyline.bezier_points[0].handle_left_type = 'VECTOR'

        polyline.bezier_points[-1].handle_right_type = 'VECTOR'
        polyline.bezier_points[-1].handle_left_type = 'VECTOR'


    
    # cleanup
    #if tDelete:
    #    deleteByName(bpy.context.object.name)
    curve2.name=name
    return curve2, idxLe  



# reduces number of points (e.g. for morphing), returns coords and leIdx
def foildDataReduceToNpoints(coords,nPoints, tKeepTE=True):
    iterMax=100


    if tKeepTE:
        curve1=curveBezierFromPoints(coords[1:-1],'testcurve',True,True) 
        nPoints_=nPoints-2
    else:
        curve1=curveBezierFromPoints(coords,'testcurve',True,True)#sharp closed
        nPoints_=nPoints
        
    cOut,leIdx=bezierCurveReduceToNpoints(curve1,nPoints_,'reducedcurve')

    
    coordOut=np.zeros((nPoints,3))
    ip=0
    if tKeepTE:
        coordOut[0]=coords[0]
        coordOut[-1]=coords[-1]
        ip+=1
        leIdx+=1
        
    for p in cOut.data.splines.active.bezier_points:
        coordOut[ip]=[p.co[0], p.co[1], p.co[2]]
        ip+=1

    #clean-up the curves
    deleteByName('testcurve')    
    deleteByName('reducedcurve')    

    return coordOut, leIdx





def foilExport(coords,profileName,filename,mode):

    if(mode=='selig4spaces'):
        f = open(filename, "w")
        f.write(profileName+"\n")
        for i in coords:
            f.write(str(i[1])+"    "+str(i[2])+"\n")
        f.close()
        
    elif(mode=='xlfr54spaces'):
        f = open(filename, "w")
        f.write(profileName+"\n")
        for i in coords:
            f.write(str(i[1]*-1.0)+"    "+str(i[2])+"\n")
        f.close()
        
        
    else:
        raise Exception('unknown mode:'+mode)


def foilImport(filename,mode):
    le=0
    yle=1e42
    
    if(mode=='auto'):
        f = open(filename, "r")
        lines = f.readlines() 

        #skip 1st line per diefinition
        coords=np.zeros( (len(lines)-1,3) ) 
        
        # Strip whitespace extract ccords 
        iL=0
        for line in lines[1:]: #skip 1st line per definition (description)

            s=line.strip().split(' ')
            coords[iL,1]=s[0]
            coords[iL,2]=s[-1]            
            #the rest is whitespaces
            iL+=1

            
        #flip sign of Y
        if coords[0,1]>0.0:
            coords[:,1]=coords[:,1]*-1.0

        idx=np.argmax(coords[:,1])    
        f.close()

    else:
        raise Exception('unknown mode:'+mode)
    
    return coords,idx
    

def plotArray(x,y,title,legend,outfile):
    print("##################### Plotting ##################")
    fig=plt.figure()
    ax= fig.add_subplot(111)
    ax.plot(x,y)
    ax.legend(legend)
    
    plt.title(title)
    plt.grid(True)

    fig.savefig(outfile)



    

#=============================================================================================
#=== bezier interpolation stuff 
#=============================================================================================
def get_combined_length(p_list):
    edge_length = 0
    for idx in range(len(p_list)-1):
        edge_length += (p_list[idx] - p_list[idx+1]).length  
           
    return edge_length


#bpy.data.curves['BezierCurve'].splines[0]
#splines.active.bezier_points
def getBezierLength(curve, nInterpol):
    
    bps=curve.data.splines.active.bezier_points
    npt=len(bps)

    l=0
    lloc=np.zeros(npt-1)
    
    for ip in range(1,npt):
        handle1 = bps[ip].handle_left
        knot1 = bps[ip].co
        knot2 = bps[ip-1].co
        handle2 = bps[ip-1].handle_right

        #note: we have handle_left and _right which can be different in free mode (which we don't use
        
        # approximate  and store lenght of this section
        p_list = mathutils.geometry.interpolate_bezier(knot1, handle1, handle2, knot2, nInterpol)
        l_=get_combined_length(p_list)
        if ip==1:

            lloc[ip-1]=l_
        else:
            lloc[ip-1]=lloc[ip-2]+l_
        # increase total lenght
        l=l+l_

    # relative lenght
    llocRel=lloc/l
    
    
    if 0:    
        print(l)
        print(lloc)
        print('---')
        print(sum(lloc))
        print(llocRel*100)

    return l, llocRel


# interpolate the c2 from its bezier curve to coords at relative length positions of c1
# e.g. for morphing: we need a) the same number of points and equal sampling along the curve
def interpolateBezier2on1(c1 ,c2, idxLe1, idxLe2,nInterpol):

    l1, lloc1=getBezierLength(c1, nInterpol)
    l2, lloc2=getBezierLength(c2, nInterpol)

    #print("npoints: "+str(len(lloc1)+1)+":"+str(len(lloc2)+1))
    #print("sanity: "+str(lloc1))


    #c1
    bps=c1.data.splines.active.bezier_points
    npt=len(bps)

    #print("NPT: "+str(npt))

    #c2
    bps2=c2.data.splines.active.bezier_points
    npt2=len(bps2)



    
    # resampled coords
    coordOut=np.zeros((npt,3))

    # first, last and le points kept
    coordOut[0]=[bps2[0].co[0], bps2[0].co[1], bps2[0].co[2]]
    coordOut[-1]=[bps2[-1].co[0], bps2[-1].co[1], bps2[-1].co[2]]

    coordOut[idxLe1]=[bps2[idxLe2].co[0], bps2[idxLe2].co[1], bps2[idxLe2].co[2]]
    
    # upper half
    for ip in range(1,npt-1):

        #skip leading edge point
        if ip==idxLe1:
            continue
            
        # locate corrsponding segment on c2 for relative lenght of c1 point
        # note lloc hast the length at end of segment, therefore ip is lloc(ip-1)
        full_l1=lloc1[ip-1]
        idx=np.argmax(lloc2 >= full_l1)
        
        #idx is the idx of the segment which leads to larger lenght
        #    but also the index of the bezier's starting point for this segment
        # be careful in which direction (requires swithcing handle left right)
        p1 = bps2[idx].handle_right #handle1
        p0 = bps2[idx].co #knot1
        p3 = bps2[idx+1].co #knot2
        p2 = bps2[idx+1].handle_left #handle2

        full_l2=lloc2[idx-1]
        
        #what is missing in absolute length
        absDelta=full_l1-full_l2

        # length of segment in curve 2
        l_=lloc2[idx]-lloc2[idx-1]

        #relative lenght on this segment
        t=absDelta/l_

        point_=np.power((1.-t),3)*p0 + 3.0*np.power((1.-t),2)*t*p1 +3.*(1.-t)*t*t*p2+t*t*t*p3
        coordOut[ip]=point_

        if 0:
            print("DEVEL: "+str(ip))
            print(full_l2,full_l1)
            print(idx, lloc1[ip], lloc1[ip-1], lloc2[idx],lloc2[idx-1])
            print(absDelta)
            print('---')
            print(t)

            handle1 = bps2[idx].handle_right
            knot1 = bps2[idx].co
            knot2 = bps2[idx+1].co
            handle2 = bps2[idx+1].handle_left

            print('INterpol test')
            nInterpol=100
            p_list = mathutils.geometry.interpolate_bezier(knot1, handle1, handle2, knot2, nInterpol)
            print(get_combined_length(p_list))

            #if ip==16:
                #curveBezierFromPoints(p_list,'Debug',False,False)
                #raise Exception('DEBUG')
        
        

    return coordOut
    



#=============================================================================================
#=== data structures
#=============================================================================================
@dataclass
class LeShift:
    sType: str      # currently elliptic or power
    dyMax: float
    xFactStart:float
    dirFact: float
    xmax: float=0  #only used for power
    p:float=0      # only used for power
    





#=============================================================================================
#=== 
#=============================================================================================
    
def applyLeShifts(x,y, LeShiftL):

    ysh=np.copy(y)

    
    print(len(LeShiftL))
    for i in range(0,len(LeShiftL)):
        print(LeShiftL[i].sType)
        
        if LeShiftL[i].sType=='elliptic':
            print('Elliptic shift applied')
            ysh=elipticShift(x,ysh, LeShiftL[i].dyMax, LeShiftL[i].xFactStart, LeShiftL[i].dirFact,LeShiftL[i].xmax)

        elif LeShiftL[i].sType=='power':
            print('Power shift applied')
            ysh=powerShiftDir(x,ysh, LeShiftL[i].p, LeShiftL[i].dyMax, LeShiftL[i].xFactStart, LeShiftL[i].dirFact,LeShiftL[i].xmax)

        else:
            raise Exception("Unknown LeShift Type")


    return ysh




#=============================================================================================
#=== 
#=============================================================================================


def chordExtensionLinear(ch, x, dChL):

    #import ipdb
    #ipdb.set_trace()
    #ipdb.set_trace(context=5)
   
    #do we have even or uneven number of sections?
    nx=len(x)
    tEven=nx/2%1<1e-10

    chEx=np.copy(ch)
    iMid=math.floor(nx/2) #will be adapted below
    diMid=0
    j=0


    # uneven: process mid first
    if not tEven:
        
        #iMid is really the mid
        dCh=chordExtensionLinear_helper(x[iMid], dChL)
        chEx[iMid]=ch[iMid]+dCh

        diMid=1
        
    # set iMid to correct start position (1 left of mid)    
    iMid=iMid-1
    for i in range(iMid,-1,-1):
        j+=1
        dCh=chordExtensionLinear_helper(x[i], dChL)

        chEx[i]=ch[i]+dCh
        if nx>1:
            chEx[iMid+diMid+j]=chEx[i] #diMid is shift by 1 in uneven case    


    return chEx        



def chordExtensionLinear_helper(x_, dChL):

    iSec=0
    iSecMax=len(dChL)-1
    
    if(abs(x_))<dChL[iSec]['s']:
        dCh=0.0
        return dCh
    
    while (abs(x_))>=dChL[iSec]['s'] and iSec<iSecMax:
        iSec+=1

    # we are positioned in between iSec & iSec-1
        
    ds=dChL[iSec]['s']-dChL[iSec-1]['s']
    sloc=(x_-dChL[iSec-1]['s'])/ds
    dyloc=(dChL[iSec]['dy']-dChL[iSec-1]['dy'])
    dCh=dChL[iSec-1]['dy']+sloc*dyloc

    return dCh






class WingFromSections:

    def __init__(self, cDict, leIdx, baseSectionsL, halfSpanMax, ellipseA, ellipseB, dChL):
        self.baseSectionsL=baseSectionsL
        self.cDict=cDict
        self.leIdx=leIdx     # for morphed profiles, le necessarily is the same
        self.halfSpanMax=halfSpanMax
        self.a=ellipseA
        self.b=ellipseB
        self.dChL=dChL
        
        self.sectionsChL=[]
        
        self.initChPerSection()
        
    def ch4span(self,s):
        ch_=ellipsePoint(self.a,self.b,s)*2.0
        chEx_=chordExtensionLinear([ch_], [s], self.dChL)
        return chEx_[0]

    
    def initChPerSection(self):
        #import ipdb
        #ipdb.set_trace()
        #ipdb.set_trace(context=5)

        for i in range(0,len(self.baseSectionsL)):
            self.sectionsChL.append(self.ch4span(self.baseSectionsL[i]["s"]))

    
        
    def coords(self,quality,scale,shiftV):
        #miminc the original interface; quality not necessary here
        #shiftV[0] is the span position
        #scale is the local ch
        localCh=scale
        
        # span position
        s=abs(shiftV[0])

    
        #sanity check:
        if s<0.0 or s>self.halfSpanMax:
            raise Exception('Span position out of range. Should be between 0 and halspanMax, is: '+str(s))
        
        # determine relevant sections
        iSecMax=len(self.baseSectionsL)-1
        iSec=0

        while s>=self.baseSectionsL[iSec]["s"] and iSec<iSecMax:
            iSec+=1


        #we are between iSec-1 and iSec, except for the outermost position

        ds=self.baseSectionsL[iSec]['s']-self.baseSectionsL[iSec-1]['s']
        sRel=(s-self.baseSectionsL[iSec-1]['s'])/ds

        dCh=self.sectionsChL[iSec]-self.sectionsChL[iSec-1]
        chRel=(localCh-self.sectionsChL[iSec-1])/dCh

        tAi=self.baseSectionsL[iSec-1]['tA']
        dtA=self.baseSectionsL[iSec]['tA']-self.baseSectionsL[iSec-1]['tA']

        # twist angle is linear
        #print("Angle debug "+str(tAi)+" "+str(dtA)+" "+str(sRel))
        tA_=tAi+dtA*sRel
        #print("Angle "+str(tA_))
        #print(shiftV[0])
        
        #if not morphed take inner profile
        tMorph=self.baseSectionsL[iSec-1]['tMorph']
        mt=self.baseSectionsL[iSec-1]['morphT']
        if not tMorph:
            c=np.copy(self.cDict[ self.baseSectionsL[iSec-1]['p'] ])
        else:
            ci=self.cDict[ self.baseSectionsL[iSec-1]['p'] ]
            co=self.cDict[ self.baseSectionsL[iSec]['p'] ]

            if mt=='lS':
                fact=sRel
            elif mt=='lCh':
                fact=chRel
            else:
                raise Exception('morphType unknown: '+BSectionL[i].morphType)
            
            if(fact>1):
                raise Exception('unrealistic fact')

            cdelta=co-ci
            c=ci+fact*cdelta #morphed profile   


        #=== apply twist angle

        RM=rotMatrix2D(tA_)

        # get 2D coords relative to COG
        #cRot=np.copy(c)
        y=c[:,1]
        z=c[:,2]
    
        cogy=sum(y)/len(y)
        cogz=sum(z)/len(z)
    
        y_=y-cogy
        z_=z-cogz
    
    
        rotyz=np.dot(RM, np.array([y_,z_])).T
    
        c[:,1]=rotyz[:,0]+cogy
        c[:,2]=rotyz[:,1]+cogz
    


        # scale & shift
        c=scale*c+shiftV

        return c


    def leadingEdgeIdx(quality):
        # old style intergace, quality not reuqired here
        
        return self.leIdx
 
            
            
    #def func4Le()



def rotMatrix2D(alpha):
    theta = np.radians(alpha)
    c, s = np.cos(theta), np.sin(theta)
    RM = np.array(((c, -s), (s, c)))
    return RM
