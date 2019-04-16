#!/python
# -*- coding: utf-8 -*-

### http://sametmax.com/lencoding-en-python-une-bonne-fois-pour-toute/
from __future__ import unicode_literals
### https://www.systutorials.com/241727/how-to-print-a-line-to-stderr-and-stdout-in-python/
# Permet en python 2.7 print("your message", file=sys.stderr) comme en Python 3
from __future__ import print_function
# http://python-future.org/compatible_idioms.html#long-integers
from builtins import int
# from past.builtins import long

"""
Verification du fichier NMEA
pour en extraire les informations generales
Construire une structure de donnees,
liste ordonnee (clef = timestamp) de 
structure des informations dispo entre 2 timestamps

    Nom du fichier
    Md5 du fichier
    Dt de modif
    NMEA reference de temps
    Liste des tags NMEA
    Nombre de lignes
    Nombre de lignes valides
    Premiere reference de temps RMC
    Derniere reference de temps RMC
    Nombre reference de temps RMC
Delai moyen reference de temps RMC
Delai median reference de temps RMC
Duree reference de temps RMC
    Premiere reference de temps ZDA
    Derniere reference de temps ZDA
    Nombre reference de temps ZDA
Delai moyen reference de temps ZDA
Delai median reference de temps ZDA
Duree reference de temps ZDA
Coordonnees MIN et MAX
Premiere ligne en mouvement
Derniere ligne en mouvement

"""

# Pour calcul de distance...
from math import sin, cos, acos, pi

import cgitb
cgitb.enable(format='text')
import pyodbc
import sqlite3
import hashlib
### http://sweetohm.net/article/introduction-yaml.html
import yaml
### https://docs.python.org/fr/2/tutorial/inputoutput.html#reading-and-writing-files
### http://sametmax.com/faire-manger-du-datetime-a-json-en-python/
import json
import sys
import os
# import shutil
#import string
import pathlib
import argparse
import configparser
import re
#from collections import OrderedDict
import collections
import time
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
dt1970 = datetime.datetime(1970, 1, 1)

#bShowIdentifier = os.getenv("dsXidentifier", False)

## fichier a traiter
me = sys.argv[0]
#args = sys.argv[1:]
# message erreur de demarrage
usageMsg = "Usage : " + me + " <Chemin et nom du fichier NMEA> <nmea reference de temps (GPRMC, IIZDA, ..)> <nmea reference de position (GPRMC, IIGLL>"
if (len(sys.argv) != 4) :
    print(me + " : Pas le bon nombre de parametres.", file=sys.stderr)
    print(usageMsg, file=sys.stderr)
    quit()
else :
    nmeaFilename = sys.argv[1]
    srcEpoch = sys.argv[2]
    srcPosition = sys.argv[3]
    if (srcEpoch[0:1] == "$") :
        srcEpoch = srcEpoch[1:]
    srcEpoch = srcEpoch.upper()
    if (len(srcEpoch) == 5) :
        print("I;Reference de temps a partir de NMEA [" + srcEpoch + "] depuis le ficher NMEA [" + nmeaFilename + "]", file=sys.stderr)
    else :
        print(usageMsg, file=sys.stderr)
        quit()
    if (srcPosition[0:1] == "$") :
        srcPosition = srcPosition[1:]
    srcPosition = srcPosition.upper()
    if (len(srcPosition) == 5) :
        print("I;Reference de position a partir de NMEA [" + srcPosition + "] depuis le ficher NMEA [" + nmeaFilename + "]", file=sys.stderr)
    else :
        print(usageMsg, file=sys.stderr)
        quit()

## Tests prealables, fichier NMEA 
if (not os.path.exists(nmeaFilename)) :
    print("E:Fichier", nmeaFilename, "introuvable", file=sys.stderr)
    quit()

## TS ISO8601 epoch
iso8601 = time.strftime("%Y%m%d%H%M%S")
epoch = int(time.time())
# print(datetime.datetime.now().isoformat()) # 2017-10-31T10:52:02.101865
# print(time.strftime("%Y-%m-%d %H:%M:%S")) # 2017-10-31 10:52:02
# print(int(time.time())) # 1509443642

## Informations sur le fichier a importer
BLOCKSIZE = 65536
hasher = hashlib.md5()
with open(nmeaFilename, 'rb') as afile:
    buf = afile.read(BLOCKSIZE)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(BLOCKSIZE)
#print(hasher.hexdigest())
fileCheck = hasher.hexdigest()

mTimeEpoch = int(os.path.getmtime(nmeaFilename)) # format epoch
# print("mTimeEpoch : " + str(mTimeEpoch))
# print(datetime.datetime.utcfromtimestamp(mTimeEpoch)) # 2017-10-19 13:40:11
mTimeStruct = time.localtime(mTimeEpoch)
# print("mTimeStruct : " + str(mTimeStruct)) # mTimeLocal : time.struct_time(tm_year=2017, tm_mon=10, tm_mday=19, tm_hour=15, tm_min=40, tm_sec=11, tm_wday=3, tm_yday=292, tm_isdst=1)
mTimeIso = time.strftime("%Y%m%d%H%M%S", mTimeStruct)
# print("mTimeIso : " + mTimeIso)
basename = os.path.basename(nmeaFilename)

