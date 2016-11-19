#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import ClassVigilance


vigilancerequest = ClassVigilance.vigilance()   # http://vigilance.meteofrance.com/data/NXFR34_LFPW_.xml
                                                # http://vigilance.meteofrance.com/data/QGFR08_LFPW_.gif

dep = "78"

if dep == "92" or dep == "93" or dep == "94":
    dep = "75"
if dep == "20":
    dep = "2A"

result = vigilancerequest.getvigilance(dep)
color =  result[0]
risk =  result[1]
flood =  result[2]
print "Vigilance '%s': Couleur = '%s', Risque = '%s'" % (dep, color, risk) 
print "Vigilance '%s': Couleur inondation = '%s'" % (dep, flood)
