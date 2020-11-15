#MIT License
#Copyright 2020 Alexander Poddey
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# foild data h105, e.g. used in kite hydrofoils
# see also https://m-selig.ae.illinois.edu/ads/coord_database.html
# if you are looking for 2d airfoil data

# quality might be 'full', 'medium', 'low'. Note in blender we will fit a bezier curve through the points,
# therfore a medium number of points is typically sufficcinet. Otherwsize the 3D mesh might get impractically large!
#
# scale: scaling factor appiled to the 2d profile. It is by default of chordlenght 1
#
# shiftV: [dx,dy,dz] added to the profile. allows you to place the leading edge where you need it
#
# The 2d profile starts ath the trailing edge (@ y=-1, goes over positive z to the leading edge and in negative z back again)
#
#
import math
import numpy as np


def coords(quality,scale,shiftV):

    if(quality=='low'):

        coords=scale*np.array([
                [0.0,-1.0000000000,-0.0009960075],
                [0.0,-0.9923910747,0.0008730353 ],
                [0.0,-0.9732261933,0.0061049655 ],
                [0.0,-0.9028826756,0.0228094365 ],
                [0.0,-0.5656912247,0.0715014889 ],
                [0.0,-0.1135761203,0.0489492481 ],
                [0.0,-0.0035325422,0.0069703941 ],
                [0.0,-0.0000000000,0.0000000000 ],
                [0.0,-0.0109729439,-0.0106883099],
                [0.0,-0.2435759130,-0.0497218477],
                [0.0,-0.8109499838,-0.0136364597],
                [0.0,-0.9842246660,-0.0002785008],
                [0.0,-0.9960683709,-0.0007296290]])+shiftV

    elif(quality=='medium'):

        coords=scale*np.array([
                [0.0,-1.0000000000,-0.0009960075],
                [0.0,-0.9968850158,-0.0002131417],
                [0.0,-0.9923910747,0.0008730353 ],
                [0.0,-0.9841079235,0.0032235503 ],
                [0.0,-0.9732261933,0.0061049655 ],
                [0.0,-0.9494646214,0.0120285280 ],
                [0.0,-0.9028826756,0.0228094365 ],
                [0.0,-0.7465577106,0.0520873754 ],
                [0.0,-0.5656912247,0.0715014889 ],
                [0.0,-0.3662695884,0.0746947582 ],
                [0.0,-0.1135761203,0.0489492481 ],
                [0.0,-0.0228438073,0.0207011579 ],
                [0.0,-0.0035325422,0.0069703941 ],
                [0.0,-0.0000000000,0.0000000000 ],
                [0.0,-0.0109729439,-0.0106883099],
                [0.0,-0.0555936001,-0.0264323653],
                [0.0,-0.2435759130,-0.0497218477],
                [0.0,-0.6224089664,-0.0347331559],
                [0.0,-0.8109499838,-0.0136364597],
                [0.0,-0.9368195370,-0.0013936882],
                [0.0,-0.9842246660,-0.0002785008],
                [0.0,-0.9960683709,-0.0007296290]])+shiftV

    elif(quality=='full'):

         coords=scale*np.array([
             [0.0,-1.0000000000,-0.0009960075],
             [0.0,-0.9985935200,-0.0006149232],
             [0.0,-0.9968850158,-0.0002131417],
             [0.0,-0.9951139440,0.0001954728],
             [0.0,-0.9923910747,0.0008730353],
             [0.0,-0.9877064000,0.0022096313],
             [0.0,-0.9841079235,0.0032235503],
             [0.0,-0.9811378883,0.0040339452],
             [0.0,-0.9732261933,0.0061049655],
             [0.0,-0.9647837205,0.0082489393],
             [0.0,-0.9494646214,0.0120285280],
             [0.0,-0.9337921506,0.0157624231],
             [0.0,-0.9028826756,0.0228094365],
             [0.0,-0.8716083152,0.0295373230],
             [0.0,-0.7465577106,0.0520873754],
             [0.0,-0.6198954787,0.0673448987],
             [0.0,-0.5656912247,0.0715014889],
            [0.0,-0.4934923822,0.0748201585],
            [0.0,-0.3662695884,0.0746947582],
            [0.0,-0.2393107074,0.0669299906],
            [0.0,-0.1135761203,0.0489492481],
            [0.0,-0.0521667932,0.0328311511],
            [0.0,-0.0228438073,0.0207011579],
            [0.0,-0.0093579649,0.0123437380],
            [0.0,-0.0035325422,0.0069703941],
            [0.0,-0.0012470218,0.0037286759],
            [0.0,-0.0000000000,0.0000000000],
            [0.0,-0.0043974551,-0.0063181004],
            [0.0,-0.0109729439,-0.0106883099],
            [0.0,-0.0253807399,-0.0171629081],
            [0.0,-0.0555936001,-0.0264323653],
            [0.0,-0.1176532453,-0.0384562654],
            [0.0,-0.2435759130,-0.0497218477],
            [0.0,-0.4963743180,-0.0452752572],
            [0.0,-0.6224089664,-0.0347331559],
            [0.0,-0.7481393672,-0.0209950917],
            [0.0,-0.8109499838,-0.0136364597],
            [0.0,-0.8738063334,-0.0066838808],
            [0.0,-0.9368195370,-0.0013936882],
            [0.0,-0.9684147503,-0.0002390124],
            [0.0,-0.9842246660,-0.0002785008],
            [0.0,-0.9921268565,-0.0004420069],
            [0.0,-0.9960683709,-0.0007296290]])+shiftV
    else:
        raise Exception("unknown quality") 
     

    return coords        

#---------------------------------------------


# Returns the index of the leading edge per quality
# As explained above, the leadingedge is at [0,0,0]
#@staticmethod
def leadingEdgeIdx(quality):

    if(quality=='low'):
        idx=7
    elif(quality=='medium'):
        idx=13
    elif(quality=='full'):
        idx=26
    else:
        raise Exception("unknown quality") 

    return idx
 