##
## (option) Timestamp en epoch au début et/ou en TS à la fin de chaque ligne NMEA
##

##  Place disponible (2 x la taille du fichier)
# nmeaFilenameSize = os.path.getsize(nmeaFilename)
nmeaFilenameName, nmeaFilenameExtension = os.path.splitext(nmeaFilename)
# print("", )
# shutil.copyfile(nmeaFilename, )

## Quelle information NMEA est la plus pertinente a utiliser ?
## RMC et ZDA
"""
$GPRMC,193428,A,4729.9205,N,00222.6770,W,0.0,143.5,200917,2.9,W,D*1C

       1         2 3       4 5        6 7   8   9    10  11|
       |         | |       | |        | |   |   |    |   | |
$--RMC,hhmmss.ss,A,llll.ll,a,yyyyy.yy,a,x.x,x.x,xxxx,x.x,a*hh
1) Time (UTC)
2) Status, V = Navigation receiver warning
3) Latitude
4) N or S
5) Longitude
6) E or W
7) Speed over ground, knots
8) Track made good, degrees true
9) Date, ddmmyy
10) Magnetic Variation, degrees
11) E or W
12) Checksum
$GPRMC	055827.000,A,4715,0596,N,131,7996,W,23,3,356,0,261115,,,N*43
$GPRMC	055927.000,A,4715,3027,N,131,7799,W,13,6,5,0,261115,,,N*4C

$IIZDA,hhmmss.ss,xx,xx,xxxx,,*hh
       I         I  I  I_Année
       I         I  I_Mois
       I         I_jour
       I_Heure
$IIZDA	194020,20,09,2017,,*5E
$IIZDA	152520,07,07,2017,,*5A

!AIVDM, !AIVDO, $AIALR, $AITXT
$GPAPB, $GPBOD, $GPGBS, $GPGGA, $GPGLL, $GPGSA, $GPGSV, $GPRMB, $GPRMC, $GPRTE, $GPTXT, $GPVTG, $GPWPL
$IIDBT, $IIDPT, $IIGLL, $IIHDG, $IIHDM, $IIMTA, $IIMTW, $IIMWD, $IIMWV, $IIVHW, $IIVLW, $IIVTG, $IIVWR, $IIVWT, $IIZDA
$PMGNS, $PSRT
"""
dJson = dict()
dJson['name'] = basename
dJson['check'] = fileCheck
dJson['mTime'] = mTimeIso
dJson['nmeaFilename'] = nmeaFilename

dRMCs = dict()
candidatVoulu = 'ZDA'

dPivots = dict()
# dLines = dict()
dPivotsSorted = collections.OrderedDict()
"""
!AIVDM, !AIVDO, $AIALR, $AITXT
$GPAPB, $GPBOD, $GPGBS, $GPGGA, $GPGLL, $GPGSA, $GPGSV, $GPRMB, $GPRMC, $GPRTE, $GPTXT, $GPVTG, $GPWPL
$IIDBT, $IIDPT, $IIGLL, $IIHDG, $IIHDM, $IIMTA, $IIMTW, $IIMWD, $IIMWV, $IIVHW, $IIVLW, $IIVTG, $IIVWR, $IIVWT, $IIZDA
$PMGNS, $PSRT
"""

def getDictEpoch() :
    dPivot = dict()
    dPivot['ts'] = None #0.0
    # dPivot['lat'] = None #0.0
    # dPivot['lon'] = None #0.0
    # dPivot['d-1'] = None #0
    # dPivot['d+10'] = None #0
    # dPivot['d+60'] = None #0
    # dPivot['ZDAepoch'] = None #0
    dPivot['ECAPB'] = None
    dPivot['GPAPB'] = None
    dPivot['BOD'] = None
    dPivot['DBT'] = None #0.0
    # dPivot['DPT'] = None
    # dPivot['HDG'] = None #0.0
    dPivot['HDM'] = None #0.0
    # dPivot['GBS'] = None
    # dPivot['GGA'] = None
    # dPivot['GLL'] = None #""
    dPivot['GLLlatNum'] = None #0.0
    dPivot['GLLlonNum'] = None #0.0
    # dPivot['GSA'] = None
    # dPivot['GSV'] = None
    # dPivot['HDG'] = None #0.0
    dPivot['HDM'] = None #0.0
    dPivot['MTA'] = None #0.0
    dPivot['MTW'] = None #0.0
    dPivot['MWD'] = None
    dPivot['MWDtws'] = None #0.0
    dPivot['MWDtwd'] = None #0.0
    dPivot['MWV'] = None
    dPivot['ECRMB'] = None
    dPivot['GPRMB'] = None
    # dPivot['RMC'] = None
    dPivot['GPRMCts'] = None #0
    dPivot['GPRMClatlon'] = None #""
    dPivot['GPRMClatNum'] = None #0.0
    dPivot['GPRMClonNum'] = None #0.0
    dPivot['GPRMCsog'] = None #0.0
    dPivot['GPRMCtmg'] = None #0.0
    # dPivot['RTE'] = None
    # dPivot['TXT'] = None
    dPivot['VHW'] = None
    dPivot['VLW'] = None #0.0
    dPivot['VLWtotal'] = None #0.0
    dPivot['VTG'] = None
    dPivot['VWR'] = None
    dPivot['VWRrl'] = None #""
    dPivot['VWRawa'] = None #0.0
    dPivot['VWRaws'] = None #0.0
    dPivot['VWT'] = None
    dPivot['VWTrl'] = None #""
    dPivot['VWTtwa'] = None #0.0
    dPivot['VWTtws'] = None #0.0
    # dPivot['WPL'] = None
    dPivot['ZDA'] = None
    # dPivot[''] = None
    # dPivot[''] = None
    # dPivot[''] = None
    # dPivot[''] = None
    # dPivot[''] = None
    # dPivot[''] = None
    # dPivot[''] = None
    # dPivot[''] = None
    return dPivot

