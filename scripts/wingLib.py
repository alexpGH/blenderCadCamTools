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
    
    print
    return x,y

#---------------------------------------------
def elipticShift(x,y, dyMax, xFactStart,dirFact):
    thick=0.0
    ysh=np.copy(y)
    xmax=np.max(x)
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
def powerShift(x,y, p, dyMax, xFactStart):
    ysh=powerShiftDir(x,y,p,dyMax, xFactStart,1.0) # dirfact fix
    return ysh    


def powerShiftDir(x,y, p, dyMax, xFactStart,dirFact):
    thick=0.0 # formerly used for reducing the geometry (e.g. for laminating) new version uses shrink
              # in placeSetcions
    ysh=np.copy(y)
    xmax=np.max(x)
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
    

def plotArray(x,y,title,legend,outfile):
    print("##################### Plotting ##################")
    fig=plt.figure()
    ax= fig.add_subplot(111)
    ax.plot(x,y)
    ax.legend(legend)
    
    plt.title(title)
    plt.grid(True)

    fig.savefig(outfile)
