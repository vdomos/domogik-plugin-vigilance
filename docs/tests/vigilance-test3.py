#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import sys
import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
import traceback
from xml.dom import minidom

'''
<CV><EV dateinsert="20161116170000" dateprevue="20161117160000" daterun="20161116165900" echeance="23" noversion="2" producteur="DP" typeprev="1" crueint="99,2A,2B,22,74"/>
<DV dep="01" coul="1"/>
<DV dep="02" coul="1"/>
<DV dep="03" coul="1"/>
<DV dep="04" coul="1"/>
<DV dep="05" coul="1"/>
<DV dep="06" coul="1"/>
<DV dep="0610" coul="1"/>
<DV dep="07" coul="1"/>
<DV dep="08" coul="1"/>
<DV dep="09" coul="1"/>
...
<DV dep="60" coul="1"/>
<DV dep="61" coul="1"/>
<DV dep="62" coul="2"><risque val="2"/></DV>
<DV dep="6210" coul="2"><risque val="9"/></DV>
<DV dep="63" coul="1"/><DV dep="64" coul="1"/>
<DV dep="6410" coul="1"/><DV dep="65" coul="1"/>
...
<DV dep="95" coul="1"/>
<DV dep="99" coul="1"/></CV>

'''
url = 'http://vigilance.meteofrance.com/data/NXFR33_LFPW_.xml'
risklong = ["aucun", "vent", "pluie-inondation", "orages", "inondations", "neige-verglas", "canicule", "grand-froid", "avalanche", "vague de submersion"]
colorlist = ["gris", "vert", "jaune", "orange", "rouge"]    # gris pour les départements sans cours d'eau à risques 

try:
    if len(sys.argv) > 1:
        xmldata = sys.argv[1]
    else:
        xmldata = urllib2.urlopen(url)
  
    dom = minidom.parse(xmldata)
except HTTPError, err:
    print u"API GET '%s', HTTPError code: %d" % (url, err.code)
except URLError, err:
    print u"API GET '%s', URLError reason: %s" % (url, err.reason)
except:
    print u"API GET '%s', Unknown error: '%s'" % (url, (traceback.format_exc()))
else:
    for all in dom.getElementsByTagName('DV'):
        depart = all.attributes['dep'].value
        colornumber = all.attributes['coul'].value
        #print "Depart = '%s', Couleur = '%s'" % (depart, colornumber)
        if colornumber != "1":
            risks = ""
            color = ""
            for risk in all.getElementsByTagName('risque'):
                risks = risks + risklong[int(risk.attributes['val'].value)] + ", "
            color = colorlist[int(colornumber)]
            print u"Departement '%s':  Couleur = '%s', Risque = '%s'" % (depart, color, risks) 