def dms2dd(d, m, s):
    """Convertit un angle "degrés minutes secondes" en "degrés décimaux"
    """
    return d + m/60 + s/3600
 
def dd2dms(dd):
    """Convertit un angle "degrés décimaux" en "degrés minutes secondes"
    """
    d = int(dd)
    x = (dd-d)*60
    m = int(x)
    s = (x-m)*60
    return d, m, s
 
def deg2rad(dd):
    """Convertit un angle "degrés décimaux" en "radians"
    """
    return dd/180*pi
 
def rad2deg(rd):
    """Convertit un angle "radians" en "degrés décimaux"
    """
    return rd/pi*180
 
def distanceGPS(latA, longA, latB, longB):
    """Retourne la distance en mètres entre les 2 points A et B connus grâce à
       leurs coordonnées GPS (en radians).
    """
    # Rayon de la terre en mètres (sphère IAG-GRS80) WGS84
    RT = 6378137
    # angle en radians entre les 2 points
    S = acos(sin(latA)*sin(latB) + cos(latA)*cos(latB)*cos(abs(longB-longA)))
    # distance entre les 2 points, comptée sur un arc de grand cercle
    return S * RT
 
def DMd2Dd(dmd) :
    # DDDMM.d --> DDD.d (S or W negative values)
    # 10601.6986 ---> 106+1.6986/60 = 106.02831 degrees
    # "GLL": "4730.189,N,223.183,W"
    # 0.001 represente 110m x 78m (lat 45°)
    # 0.0001 represente 11m x 7/8m
    dotPos = dmd.find(".")
    D = float(dmd[0:dotPos - 2])
    M = float(dmd[dotPos - 2:]) / 60
    return (round(D + M, 6))

def getDtFromNmeaLine(line) :
    global dt1970
    candidatDt = line[3:6]
    if (candidatDt == 'RMC') :
        lTmp = line.split(",")
        # $GPRMC,072648.00,A,4730.18648,N,00223.18287,W,0.049,46.36,010618,,,A*43
        ts = float("20" + lTmp[9][4:6] + lTmp[9][2:4] + lTmp[9][0:2] + lTmp[1][0:2] + lTmp[1][2:4] + lTmp[1][4:])
        dt = datetime.datetime(2000 + int(lTmp[9][4:6]), int(lTmp[9][2:4]), int(lTmp[9][0:2]), int(lTmp[1][0:2]), int(lTmp[1][2:4]), int(lTmp[1][4:6]), int(lTmp[1][7:]))
        ep = (dt - dt1970).total_seconds()
        # print("epoch : [", ep, "]", file=sys.stderr)
        return (ts, dt, ep)
    if (candidatDt == 'ZDA') :
        lTmp = line.split(",")
        # $IIZDA,121644,01,06,2018,,*57
        ts = float(lTmp[4] + lTmp[3] + lTmp[2] + lTmp[1][0:2] + lTmp[1][2:4] + lTmp[1][4:6])
        dt = datetime.datetime(int(lTmp[4]), int(lTmp[3]), int(lTmp[2]), int(lTmp[1][0:2]), int(lTmp[1][2:4]), int(lTmp[1][4:6]))
        ep = (dt - dt1970).total_seconds()
        # print("epoch : [", ep, "]", file=sys.stderr)
        return (ts, dt, ep)

