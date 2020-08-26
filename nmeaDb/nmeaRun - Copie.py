#!/python
# -*- coding: utf-8 -*-

### http://sametmax.com/lencoding-en-python-une-bonne-fois-pour-toute/
from __future__ import unicode_literals

"""
Importer les phrases NMEA 0183 dans la base de donnees
$IIVLW,0088.0,N,088.65,N*4E
$IIVHW,,,268.,M,01.44,N,02.66,K*10
"""

import cgitb
cgitb.enable(format='text')
import pyodbc
import sqlite3
import hashlib
import sys
import os
#import string
import pathlib
import argparse
import configparser
import re
#from collections import OrderedDict
import collections
import time
# Passage en UTC (sinon == -3600)
time.timezone = 0
import datetime
import decimal

decimal.getcontext().prec = 2
TAB = '\t'
FileOutSep = TAB
FileOutHeader = False
Verbose = True
#dIni['verbose'] = Verbose
dtNow  = datetime.datetime.today()
tsNow = dtNow.timestamp()

def average(lst):
    l = len(lst)
    if (l == 0) :
        return 0
    if (l == 1) :
        return lst[0]
    return sum(lst) / len(lst)

def forgeDict() : 
    # NKE 90-60-357 interface Intercom --> NMEA
    d = dict()
    d['lat'] = set()
    d['lon'] = set()
    d['tsEpoch'] = set()
    #d[''] = list()
    d['compas'] = list()
    d['HDM'] = list()
    d['speedo'] = list()
    d['COG'] = list()
    d['SOG'] = list()
    d['DPT'] = list()
    d['MTW'] = list()
    d['AWA'] = list()
    d['AWS'] = list()
    d['TWS'] = list()
    d['TWD'] = list()
    d['TWA'] = list()
    d['MTA'] = list()
    d['XTE'] = list()
    # d['IIVHW'] = list()
    # d['IIVLW'] = list()
    # d['IIDPT'] = list()
    # d['IIDBT'] = list()
    # d['IIMTW'] = list()
    # d['IIVWR'] = list()
    # d['IIMWD'] = list()
    # d['IIVWT'] = list()
    # d['IIMTA'] = list()
    # d['IIHDG'] = list()
    # d['IIHDM'] = list()
    # d['IIXDR'] = list()
    # d['IIZDA'] = list()
    # d['IIGLL'] = list()
    # d['IIVTG'] = list()
    # d['IIXTE'] = list()
    # d['IIRMB'] = list()
    """
    AWA (Apparent Wind Angle) : angle du vent apparent. 
    AWS (Apparent Wind Speed) : La vitesse du vent apparent. 
    BRG  (Bearing to destination) : Cap à suivre pour aller au prochain point de destination. 
    BTW (Bearing to Waypoint) : Relèvement du prochain Waypoint. 
    COG = Course over Ground to the next waypoint (Cap sur le fond jusqu'au prochain waypoint)
    CDI  (Course Deviation Indicator) : couloir de navigation virtuel servant de repère au déplacement du bateau et permet d’éviter les écarts de route. 
    CMG (Course made good) : cap suivi depuis le départ. 
    COG (Course Over Ground) : cap suivi sur le fond. 
    DPT (Depth) : Profondeur. 
    DTW (Distance to Waypoint) : Distance jusqu’au prochain waypoints. 
    HDG (Heading) : Orientation du mobile, sans rapport avec son déplacement (cap du bateau) 
    MTW : Temperature eau
    SOG = Speed over Ground - inclu le courant prévu (Vitesse sur le fond)
    SPEEDO : Cette valeur correspond la vitesse surface du navire. 
    SST : Température d’eau.
    STA : Direction du courant.
    STR (Steering) : Différence entre le COG(cap vrai)et le CTS (cap optimum à suivre pour rejoindre la route initialement prévue) 
    STW (Speed True Water) : vitesse surface. 
    TWS = True Wind Speed (Vitesse du vent vrai)
    TWD = True Wind Direction (Direction du vent vrai)
    TWA = True Wind Angle – angle of the boat to the wind (Angle du vent vrai – angle du bateau par rapport au vent)
    VMG  (Velocity Made Good) : Vitesse d’approche au point  situé dans l’axe du vent 
    VMC  (Velocity Made of Course) : Vitesse de progression sur la route
    """
    return d

