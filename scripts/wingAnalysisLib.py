#MIT License
#Copyright 2020 Alexander Poddey
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from __future__ import division      
import bpy
import math
import numpy as np
import matplotlib.pyplot as plt

import mathutils

from dataclasses import dataclass
from bs4 import BeautifulSoup

import wingLib

@dataclass
class BaseSection:
    profile: str     #inner profile outer will be the inner of the next in list
    fromSpan: float  # from wher on wards in % of span 
    twist: float     #
    nSub: int        # how many subsections to add
    yNumPfact: float # scale the given panelsPerMeter by this value
    tMorphSub: bool  #
    morphType: str='lS' #
    addCh: float=0.0  # for over /underelliptic chordlenght

    
#=================================================================================================
#The basic explane tree to which we will add sections
#=================================================================================================
def buildXPlaneTree():

    markup='''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE explane>
<explane version="1.0">
    <Units>
        <length_unit_to_meter>1</length_unit_to_meter>
        <mass_unit_to_kg>1</mass_unit_to_kg>
    </Units>
    <Plane>
        <Name>BlenderExportedPlane</Name>
        <Description></Description>
        <Inertia/>
        <has_body>false</has_body>
        <wing>
            <Name>Main Wing</Name>
            <Type>MAINWING</Type>
            <Color>
                <red>34</red>
                <green>168</green>
                <blue>252</blue>
                <alpha>255</alpha>
            </Color>
            <Description></Description>
            <Position>          0,           0,           0</Position>
            <Tilt_angle>  0.000</Tilt_angle>
            <Symetric>true</Symetric>
            <isFin>false</isFin>
            <isDoubleFin>false</isDoubleFin>
            <isSymFin>false</isSymFin>
            <Inertia>
                <Volume_Mass>  0.000</Volume_Mass>
            </Inertia>
            <Sections>
            </Sections>
        </wing>
    </Plane>
</explane>
'''
    
    #Note: this converts all tags to lowercase (which works for xlfr5)
    #soup = BeautifulSoup(markup, 'xml')    
    soup = BeautifulSoup(markup, 'html.parser')    

    return soup



#=================================================================================================
# Adds a section to the explane tree fo xlfr5
# Note xflr5 has a bug: it can not read inverse sine
#=================================================================================================
def xPlaneAddSection(soup, y, ch, xoff, di, tw, xnum, xdist, ynum, ydist, leftfoil, rightfoil):

    Sections=soup.explane.plane.wing.sections


    Section = soup.new_tag("section")
    Sections.append(Section)
        
    t=soup.new_tag("y_position")
    t.string=str(y)
    Section.append(t)

    t=soup.new_tag("chord")
    t.string=str(ch)
    Section.append(t)

    t=soup.new_tag("xoffset")
    t.string=str(xoff)
    Section.append(t)
    
    t=soup.new_tag("dihedral")
    t.string=str(di)
    Section.append(t)
    
    t=soup.new_tag("twist")
    t.string=str(tw)
    Section.append(t)
    
    t=soup.new_tag("x_number_of_panels")
    t.string=str(xnum)
    Section.append(t)
    
    t=soup.new_tag("x_panel_distribution")
    t.string=xdist
    Section.append(t)
    
    t=soup.new_tag("y_number_of_panels")
    t.string=str(ynum)
    Section.append(t)
    
    t=soup.new_tag("y_panel_distribution")
    t.string=ydist
    Section.append(t)
    
    t=soup.new_tag("left_side_foilname")
    t.string=leftfoil
    Section.append(t)
    
    t=soup.new_tag("right_side_foilname")
    t.string=rightfoil
    Section.append(t)
    
    return soup