def xtrInfos(candidatDt, line, dP) :
    lTmp = line.split(',')
    """
    !AIVDM, !AIVDO, $AIALR, $AITXT
    $GPAPB, $GPBOD, $GPGBS, $GPGGA, $GPGLL, $GPGSA, $GPGSV, $GPRMB, $GPRMC, $GPRTE, $GPTXT, $GPVTG, $GPWPL
    $IIDBT, $IIDPT, $IIGLL, $IIHDG, $IIHDM, $IIMTA, $IIMTW, $IIMWD, $IIMWV, $IIVHW, $IIVLW, $IIVTG, $IIVWR, $IIVWT, $IIZDA
    $PMGNS, $PSRT
    """
    # if () :
        # dp[candidatDt] =
        # return candidatDt + " = " +
    """   
    # $GPAPB,,,,,,,,,,,,,,*44    APB - Autopilot Sentence "B"
    Field Number:
        Status V = Loran-C Blink or SNR warning V = general warning flag or other navigation systems when a reliable fix is not available
        Status V = Loran-C Cycle Lock warning flag A = OK or not used
        Cross Track Error Magnitude
        Direction to steer, L or R
        Cross Track Units, N = Nautical Miles
        Status A = Arrival Circle Entered
        Status A = Perpendicular passed at waypoint
        Bearing origin to destination -->     
        M = Magnetic, T = True
        Destination Waypoint ID
        Bearing, present position to Destination -->    
        M = Magnetic, T = True 
        Heading to steer to destination waypoint -->    
        M = Magnetic, T = True
        Checksum
    Example: $GPAPB,A,A,0.10,R,N,V,V,011,M,DEST,011,M,011,M*82
    """
    
    # $GPBOD,,T,,M,ATT VILAIN,ATT-PALAIS*59     BOD - Bearing - Waypoint to Waypoint   ! is NOT updated dynamically! 
    
    # $GPGBS,072627.00,4.3,2.8,8.6,,,,*44    GBS - GPS Satellite Fault Detection
    
    # $GPGGA,072844.000,4714.3220,N,00131.5485,W,1,08,1.6,36.2,M,48.5,M,,0000*78    GGA - Global Positioning System Fix Data
    
    # $GPGSA,A,3,05,07,08,13,15,18,20,21,24,28,30,37,1.5,1.0,1.1*38    GSA - GPS DOP and active satellites
    
    # $GPGSV,3,2,12,22,59,065,38,01,53,117,46,17,51,276,,23,45,180,39*7F    GSV - Satellites in view
    
    """
    # $GPRMB,V,,,ATT-PAL,ATT VI,4730.3500,N,00231.7540,W,,,,V,N*62    RMB - Recommended Minimum Navigation Information
        Status, A= Active, V = Void
        Cross Track error - nautical miles
        Direction to Steer, Left or Right
        TO Waypoint ID
        FROM Waypoint ID
        Destination Waypoint Latitude
        N or S
        Destination Waypoint Longitude
        E or W
        Range to destination in nautical miles
        Bearing to destination in degrees True
        Destination closing velocity in knots
        Arrival Status, A = Arrival Circle Entered
        FAA mode indicator (NMEA 2.3 and later)
        Checksum
    Example: $GPRMB,A,0.66,L,003,004,4917.24,N,12309.57,W,001.3,052.5,000.5,V*0B
    """
    
    # $GPRTE,1,1,c,VIL LE PALAIS,ATT-PALAIS,ATT VILAIN*75    RTE - Routes
    
    # $GPWPL,4721.3270,N,00308.6350,W,ATT-PALAIS*3E
    
    # 
    if (candidatDt == 'ECAPB' and lTmp[1] == 'A' and lTmp[2] == 'A') :
        dp['ECAPB'] = line
        return candidatDt + " = " + line 
    if (candidatDt == 'GPAPB' and lTmp[1] == 'A' and lTmp[2] == 'A') :
        dp['GPAPB'] = line
        return candidatDt + " = " + line
    if (candidatDt == 'ECRMB' and lTmp[1] == 'A') :
        dp['ECRMB'] = line
        return candidatDt + " = " + line
    if (candidatDt == 'GPRMB' and lTmp[1] == 'A') :
        dp['GPRMB'] = line
        return candidatDt + " = " + line

    if (candidatDt == 'IIVHW') :
        dP['VHW'] = float(lTmp[5])
        return candidatDt + " = " + lTmp[5] + " dans " + line
    if (candidatDt == 'IIVLW') :
        dP['VLW'] = float(lTmp[3])
        dP['VLWtotal'] = float(lTmp[1])
        return candidatDt + " = " + lTmp[3] + " VLWtotal = " + lTmp[1] + " dans " + line
    if (candidatDt == 'IIDBT') :
        dP['DBT'] = float(lTmp[3])
        return candidatDt + " = " + lTmp[3] + " dans " + line
    if (candidatDt == 'IIMTW') :
        dP['MTW'] = float(lTmp[1])
        return candidatDt + " = " + lTmp[1] + " dans " + line
    if (candidatDt == 'IIVWR') :
        dP['VWRrl'] = lTmp[2]
        if (lTmp[2] == 'L') :
            dP['VWRawa'] = -float(lTmp[1])
        else :
            dP['VWRawa'] = float(lTmp[1])
        dP['VWRaws'] = float(lTmp[3])
        return candidatDt + " VWRawa = " + str(dP['VWRawa']) + " VWRrl = " + lTmp[2] + " VWRaws = " + lTmp[3] + " dans " + line
    if (candidatDt == 'IIMWD') :
        dP['MWDtwd'] = float(lTmp[3])
        dP['MWDtws'] = float(lTmp[5])
        return candidatDt + " MWDtwd = " + lTmp[3] + " MWDtws = " + lTmp[5] + " dans " + line
    if (candidatDt == 'IIVWT') :
        dP['VWTrl'] = lTmp[2]
        if (lTmp[2] == 'L') :
            dP['VWTtwa'] = -float(lTmp[1])
        else :
            dP['VWTtwa'] = float(lTmp[1])
        dP['VWTtws'] = float(lTmp[3])
        return candidatDt + " VWTtwa = " + str(dP['VWTtwa']) + " VWTrl = " + lTmp[2] + " VWTtws = " + lTmp[3] + " dans " + line
    if (candidatDt == 'IIMTA') :
        dP['MTA'] = float(lTmp[1])
        return candidatDt + " = " + lTmp[1] + " dans " + line
    if (candidatDt == 'IIHDM') :
        dP['HDM'] = float(lTmp[1])
        return candidatDt + " = " + lTmp[1] + " dans " + line
    if (candidatDt == 'IIGLL') :
        # $GPGLL,4740.2898,N,00321.2259,W,083718,A,A*50
        if (lTmp[6] == 'A') :
            dP[candidatDt] = str(float(lTmp[1])) + "," + lTmp[2] + "," + str(float(lTmp[3])) + "," + lTmp[4]
            if (lTmp[2] == 'S') :
                dP['GLLlatNum'] = DMd2Dd("-" + lTmp[1]) #float("-" + lTmp[1]) / 100.0
            else :
                dP['GLLlatNum'] = DMd2Dd(lTmp[1]) #float(lTmp[1]) / 100.0
            if (lTmp[4] == 'W') :
                dP['GLLlonNum'] = DMd2Dd("-" + lTmp[3]) #float("-" + lTmp[3]) / 100.0
            else :
                dP['GLLlonNum'] = DMd2Dd(lTmp[3]) #float(lTmp[3]) / 100.0
            return candidatDt + " = " +  dP[candidatDt] + " dans " + line
        else :
            return None
    if (candidatDt == 'IIMWV') :
        # $IIMWV,255,R,03.0,N,A*12
        return candidatDt + " = pas necessaire"
    if (candidatDt == 'IIHDG') :
        # $IIHDG,328.,,,,*70
        return candidatDt + " = pas necessaire car HDM present"
    if (candidatDt == 'IIVTG') :
        # $IIVTG,046.,T,,M,03.5,N,06.5,K,A*2D
        return candidatDt + " = pas necessaire"
    if (candidatDt == 'IIDPT') :
        # $IIDPT,0001.9,,*7A
        return candidatDt + " = pas necessaire"
    if (candidatDt == 'GPRMC' or candidatDt == 'ECRMC' or candidatDt == 'IIRMC') :
        # $GPRMC,091930.00,A,4728.86549,N,00232.55440,W,5.248,201.64,010618,,,D*73
        ##  Info de nav, vont dans le dict() general
        if (lTmp[7] != "") :
            dP['GPRMCsog'] = lTmp[7]
        if (lTmp[8] != "") :
            dP['GPRMCtmg'] = lTmp[8]#round(float(lTmp[8]), 0)
        # dPivot['GPRMCts'] = None #0
        # dPivot['GPRMClatlon'] = None #""
        # dPivot['GPRMClatNum'] = None #0.0
        # dPivot['GPRMClonNum'] = None #0.0

            
            
        return candidatDt + " = SOG et TMG"
    if (candidatDt == 'GPGBS') :
        # $GPGBS,091930.00,1.6,1.5,2.8,,,,*4A
        return candidatDt + " = pas necessaire"
    if (candidatDt == 'IIVTG') :
        # $IIVTG,046.,T,,M,03.5,N,06.5,K,A*2D
        return candidatDt + " = pas necessaire"
    return None