def feedDict(d, r) :
    ## Pour NKE 90-60-357 interface Topline --> NMEA
    for l in ret : 
        #SELECT lat, lon, tsEpoch, NmeaID, NmeaVal
        ## 4743.597	-321.014	1528427822
        d['lat'].add(l[0])
        d['lon'].add(l[1])
        d['tsEpoch'].add(l[2])
        i = l[3]
        v = l[4]
        if (i == "$IIVHW") :
            ## Vitesse surface et cap compas
            ## $IIVHW	,,003.,M,00.00,N,00.00,K*1C
            l_VHW = v.split(",")
            d['compas'].append(int(float(l_VHW[2])))
            d['speedo'].append(float(l_VHW[4]))
        # elif (i == "$IIVLW") :
            ## Loch total et journalier
            ## $IIVLW	0244.0,N,046.86,N*43
            # pass
        elif (i == "$IIDPT") :
            ## Profondeur
            ## $IIDPT	0002.8,,*78
            dpt = v[0: v.find(",")]
            d['DPT'].append(float(dpt))
            pass
        # elif (i == "$IIDBT") :
            ## Profondeur
            ## $IIDBT	0009.2,f,0002.8,M,,*78
            # pass
        elif (i == "$IIMTW") :
            ## Temperature eau
            ## $IIMTW	18.2,C*18
            mtw = v[0: v.find(",")]
            d['MTW'].append(float(mtw))
        elif (i == "$IIVWR") :
            ## Angle et vitesse vent apparent
            ## $IIVWR	022.,R,02.1,N,01.1,M,003.9,K*70
            l_VWR = v.split(",")
            # print(l_VWR[0], "\t", l_VWR[1], "\t", -float(l_VWR[0]), "\t", float("-" + l_VWR[0]))
            if (l_VWR[1] == "L") :
                d['AWA'].append(-int(float(l_VWR[0])))
            elif (l_VWR[1] == "R") :
                d['AWA'].append(int(float(l_VWR[0])))
            d['AWS'].append(float(l_VWR[2]))
        elif (i == "$IIMWD") :
            ## Direction et vitesse vent reel
            ## $IIMWD	,,025.,M,02.1,N,01.1,M*0A
            l_MWD = v.split(",")
            d['TWD'].append(int(float(l_MWD[2])))
            d['TWS'].append(float(l_MWD[4]))
        elif (i == "$IIVWT") :
            ## Angle et vitesse vent reel
            ## $IIVWT	022.,R,02.1,N,01.1,M,003.9,K*76
            vwt = v[0: v.find(",")]
            d['TWA'].append(int(float(vwt)))
        elif (i == "$IIMTA") :
            ## Temperature air
            ## $IIMTA	14.8,C*08
            mta = v[0: v.find(",")]
            d['MTA'].append(float(mta))
        # elif (i == "$IIHDG") :
            ## Compas magnetique $IIHDG	003.,,,,*7A
            # pass                 
        elif (i == "$IIHDM") :
            ## Compas magnetique $IIHDM	003.,M*11
            hdm = v[0: v.find(",")]
            d['HDM'].append(int(float(hdm)))
        # elif (i == "$IIHDT") :
            ## Compas vrai
            # pass
        # elif (i == "$IIMMB") :
            ## Barometre
            # pass
        # elif (i == "$IIXDR") :
            ## Angle de mat (et autres ?)
            # pass
        # elif (i == "$IIZDA") :
            ## Heure et date UTC $IIZDA	051702,08,06,2018,,*5B
            # pass
        # elif (i == "$IIGLL") :
            ## latitude longitude $IIGLL	4743.597,N,00321.014,W,051704,A,A*4F
            # pass
        elif (i == "$IIVTG") :
            ## Ca et vitesse fond $IIVTG	351.,T,,M,00.0,N,00.0,K,A*2D
            l_VTG = v.split(",")
            # cog = int(float(l_VTG[0]))
            # sog = float(l_VTG[4])
            d['COG'].append(int(float(l_VTG[0])))
            d['SOG'].append(float(l_VTG[4]))
            pass
        # elif (i == "$IIMWV") :
            ##  $IIMWV	022,R,02.1,N,A*10
            """MWV - Wind Speed and Angle
                    1   2 3   4 5
                    |   | |   | |
             $--MWV,x.x,a,x.x,a*hh<CR><LF>
                Wind Angle, 0 to 360 degrees
                Reference, R = Relative, T = True
                Wind Speed
                Wind Speed Units, K/M/N
                Status, A = Data Valid """
            # pass
        elif (i == "$IIXTE") :
            ## Ecart de route $IIXTE	A,A,0.58,R,N,A,*2B
            ##      $ECXTE	A,A,0.001,R,N*50
            l_XTE = v.split(",")
            # print(v[0:3], "\t", v[10:11], "\t", v[4:9], "\t", v)
            if (l_XTE[0] == "A" and l_XTE[1] == "A") : 
                if (l_XTE[3] == "L") : 
                    d['XTE'].append(-float(l_XTE[2]))
                elif(l_XTE[3] == "R") :
                    d['XTE'].append(float(l_XTE[2]))
            
        # elif (i == "$IIRMB") :
            ## Cap et distance au WP 
            ##      $ECRMB	A,0.001,R,,00_Dep,4740.523,N,00323.483,W,3.499,208.390,0.000,V*1D
            ##      $GPRMB  A,9.99,L,004,005,4725.5168,N,00229.2562,W,170.410,334.9,,V,A*65
            # pass
        # elif (i == "$TRWPL") :
            ## Homme a la mer (Transfert de WPL ?)
            # pass
        # elif (i == "$PMLR") :
            ## Homme a la mer
            # pass
        # elif (i == "$II") :
            ##
            # pass
            
    return

