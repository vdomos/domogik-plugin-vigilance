# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

Vigilance 

Implements
==========

- Vigilance

@author: domos  (domos dt vesta at gmail dt com)
@copyright: (C) 2007-2016 Domogik project
@license: GPL(v3)
@organization: Domogik


Départements concernés par le risque 'Vague de submersion':
Depart = '0610', Couleur = '1'
Depart = '1110', Couleur = '1'
Depart = '1310', Couleur = '1'
Depart = '1410', Couleur = '1'
Depart = '1710', Couleur = '1'
Depart = '2210', Couleur = '1'
Depart = '2910', Couleur = '1'
Depart = '2A10', Couleur = '1'
Depart = '2B10', Couleur = '1'
Depart = '3010', Couleur = '1'
Depart = '3310', Couleur = '1'
Depart = '3410', Couleur = '1'
Depart = '3510', Couleur = '1'
Depart = '4010', Couleur = '1'
Depart = '4410', Couleur = '1'
Depart = '5010', Couleur = '1'
Depart = '5610', Couleur = '1'
Depart = '5910', Couleur = '1'
Depart = '6210', Couleur = '2'
Depart = '6410', Couleur = '1'
Depart = '6610', Couleur = '1'
Depart = '7610', Couleur = '1'
Depart = '8010', Couleur = '2'
Depart = '8310', Couleur = '1'
Depart = '8510', Couleur = '1'

Cas couleur "département" > couleur "Vague-Submersion":
    <DV dep="76" coul="2">
        <risque val="3"/>
        <risque val="1"/>
    </DV>
    <DV dep="7610" coul="1"/>
 

Cas couleur "Vague-Submersion" > couleur "département"
<DV dep="33" coul="1"/>
<DV dep="3310" coul="2">
    <risque val="9"/>
</DV>  

A voir si un départemnet10 peut avoir d'autre risque que le '9' (Vague Submersion) ?
 
Vigilance orange département 62:
NXFR33_LFPW_.xml
----------------
<DV dep="62" coul="3">
    <risque val="2"/>
</DV>
<DV dep="62" coul="2">
    <risque val="1"/>
    <risque val="4"/>
    <risque val="3"/>
</DV>
<DV dep="6210" coul="2">
    <risque val="9"/>
</DV>

NXFR34_LFPW_.xml
----------------
<datavigilance couleur="3" dep="62">
    <risque valeur="2"/>
    <crue valeur="2"/>
</datavigilance>
<datavigilance couleur="2" dep="6210"/>


http://vigilance.meteofrance.com/data/WXQQ62_LFPW_.xml
------------------------------------------------------
...
<Datevigilance>Emis le : vendredi 18 novembre 2016 à  10h56 </Datevigilance>
...


"""

import traceback
import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
from xml.dom import minidom
from datetime import datetime


class VigilanceException(Exception):
    """
    Vigilance exception
    """

    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)


class Vigilance:
    """ Vigilance
    """

    def __init__(self, log, send, stop, device_id, dep):
        """ Init Vigilance object
            @param log : log instance
            @param send : send
            @param stop : stop flag
            @param device_id : domogik device id
            @param dep : departement ID
        """
        self.log = log
        self.device_id = device_id
        self.dep = dep
        self._send = send
        self._stop = stop


    def check(self):
        """ Get weather vigilance
        """
        while not self._stop.isSet():
            self.log.debug(u"==> Get weather vigilance for '%s' 'departement'" % (self.dep))
            info, colors, risk = self.getvigilance(self.dep)
            
            if colors != "error":
                self.log.info(u"==> Vigilance for 'departement' '%s' : '%s' (risk = '%s')" % (self.dep, colors, risk))
                self._send(self.device_id, self.dep, colors, risk, info)
            else:
                self.log.warning(u"### Error getting vigilance for 'departement' '%s'" % self.dep)
                
            self._stop.wait(300)


    def getvigilance(self, deprequest):
        '''
        Inspired from GuiguiAbloc'code: http://api.domogeek.fr
        '''
        url = 'http://vigilance.meteofrance.com/data/NXFR33_LFPW_.xml'      # 'http://vigilance.meteofrance.com/data/NXFR34_LFPW_.xml'
        risklong = ["", "Wind", "Rain", "Thunderstorms", "Flood", "Snow/ice", "Heat wave", "Intense cold", "Avalanches", "Submersion wave"]
        colorlist = ["E0E0D1", "28D661", "FFFF00", "FFC400", "FF0000"]      # ["grey", "green", "yellow", "orange", "red"]

        if deprequest == "92" or deprequest == "93" or deprequest == "94": deprequest = "75"
        if deprequest == "20": deprequest = "2A"
        try:
            xmldata = urllib2.urlopen(url)
            #xmldata = "/var/lib/domogik/domogik_packages/plugin_vigilance/docs/tests//NXFR33_LFPW_.xml"
            dom = minidom.parse(xmldata)
        except HTTPError, err:
            self.log.error(u"API GET '%s', HTTPError code: %d" % (url, err.code))
            return "error", "", ""
        except URLError, err:
            self.log.error(u"API GET '%s', URLError reason: %s" % (url, err.reason))
            return "error", "", ""
        except:
            self.log.error(u"API GET '%s', Unknown error: '%s'" % (url, (traceback.format_exc())))
            return "error", "", ""
        else:
            vigiColor = ""
            vigiColors = ["1", "1", "1", "1", "1", "1", "1", "1", "1", "1"]     # Contient couleur pour chaque risque, vigiColors[0]  = couleur global (max), vigiColors[1] = "2" ==> Vigilance "Vent" = couleur Jaune
            vigiRisks = ["", "No vigilance,", "", "", ""]                       # Contient risques texte pour chaque couleur et seul le risque de la couleur max sera affiché
            
            for ev in dom.getElementsByTagName('EV'):
                dateinsert = ev.attributes['dateinsert'].value
                #vigiInfo = datetime.strptime(dateinsert, "%Y%m%d%H%M%S").strftime("%d/%m/%Y %H:%M:%S")
                vigiInfo = dateinsert
            
            for dv in dom.getElementsByTagName('DV'):
                departement = dv.attributes['dep'].value
                if departement == deprequest  or  departement == deprequest + "10":
                    vigiColor = dv.attributes['coul'].value 
                    if vigiColor != "1":
                        if int(vigiColor) > int(vigiColors[0]):  vigiColors[0] = vigiColor
                        for risk in dv.getElementsByTagName('risque'):
                            riskValue = int(risk.attributes['val'].value)
                            vigiColors[riskValue] = vigiColor
                            vigiRisks[int(vigiColor)] = vigiRisks[int(vigiColor)] + risklong[riskValue] + ","
                            self.log.debug(u"==> Vigilance for '%s' = '%s' with risk '%s'" % (departement, vigiColor, risklong[riskValue]))
                 
            if vigiColor:
                risks = vigiRisks[int(vigiColors[0])]   # Seul le risque de la couleur max sera affiché
                risks = risks[0:-1]                     # Delete last ','
                for idx, item in enumerate(vigiColors):
                    vigiColors[idx] = colorlist[int(item)]
                return vigiInfo, vigiColors, risks
            else:
                return "", vigiColors, "Unknow departement"