def getEpochFromGPRMC(line) :
    global dt1970
    lTmp = line.split(",")
    # $GPRMC,072648.00,A,4730.18648,N,00223.18287,W,0.049,46.36,010618,,,A*43
    ts = float("20" + lTmp[9][4:6] + lTmp[9][2:4] + lTmp[9][0:2] + lTmp[1][0:2] + lTmp[1][2:4] + lTmp[1][4:]) #  + ".0"
    # certaines phrases n'ont pas de millisecondes (lTmp[1][7:])
    dtDecimales = len(lTmp[1][7:])
    if (dtDecimales == 0) :
        dt = datetime.datetime(2000 + int(lTmp[9][4:6]), int(lTmp[9][2:4]), int(lTmp[9][0:2]), int(lTmp[1][0:2]), int(lTmp[1][2:4]), int(lTmp[1][4:6]))
    else :
        dt = datetime.datetime(2000 + int(lTmp[9][4:6]), int(lTmp[9][2:4]), int(lTmp[9][0:2]), int(lTmp[1][0:2]), int(lTmp[1][2:4]), int(lTmp[1][4:6]), int(lTmp[1][7:]))
    ep = (dt - dt1970).total_seconds() + 0.0
    
    # print("epoch : [", ep, "]", file=sys.stderr)
    return (ep, ts, dtDecimales)