def distilDict(d) : 
    dCumul = forgeDict()
    for k, v in d.items() :
        nbr = len(v)
        # print("k =", k, "\t\t nbr =", nbr)
        ## Les MIN(), MAX() des lat, lon et tsEpoch 
        dCumul['lat'].add(min(d['lat']))
        dCumul['lat'].add(max(d['lat']))
        dCumul['lon'].add(min(d['lon']))
        dCumul['lon'].add(max(d['lon']))
        dCumul['tsEpoch'].add(min(d['tsEpoch']))
        dCumul['tsEpoch'].add(max(d['tsEpoch']))
        ##  
        dCumul['compas'] = int(average(d['compas']))
        dCumul['speedo'] = round(average(d['speedo']), 2)
        dCumul['DPT'] = round(average(d['DPT']), 2)
        dCumul['MTW'] = round(average(d['MTW']), 2)
        dCumul['AWA'] = int(average(d['AWA']))
        dCumul['AWS'] = round(average(d['AWS']), 2)
        dCumul['TWD'] = int(average(d['TWD']))
        dCumul['TWS'] = round(average(d['TWS']), 2)
        dCumul['TWA'] = int(average(d['TWA']))
        dCumul['MTA'] = round(average(d['MTA']), 2)
        dCumul['HDM'] = int(average(d['HDM']))
        dCumul['COG'] = int(average(d['COG']))
        dCumul['SOG'] = round(average(d['SOG']), 2)
        dCumul['XTE'] = round(average(d['XTE']), 2)
        ## Si demande, suppr des valeurs extremes
        # if (supprExtrem) :
            # if (len(d['compas']) > 10) :
                # d['compas'].sort()
                # pass
    return dCumul
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


#bShowIdentifier = os.getenv("dsXidentifier", False)

## fichier a traiter
me = sys.argv[0]
#args = sys.argv[1:]
if (len(sys.argv) != 4) :
    print(me + " : Pas le bon nombre de parametres.")
    print("Usage : " + me + "<Chemin et nom de la base Sqlite> <ID fichier> <pas>")
    quit()
else :
    nmeaDbname = sys.argv[1]
    fileID = sys.argv[2]
    step = sys.argv[3]
    print("I;Traitement du fichier NMEA [" + fileID + "] dans la base Sqlite [" + nmeaDbname + "] par un pas de [" + step + "] secondes")

## Verifications prealables
if (not os.path.exists(nmeaDbname)) :
    print("E:Base", nmeaDbname, "introuvable")
    quit()
if (not fileID.isnumeric()) :
    print("E:L'ID du fichier doit etre un entier")
    quit()
if (not step.isnumeric()) :
    print("E:Le pas doit etre un entier")
    quit()
else :
    step = int(step)
try :
    db = sqlite3.connect(nmeaDbname)
    cursor = db.cursor()
    cursor.execute("SELECT MIN(tsEpoch) AS ""Min"", MAX(tsEpoch) AS ""Max"" FROM nmeaValues WHERE FileID = " + str(fileID) + " AND tsEpoch IS NOT NULL")
    ret = cursor.fetchone()
    if (ret[0] == None) :
        print("E;Le FileID [" + fileID + "] est introuvable")
        quit()
    else :
        tsMin = int(ret[0])
        tsMax = int(ret[1])
except Exception as e :
    print("E:Pb avec la DB [" + nmeaDbname + "]")
    db.close()
    quit()

supprExtrem = True    
    
## Boucle d'exploration, suivant le pas d'analyse
tsDebut = tsMin
tsFin   = tsDebut + step
lTsCumul = list()
dTs = forgeDict()
print("\t".join(dTs.keys()))    
while (tsFin <= tsMax) :
    dTs = forgeDict()
    cursor.execute("SELECT lat, lon, tsEpoch, NmeaID, NmeaVal FROM nmeaValues WHERE FileID = " + str(fileID) + " AND tsEpoch BETWEEN " +str(tsDebut) + " AND " + str(tsFin))
    ret = cursor.fetchall()
    # print(len(ret))
    feedDict(dTs, ret)
    lTsCumul.append(distilDict(dTs))
    
    tsDebut = tsFin
    tsFin = tsDebut + step

# print(ret)
print(dTs['compas'])
print(lTsCumul[-1])
        