#=================================================================================================
# yNumPperM= number of panesl per m
#=================================================================================================
def xPlaneAddSectionsElliptic(soup, LeShiftL, BSectionL, span, ch4Ellipse, xNumPanels, yNumPperM, roundTo):
    
    halfspan=span/2.0

    a=halfspan
    b=ch4Ellipse/2.0

    factL=[]

    
    # check num of sections
    nsec=len(BSectionL)
    if nsec<2:
        raise Exception('We can not build wing with only one section')

    iRegion=0
    # loop over main sections
    for i in range(0,nsec):

        print("==== SECTION: "+str(i))
        
        factLSec=[]
        
        tMorph=BSectionL[i].tMorphSub

        # y panel scale factor
        ySc=BSectionL[i].yNumPfact
        
        # inner position
        si=BSectionL[i].fromSpan
        ti=BSectionL[i].twist

        # span sposition and chord for inner section (convert outer % span position to abs position)
        yi=si*halfspan/100.0 #note xlfr5's y is our x!
        chi=2.0*wingLib.ellipsePoint(a,b,yi)#note xlfr5's y is our x!

        #apply ch scaling
        scChi=BSectionL[i].addCh
        chi=chi+scChi
        #print(chi)
        
        # not the last section (which is the end of the wing)
        if i != (nsec-1):
            so=BSectionL[i+1].fromSpan
            to=BSectionL[i+1].twist
            scCho=BSectionL[i+1].addCh
            #print('Scaling outer: '+str(scCho))
            
            if tMorph:
                # span sposition and chord for outer section (convert outer % span position to abs position)
                yo=so*halfspan/100.0 #note xlfr5's y is our x!
                cho=2.0*wingLib.ellipsePoint(a,b,yo)#note xlfr5's y is our x!

                #apply ch scaling
                cho=cho+scCho

        else:
            so=BSectionL[i].fromSpan
            to=BSectionL[i].twist
            scCho=BSectionL[i].addCh
            
        
        nSub=BSectionL[i].nSub
        ds=(so-si)/(nSub+1)
        dt=(to-ti)/(nSub+1)

        dScCh=(scCho-scChi)/(nSub+1)
        #print("dScCh= "+str(dScCh))
        
        for iSub in range(0,nSub+1):

            iRegion+=1
            print("===================== iSub, Region: "+str(iSub)+" "+str(iRegion))
            
            # convert % span position to abs position
            y=(si+iSub*ds)*halfspan/100.0 #note xlfr5's y is our x!
            x=wingLib.ellipsePoint(a,b,y)#note xlfr5's y is our x!
            ch=2.0*x

            # apply additive ch 
            print(ch)
            ch=(scChi+iSub*dScCh)+ch
            print("Scaling: "+str(scChi)+" "+str(iSub)+" "+str(dScCh))
            print(ch)
            
            # shift leading edge to correct position
            xsh=wingLib.applyLeShifts([y],[x], LeShiftL)#note xlfr5's y is our x!
            xoff=-xsh[0] #offset is defined positive in xflr5
                
            di=0.0

            
            # morph or not
            if not tMorph:
                tw=ti+iSub*dt

                #xlfr5 takes 2 x the same
                leftfoil=BSectionL[i].profile
                rightfoil=leftfoil

            else:
                mt=BSectionL[i].morphType
                
                if mt=='lS':
                    fact=(y-yi)/(yo-yi)
                elif mt=='lCh':
                    fact=(ch-chi)/(cho-chi)
                else:
                    raise Exception('morphType unknown: '+BSectionL[i].morphType)

                if(fact>1):
                    print(ch)
                    print(chi)
                    print(cho)
                    print(scCho)
                    raise Exception('unrealistic fact')
                
                # keep for factL
                factLSec.append(fact)

                # twist
                tw=ti+fact*(to-ti)

                # profile morphing (if close to first or last, use that one instead)
                rFact=round(fact/roundTo)*roundTo
                print("======== rFact "+str(rFact)+" "+str(fact)+"")
                if abs(rFact)<roundTo:
                    leftfoil=BSectionL[i].profile
                elif abs(rFact-1.0)<roundTo:
                    leftfoil=BSectionL[i+1].profile
                else:
                    leftfoil=BSectionL[i].profile+BSectionL[i+1].profile+'_'+str(int(rFact*100.0))

                rightfoil=leftfoil

                
            xnum=xNumPanels
            xdist='COSINE' # should always be cosine for our applications

            ynum=max(1,int(ySc*yNumPperM*(halfspan*ds/100.0))) # at least 1 panel

            if iRegion==1:
                ydist='UNIFORM'
            elif iRegion==2:
                ydist='INVERSESINE'
            else:
                ydist='COSINE'
                
                
                
            # now add this (sub) section
            soup=xPlaneAddSection(soup, y,  ch,   xoff, di, tw  , xnum, xdist, ynum, ydist, leftfoil, rightfoil)

        # keep factLSec for this section
        factL.append(factLSec)
                


    return soup, factL
        