def getEpochFromECRMC(line) :
    return (getEpochFromGPRMC(line))

def getEpochFromIIZDA(line) :
    global dt1970
    lTmp = line.split(",")
    # $IIZDA,121644,01,06,2018,,*57
    ts = float(lTmp[4] + lTmp[3] + lTmp[2] + lTmp[1][0:2] + lTmp[1][2:4] + lTmp[1][4:6] + ".0")
    dt = datetime.datetime(int(lTmp[4]), int(lTmp[3]), int(lTmp[2]), int(lTmp[1][0:2]), int(lTmp[1][2:4]), int(lTmp[1][4:6]))
    ep = (dt - dt1970).total_seconds() + 0.0
    if (len(lTmp[1]) > 6) :
        dtDecimales = len(lTmp[1]) - 6
    else :
        dtDecimales = 0
    #print("ZDA [", line, "] ts", ts, "    ep", ep, file=sys.stderr)
    return (ep, ts, dtDecimales)

def getPosiFromGPRMC(line) :
    lTmp = line.split(",")
    ##  $GPRMC,072648.00,A,4730.18648,N,00223.18287,W,0.049,46.36,010618,,,A*43
    if (lTmp[2] != "A") :
        return None
    else :
        if (lTmp[4] == "S") :
            lTmp[3] = "-" + lTmp[3]
        if (lTmp[6] == "W") :
            lTmp[5] = "-" + lTmp[5]
        return(float(lTmp[3]), float(lTmp[5]))
        
def getPosiFromECRMC(line) :
    return(getPosiFromGPRMC(line))
    
    
def getPosiFromIIGLL(line) :
    lTmp = line.split(",")
    ##  $IIGLL,4729.799,N,00222.958,W,111758,A,A*40
    if (lTmp[6] != "A") :
        return None
    else :
        if (lTmp[2] == "S") :
            lTmp[1] = "-" + lTmp[1]
        if (lTmp[4] == "W") :
            lTmp[3] = "-" + lTmp[3]
        return(float(lTmp[1]), float(lTmp[3]))    
    
# dPivot = getDictEpoch()
nbrGll = nbrRmc = nbrRmcUsed = nbrGllAndRmc = 0
## dTimeRefs[<tag de temps>] = [1ere ligne, derniere ligne, nbr de lignes, debut, fin, nbr de secondes, delai moyen, nbr decimales temps]
dTimeRefs = dict()
dTimeRefs['GPRMC'] = [None, None, 0, None, None, 0, 0.0, 0]
dTimeRefs['ECRMC'] = [None, None, 0, None, None, 0, 0.0, 0]
dTimeRefs['IIRMC'] = [None, None, 0, None, None, 0, 0.0, 0]
dTimeRefs['IIZDA'] = [None, None, 0, None, None, 0, 0.0, 0]
ep    = ts    = dtDeci    = 0  
epTmp = tsTmp = dtDeciTmp = 0

## dPosiRefs[<tag de position>] = 1ere ligne, derniere ligne, nbr de lignes, --, --, LatMin, LonMin, LatMax, LonMax, nbr decimales position
dPosiRefs = dict()
dPosiRefs['GPRMC'] = [None, None, 0, None, None, 0.0, 0.0, 0.0, 0.0, 0]
dPosiRefs['ECRMC'] = [None, None, 0, None, None, 0.0, 0.0, 0.0, 0.0, 0]
dPosiRefs['IIGLL'] = [None, None, 0, None, None, 0.0, 0.0, 0.0, 0.0, 0]
dPosiRefs['GPRMC'] = [None, None, 0, None, None, None, None]
dPosiRefs['ECRMC'] = [None, None, 0, None, None, None, None]
dPosiRefs['IIGLL'] = [None, None, 0, None, None, None, None]

## dict de tout les tags presents
dTags = dict()


with open(nmeaFilename, 'r') as fNmea :
    nLine = nLineNmea = nLineDtRef = nLineXyRef = 0
    nLineDtFirst = nLineDtLast = nLineXyFirst = nLineXyLast = None
    for line in fNmea.readlines() :
        candidatDt = candidatXy = ""
        nLine += 1
        line = line.rstrip()
        if (line == "") :
            continue
        if (line[0:3] == "!AI") :
            # !AIVDO,1,1,,,B3HvFrP0;?u7vh6jtRVhkwi5wP06,0*03
            continue
        if (line[0:1] == "$") :
            ##  La ligne est-elle du NMEA ?
            if (line[-3:-2] == "*") :
                nLineNmea += 1 
            else :
                continue
            candidatDt = candidatXy = line[1:6]
            ##  Construire la liste des tags NMEA contenus dans le fichier.
            if (candidatDt not in dTags) :
                dTags[candidatDt] = None
                
            ##  Premier ou dernier des differents tags de position possible ?    
            if (candidatXy in dPosiRefs) :
                if (dPosiRefs[candidatXy][0] is None) :
                    dPosiRefs[candidatXy][0] = nLine
                else :
                    dPosiRefs[candidatXy][1] = nLine
                dPosiRefs[candidatXy][2] += 1
                
                # if (candidatXy != srcPosition) :
                if (candidatXy == "GPRMC") :
                    (lat, lon) = getPosiFromGPRMC(line)
                elif (candidatXy == "ECRMC") :
                    (lat, lon) = getPosiFromECRMC(line)
                elif (candidatXy == "IIGLL") :
                    (lat, lon) = getPosiFromIIGLL(line)
                # print("candidatXy =", candidatXy, ", lat =", lat, ", lon =", lon)
                
                if (dPosiRefs[candidatXy][3] is None) :
                    dPosiRefs[candidatXy][3] = lat
                else :
                    dPosiRefs[candidatXy][3] = min(dPosiRefs[candidatXy][3], lat)
                if (dPosiRefs[candidatXy][4] is None) :
                    dPosiRefs[candidatXy][4] = lon
                else :
                    dPosiRefs[candidatXy][4] = min(dPosiRefs[candidatXy][4], lon)
                if (dPosiRefs[candidatXy][5] is None) :
                    dPosiRefs[candidatXy][5] = lat
                else :
                    dPosiRefs[candidatXy][5] = max(dPosiRefs[candidatXy][5], lat)
                if (dPosiRefs[candidatXy][6] is None) :
                    dPosiRefs[candidatXy][6] = lon
                else :
                    dPosiRefs[candidatXy][6] = max(dPosiRefs[candidatXy][6], lon)
                
                ##  ? Reference de position ?
                if (candidatXy == srcPosition) :
                    ##  Premiere ou derniere reference de temps ?
                    if (nLineXyFirst is None) : 
                        nLineXyFirst = nLine
                    else :
                        nLineXyLast = nLine
                    nLineXyRef += 1
                    
            # print("candidatDt ? [" + candidatDt + "]" + TAB + "[" + srcEpoch + "]")
            # print("ep", ep, "       line", line)
            ##  Premier ou dernier des differents tags de temps possible ?
            if (candidatDt in dTimeRefs) :
                #print("candidatDt", candidatDt, " ligne", nLine, TAB, line)
                pass
                if (dTimeRefs[candidatDt][0] is None) :
                    dTimeRefs[candidatDt][0] = nLine
                else :
                    dTimeRefs[candidatDt][1] = nLine
                dTimeRefs[candidatDt][2] += 1

                # if (candidatDt != srcEpoch) :
                if   (candidatDt == "GPRMC") :
                    (epTmp, tsTmp, dtDeciTmp) = getEpochFromGPRMC(line)
                elif (candidatDt == "ECRMC") :
                    (epTmp, tsTmp, dtDeciTmp) = getEpochFromECRMC(line)
                elif (candidatDt == "IIZDA") :
                    (epTmp, tsTmp, dtDeciTmp) = getEpochFromIIZDA(line)
                if (dTimeRefs[candidatDt][3] is None) :
                    (dTimeRefs[candidatDt][3]) = epTmp
                else : 
                    (dTimeRefs[candidatDt][4]) = epTmp   
                
                ##  ? Reference de temps ?
                if (candidatDt == srcEpoch) :
                
                    # print("candidatDt == srcEpoch")
                    ##  Premiere ou derniere reference de temps ?
                    if (nLineDtFirst is None) : 
                        nLineDtFirst = nLine
                    else :
                        nLineDtLast = nLine
                    nLineDtRef += 1
                    if   (candidatDt == "GPRMC") :
                        (ep, ts, dtDeci) = getEpochFromGPRMC(line)
                    elif (candidatDt == "ECRMC") :
                        (ep, ts, dtDeci) = getEpochFromECRMC(line)
                    elif (candidatDt == "IIZDA") :
                        (ep, ts, dtDeci) = getEpochFromIIZDA(line)
                    else :
                        print("E;Reference de temps a partir de NMEA [" + srcEpoch + "] non geree", file=sys.stderr)
                        quit()
                    # print("ep", ep, TAB, "ts", ts)
                    if (not ep in dPivotsSorted and ep > 0) :
                        pass
                    elif (not round(ep + 0.1, 1) in dPivotsSorted) :
                        ep = round(ep + 0.1, 1)
                        ts = round(ts + 0.1, 1)
                    elif (not round(ep + 0.2, 1) in dPivotsSorted) :
                        ep = round(ep + 0.2, 1)
                        ts = round(ts + 0.2, 1)
                    elif (not round(ep + 0.3, 1) in dPivotsSorted) :
                        ep = round(ep + 0.3, 1)
                        ts = round(ts + 0.3, 1)
                    elif (not round(ep + 0.4, 1) in dPivotsSorted) :
                        ep = round(ep + 0.4, 1)
                        ts = round(ts + 0.4, 1)
                    elif (not round(ep + 0.5, 1) in dPivotsSorted) :
                        ep = round(ep + 0.5, 1)
                        ts = round(ts + 0.5, 1)
                    else :
                        # On n'a jamais vu ce truc...
                        pass
                    ##  Fourniture d'un dictionnaire dont les clefs sont prérenseignées, et les valeurs a None
                    # dPivotsSorted[ep] = getDictEpoch()
                    # dPivotsSorted[ep]['ts'] = ts

                    # if (dTimeRefs[candidatDt][3] is None) :
                        # dTimeRefs[candidatDt][3] = ep
                    # else : 
                        # dTimeRefs[candidatDt][4] = ep

                # if (ep != 0) :
                    # retCode = xtrInfos(candidatDt, line, dPivotsSorted[ep])
                    # if (retCode is None) :
                        # pass
                    # else :
                        # pass
       





print("Pour [" + str(nLine) + "] lignes, [" + str(nLineNmea) + "] tags NMEA valides .", )
"""
Pour [369349] lignes, [342778] tags NMEA valides .
"""
print("La reference de temps (" + srcEpoch + ") compte [" + str(nLineDtRef) + "] lignes, de la ligne [" + str(nLineDtFirst) + "] a la ligne [" + str(nLineDtLast) + "]")
if (nLineDtRef > 0 and nLineDtFirst is not None) :
    print(", soit une reference de temps toutes les " + str(round((nLineDtLast - nLineDtFirst) / nLineDtRef, 2)) + " lignes")
    ## dTimeRefs[<tag de temps>] = [1ere ligne, derniere ligne, nbr de lignes, debut, fin, nbr de secondes, delai moyen]
    for k in (dTimeRefs) :
        if (dTimeRefs[k][3] is not None and dTimeRefs[k][4] is not None) :
            dTimeRefs[k][5] = round(dTimeRefs[k][4] - dTimeRefs[k][3], 1)
            dTimeRefs[k][6] = round(dTimeRefs[k][5] / dTimeRefs[k][2], 1)
        print(k, TAB, dTimeRefs[k])
"""
La reference de temps (IIZDA) compte [22259] lignes, de la ligne [17] a la ligne [369348]
, soit une reference de temps toutes les 16.59 lignes
GPRMC 	 [2173, 369285, 6115, 1527837978.0, 1527862281.0, 24303.0, 4.0, 0]
ECRMC 	 [None, None, 0, None, None, 0, 0.0, 0]
IIRMC 	 [None, None, 0, None, None, 0, 0.0, 0]
IIZDA 	 [17, 369348, 22259, 1527837806.0, 1527862284.0, 24478.0, 1.1, 0]
"""
print("La reference de position (" + srcPosition + ") compte [" + str(nLineXyRef) + "] lignes, de la ligne [" + str(nLineXyFirst) + "] a la ligne [" + str(nLineXyLast) + "]")
if (nLineXyRef > 0 and nLineXyFirst is not None) :
    print(", soit une reference de position toutes les " + str(round((nLineXyLast - nLineXyFirst) / nLineXyRef, 2)) + " lignes")
    ## dPosiRefs[<tag de position>] = 1ere ligne, derniere ligne, nbr de lignes, LatMin, LonMin, LatMax, LonMax, nbr decimales position
    for k in (dPosiRefs) :
        print(k, TAB, dPosiRefs[k])
"""
La reference de position (GPRMC) compte [6115] lignes, de la ligne [2173] a la ligne [369285]
, soit une reference de position toutes les 60.03 lignes
GPRMC 	 [2173, 369285, 6115, 4723.92931, -238.21505, 4730.52287, -223.11555]
ECRMC 	 [None, None, 0, None, None, None, None]
IIGLL 	 [16, 369347, 22259, 4723.928, -238.215, 4730.523, -223.117]
"""


print(sorted(dTags))
"""
['AIALR', 'AITXT', 'GPGBS', 'GPRMC', 'GPTXT', 'IIDBT', 'IIDPT', 'IIGLL', 'IIHDG', 'IIHDM', 'IIMTA', 'IIMTW', 'IIMWD', 'IIMWV', 'IIVHW', 'IIVLW', 'IIVTG', 'IIVWR', 'IIVWT', 'IIZDA', 'PSRT,']
"""



# for k in dLines :
    # print(dLines[k])
