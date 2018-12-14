#!/python
# -*- coding: utf-8 -*-

### http://sametmax.com/lencoding-en-python-une-bonne-fois-pour-toute/
from __future__ import unicode_literals
### https://www.systutorials.com/241727/how-to-print-a-line-to-stderr-and-stdout-in-python/
# Permet en python 2.7 print("your message", file=sys.stderr) comme en Python 3
from __future__ import print_function

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
epoch = datetime.datetime(1970, 1, 1)


#bShowIdentifier = os.getenv("dsXidentifier", False)

## fichier a traiter
me = sys.argv[0]
#args = sys.argv[1:]
if (len(sys.argv) != 3) :
    print(me + " : Pas le bon nombre de parametres.", file=sys.stderr)
    print("Usage : " + me + " <Chemin et nom du fichier NMEA> <Chemin et nom de la base Sqlite>", file=sys.stderr)
    quit()
else :
    nmeaFilename = sys.argv[1]
    nmeaDbname = sys.argv[2]
    print("I;Import du fichier NMEA [" + nmeaFilename + "] dans la base Sqlite [" + nmeaDbname + "]", file=sys.stderr)

## Tests prealables, fichier NMEA puis DB
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
nmeaTsFilename = nmeaFilenameName + "_TS" + nmeaFilenameExtension
# print("nmeaTsFilename", nmeaTsFilename)
# shutil.copyfile(nmeaFilename, nmeaTsFilename)

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
"""

lCandidats = list()
ddCandidats = dict()
ddCandidats['RMC'] = dict()
ddCandidats['RMC']['nbrL'] = 0
ddCandidats['RMC']['lPremiere'] = 0
ddCandidats['RMC']['lDerniere'] = 0
ddCandidats['RMC']['sPremiere'] = ""
ddCandidats['RMC']['sDerniere'] = ""
ddCandidats['RMC']['dtPremiere'] = ""
ddCandidats['RMC']['dtDerniere'] = ""
ddCandidats['RMC']['duree'] = 0
ddCandidats['RMC']['intervalle'] = 0.0
ddCandidats['RMC']['couvertureDebut'] = 0.0
ddCandidats['RMC']['couvertureFin'] = 0.0
ddCandidats['RMC']['couvertureTotale'] = 0.0
ddCandidats['ZDA'] = dict()
ddCandidats['ZDA']['nbrL'] = 0
ddCandidats['ZDA']['lPremiere'] = 0
ddCandidats['ZDA']['lDerniere'] = 0
ddCandidats['ZDA']['sPremiere'] = ""
ddCandidats['ZDA']['sDerniere'] = ""
ddCandidats['ZDA']['dtPremiere'] = ""
ddCandidats['ZDA']['dtDerniere'] = ""
ddCandidats['ZDA']['duree'] = 0
ddCandidats['ZDA']['intervalle'] = 0.0
ddCandidats['ZDA']['couvertureDebut'] = 0.0
ddCandidats['ZDA']['couvertureFin'] = 0.0
ddCandidats['ZDA']['couvertureTotale'] = 0.0

for candidat, dCandidats in ddCandidats.items() :
    lCandidats.append(candidat)

def getDtFromNmeaLine(line) :
    candidat = line[3:6]
    if (candidat == 'RMC') :
        lTmp = line.split(",")
        return datetime.datetime(2000 + int(lTmp[9][4:6]), int(lTmp[9][2:4]), int(lTmp[9][0:2]), int(lTmp[1][0:2]), int(lTmp[1][2:4]), int(lTmp[1][4:6]))
    if (candidat == 'ZDA') :
        lTmp = line.split(",")
        return datetime.datetime(int(lTmp[4]), int(lTmp[3]), int(lTmp[2]), int(lTmp[1][0:2]), int(lTmp[1][2:4]), int(lTmp[1][4:6]))
        
        
dernierCandidat = ""
dernierDT = None
dernierNumL = 0
deltaRmcZda = None
deltaRmcZdaNbr = 0
deltaRmcZda00 = 0
deltaRmcZda01 = 0
deltaRmcZda02 = 0
deltaRmcZdaSeuil = 3
deltaRmcZdaSeuilFranchi = None
deltaRmcZdaSeuilFranchiProportion = None
with open(nmeaFilename, 'r') as fNmea :
    nLineRaw = nLine = 0
    for line in fNmea.readlines() :
        nLineRaw += 1
        line = line.rstrip()
        if (line == "") :
            continue
        if (line[0:3] == "!AI") :
            continue
        nLine += 1
        if (line[0:1] == "$") :
            candidat = line[3:6]
            # print(candidat)
            if (candidat in lCandidats) :
                ddCandidats[candidat]['nbrL'] += 1
                ddCandidats[candidat]['lDerniere'] = nLine
                ddCandidats[candidat]['sDerniere'] = line
                if (ddCandidats[candidat]['lPremiere']) == 0 :
                    ddCandidats[candidat]['lPremiere'] = nLine
                    ddCandidats[candidat]['sPremiere'] = line
                    ddCandidats[candidat]['lDerniere'] = nLine
                    ddCandidats[candidat]['sDerniere'] = line
                if (candidat == 'RMC') :
                    dernierCandidat = candidat
                    dernierDT = getDtFromNmeaLine(line)
                    dernierNumL = nLine
                if (candidat == 'ZDA' and dernierCandidat == 'RMC' and (nLine - dernierNumL) < 50) : 
                    deltaRmcZdaNbr += 1
                    deltaRmcZda = (getDtFromNmeaLine(line) - dernierDT).total_seconds()
                    if (abs(deltaRmcZda) > deltaRmcZdaSeuil) :
                        if (deltaRmcZdaSeuilFranchi is None) :
                            deltaRmcZdaSeuilFranchi = 0
                        deltaRmcZdaSeuilFranchi += 1
                        print("Ligne : ", nLineRaw, ", deltaRmcZda :", deltaRmcZda)
                    elif (deltaRmcZda == 0) :
                        deltaRmcZda00 += 1
                    elif (abs(deltaRmcZda) == 1) :
                        deltaRmcZda01 += 1
                    elif (abs(deltaRmcZda) == 2) :
                        deltaRmcZda02 += 1
                        
                    dernierCandidat = candidat
deltaRmcZdaSeuilFranchiProportion = round(deltaRmcZdaSeuilFranchi * 100 / deltaRmcZdaNbr, 2)
deltaRmcZda00Proportion = round(deltaRmcZda00 * 100 / deltaRmcZdaNbr, 2)
deltaRmcZda01Proportion = round(deltaRmcZda01 * 100 / deltaRmcZdaNbr, 2)
deltaRmcZda02Proportion = round(deltaRmcZda02 * 100 / deltaRmcZdaNbr, 2)

print("La recherche des deltas entre RMC puis ZDA a un seuil de : ", deltaRmcZdaSeuil, " secondes")
print(deltaRmcZdaNbr, " deltas en tout, dont ", deltaRmcZdaSeuilFranchi, " seuil franchi soit ", deltaRmcZdaSeuilFranchiProportion, "%")
print(deltaRmcZdaNbr, " deltas en tout, dont ", deltaRmcZda00, " a 0, soit ", deltaRmcZda00Proportion, "%")
print("    et ", deltaRmcZda01, " a +/- 1 sec, soit ", deltaRmcZda01Proportion, "%, ", deltaRmcZda02, " a +/- 2 sec, soit ", deltaRmcZda02Proportion, "%")

                    
## Duree, intervalle
## Couvertures de chacun des candidats
lTmp = list()
# Pour RMC
if (ddCandidats['RMC']['nbrL'] > 0) :
    lTmp = ddCandidats['RMC']['sPremiere'].split(",")
    # ddCandidats['RMC']['dtPremiere'] = "20" + str(lTmp[9][4:6]) + str(lTmp[9][2:4]) + str(lTmp[9][0:2]) + " " + str(lTmp[1][0:6])
    ddCandidats['RMC']['dtPremiere'] = datetime.datetime(2000 + int(lTmp[9][4:6]), int(lTmp[9][2:4]), int(lTmp[9][0:2]), int(lTmp[1][0:2]), int(lTmp[1][2:4]), int(lTmp[1][4:6]))
    # sRmcPremiereDT = datetime.strptime(str(lTmp[9]) + str(lTmp[1]), '%d%m%y%H%M%S')
    lTmp = ddCandidats['RMC']['sDerniere'].split(",")
    # ddCandidats['RMC']['dtDerniere'] =  "20" + str(lTmp[9][4:6]) + str(lTmp[9][2:4]) + str(lTmp[9][0:2]) + " " + str(lTmp[1][0:6])
    ddCandidats['RMC']['dtDerniere'] = datetime.datetime(2000 + int(lTmp[9][4:6]), int(lTmp[9][2:4]), int(lTmp[9][0:2]), int(lTmp[1][0:2]), int(lTmp[1][2:4]), int(lTmp[1][4:6]))
    # sRmcDerniereDT =  datetime.strptime(str(lTmp[9]) + str(lTmp[1]), '%d%m%y%H%M%S')
    # print(time.strptime(ddCandidats['RMC']['dtDerniere'], "%Y%m%d %H%M%S"))
    ddCandidats['RMC']['duree'] = (ddCandidats['RMC']['dtDerniere'] - ddCandidats['RMC']['dtPremiere']).total_seconds()
    ddCandidats['RMC']['intervalle'] = round(ddCandidats['RMC']['duree']  / ddCandidats['RMC']['nbrL'], 3)
    ddCandidats['RMC']['couvertureDebut'] = round(ddCandidats['RMC']['lPremiere'] * 100 / nLine, 2)
    ddCandidats['RMC']['couvertureFin'] = round(ddCandidats['RMC']['lDerniere'] * 100 / nLine, 2)
    ddCandidats['RMC']['couvertureTotale'] = ddCandidats['RMC']['couvertureFin'] - ddCandidats['RMC']['couvertureDebut']
    print(ddCandidats['RMC']['dtDerniere'], file=sys.stderr) ## 2018-06-01 14:11:21
# Pour ZDA
if (ddCandidats['ZDA']['nbrL'] > 0) :
    lTmp = ddCandidats['ZDA']['sPremiere'].split(",")
    # ddCandidats['ZDA']['dtPremiere'] = str(lTmp[4]) + str(lTmp[3]) + str(lTmp[2]) + " " + str(lTmp[1][0:6])
    ddCandidats['ZDA']['dtPremiere'] = datetime.datetime(int(lTmp[4]), int(lTmp[3]), int(lTmp[2]), int(lTmp[1][0:2]), int(lTmp[1][2:4]), int(lTmp[1][4:6]))
    # sZdaPremiereDT = datetime.strptime(str(lTmp[2]) + str(lTmp[3]) + str(lTmp[4]) + str(lTmp[1]), '%d%m%y%H%M%S')
    lTmp = ddCandidats['ZDA']['sDerniere'].split(",")
    # ddCandidats['ZDA']['dtDerniere'] = str(lTmp[4]) + str(lTmp[3]) + str(lTmp[2]) + " " + str(lTmp[1][0:6])
    ddCandidats['ZDA']['dtDerniere'] = datetime.datetime(int(lTmp[4]), int(lTmp[3]), int(lTmp[2]), int(lTmp[1][0:2]), int(lTmp[1][2:4]), int(lTmp[1][4:6]))
    # sZdaDerniereDT = datetime.strptime(str(lTmp[2]) + str(lTmp[3]) + str(lTmp[4]) + str(lTmp[1]), '%d%m%y%H%M%S')
    ddCandidats['ZDA']['duree'] = (ddCandidats['ZDA']['dtDerniere'] - ddCandidats['ZDA']['dtPremiere']).total_seconds()
    ddCandidats['ZDA']['intervalle'] = round(ddCandidats['ZDA']['duree']  / ddCandidats['ZDA']['nbrL'], 3)
    ddCandidats['ZDA']['couvertureDebut'] = round(ddCandidats['ZDA']['lPremiere'] * 100 / nLine, 2)
    ddCandidats['ZDA']['couvertureFin'] = round(ddCandidats['ZDA']['lDerniere'] * 100 / nLine, 2)
    ddCandidats['ZDA']['couvertureTotale'] = ddCandidats['ZDA']['couvertureFin'] - ddCandidats['ZDA']['couvertureDebut']

    
    
    
print(nmeaFilename + " : Nbr Lignes NMEA [" + str(nLine) + "]")
# print(ddCandidats)
for candidat, dCandidats in ddCandidats.items() :
    print("Pour le candidat [" + candidat + "]")
    for key, val in dCandidats.items() :
        print(candidat + "\t" + key + "\t" + str(val))
    # print(candidat, dCandidats)

exit()

##  Verif prealable de la DB

if (not os.path.exists(nmeaDbname)) :
    print("E:Base", nmeaDbname, "introuvable", file=sys.stderr)
    quit()
try :
    db = sqlite3.connect(nmeaDbname)
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) AS ""NbrL"" FROM nmeaFiles")
    nbrL = cursor.fetchone()
    #print("nbrL = ", nbrL)
    cursor.execute("SELECT COUNT(*) AS ""NbrL"" FROM nmeaPropSentences")
    nbrL = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS ""NbrL"" FROM nmeaSentences")
    nbrL = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS ""NbrL"" FROM nmeaTalkers")
    nbrL = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS ""NbrL"" FROM nmeaTraces")
    nbrL = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS ""NbrL"" FROM nmeaValues")
    nbrL = cursor.fetchone()
except Exception as e :
    print("E:Pb avec la DB [" + nmeaDbname + "]", file=sys.stderr)
    db.close()
    quit()


def getXydtFromInstruments(id, val) :
    retX = retY = retXY = retDT = None
    if (id == '$IIZDA') :
        ##  $IIZDA,051702,08,06,2018,,*5B
        zda = val.split(',')
        retDT = str(zda[3]) + str(zda[2]) + str(zda[1]) + str(zda[0])
        #print (val, ' --> ', retDT)
    if (id == '$IIGLL') :
        ##  $IIGLL,4743.597,N,00321.014,W,051702,A,A*49
        gll = val.split(',') # ok si gll[5 ou 6] == 'A' ou 'A*nn'
        retXY = gll[0] + ' ' + gll[1] + '\t' + gll[2] + ' ' + gll[3]
        #print(val, ' --> ', retXY)
        ##  N --> ?    S --> ?    W --> ?    E --> ?
        retX = gll[0]
        if (gll[1] == 'S') :
            retX = '-' + gll[0]
        retY = gll[2]
        if (gll[3] == 'W') :
            retY = '-' + gll[2]
        #print(val, ' --> ', retX, '/', retY)
    return(retX, retY, retXY, retDT)

def getXydtFromGps(id, val) :
    retX = retY = retXY = retDT = None

    return(retX, retY, retXY, retDT)

def getXydt(id, val) :
    retX = retY = retXY = retDT = None

    return(retX, retY, retXY, retDT)



## Verification de la presence de ces donnees ...
#sql = "SELECT DISTINCT fileName, fileTsWrite FROM nmeaFiles WHERE fileName LIKE '%" + "ZZZ" + basename + "%' OR fileCheck LIKE '" + fileCheck + "ZZZ" + "' OR fileTsWrite = " + mTimeIso + "999" + ";"
sql = "SELECT DISTINCT FileName, FileTsWrite FROM nmeaFiles WHERE FileName LIKE '%" + basename + "%' OR FileCheck LIKE '" + fileCheck + "' OR FileTsWrite = " + mTimeIso + ";"
cursor.execute(sql)
res = cursor.fetchone()
#print("res =", res)
if (res != None) :
    (candidatName, candidatTsWrite) = res
    print("W:Un fichier " + candidatName + " du " + str(candidatTsWrite) + ", fort similaire, existe dans la base.")
    db.close()
    quit()

## INSERT du flux NMEA
try :
    ## feed nmeaFiles
    sql = "INSERT INTO nmeaFiles(FileName, FileCheck, FileTsWrite, FileTsImport) VALUES ('" + basename + "', '" + fileCheck + "', " + mTimeIso + ", " + iso8601 + ");"
    cursor.execute(sql)
    sql = "SELECT LAST_INSERT_ROWID();" # print(cursor.lastrowid)
    cursor.execute(sql)
    fileId = cursor.fetchone()[0] # (3,)  donc [0] pour isoler le premier element
    #print(fileId)

    """
        Type de trames pour marquage temporel et spatial
    Les trames dépendent des équipements.
    On part du postulat qu'un GPS est plus probablement présent que d'autres équipements
    Les trames de type $GP seront donc utilisées en priorité par rapport aux trames $II
    $GPRMC dt + xy (ou $EC)
    $GPRMC,083717.00,A,4740.29142,N,00321.22402,W,4.418,234.15,070618,,,D*7E
    $ECRMC,051703,A,4743.597,N,00321.014,W,0.000,351.000,080618,1.064,W*6E
    $GPGLL xy (ou $II)
    $GPGLL,4740.2898,N,00321.2259,W,083718,A,A*50
    $IIGLL,4743.597,N,00321.014,W,051702,A,A*49
    $IIZDA dt
    $IIZDA,051702,08,06,2018,,*5B
    $GPGGA xy (time sans date)
    $GPGGA,083718,4740.2898,N,00321.2259,W,1,12,0.8,1.7,M,49.5,M,,*50
    Les n premieres lignes du fichier seront parcourues,
    afin de déterminer quel type de trammes sera pris en compte.
    """
    ##  Marquage spatial et temporel
    xydt = False
    ##  Nombre de ligne pour echantillon
    NbrSampleLines = 1000
    ##  Nombre de trame par type
    nbIIGLL = nbIIZDA = nbRMC = nbGLL = nbGGA = nbZDA = 0
    ##  Type de trame
    ttIIGLL = nbIIZDA = ttRMC = ttGLL = ttGGA = ttZDA = False
    ##  Listes de types choisis
    dtTrameTypesList = list()
    xyTrameTypesList = list()
    xydtTrameTypesList = list()
    ##  Talker de trames a prendre en compte
    ##  'G' pour GPRMC
    ##  'I' pour IIGLL + IIZDA
    ##  (reste aussi IIRMC...)
    favori = 'G'
    with open(nmeaFilename, 'r') as fNmea :
        nLine = 0
        for line in fNmea.readlines() :
            line = line.rstrip()
            if (line == "") :
                continue
            if (line[0:3] == "!AI") :
                continue
            nLine += 1
            if (nLine > NbrSampleLines) :
                break
            if (line[0:1] != "$") :
                traceInfo = traceInfo + line
                id = ""
                val = line
            else :
                commaPos = line.find(",")
                idFull = line[0:commaPos].upper()
                talker = idFull[1:4]
                id = idFull[3:]
                ##  Ne pas tenir compte des trames proprietaire
                if (talker[0] == 'P') :
                    continue
                #print(id, "|", line)
                if (id == 'RMC') : ##  dt + xy
                    ttRMC = True
                    nbRMC = nbRMC + 1
                elif (id == 'GLL') : ##  xy
                    ttGLL = True
                    nbGLL = nbGLL + 1
                    if (idFull == '$IIGLL') : ##  xy
                        ttIIGLL = True
                        nbIIGLL = nbIIGLL + 1
                elif (id == 'GGA') : ##  xy
                    ttGGA = True
                    nbGGA = nbGGA + 1
                elif (id == 'ZDA') : ##  dt
                    ttZDA = True
                    nbZDA = nbZDA + 1
                    if (idFull == '$IIZDA') : ##  xy
                        ttIIZDA = True
                        nbIIZDA = nbIIZDA + 1
    #print("nbRMC =", nbRMC, ", nbGLL =", nbGLL, ", nbIIGLL =", nbIIGLL, ", nbGGA =", nbGGA, ", nbZDA =", nbZDA, ", nbIIGLL =", nbIIGLL)
    ##  Test si marquage temporel possible
    ##  (priorite aux infos NKE)
    xydt = False
    if (ttIIGLL and ttIIZDA) :
        ##  Test de la quantite de IIGLL et de IIZDA (2% de l'echantillon)
        if (nbIIGLL > (NbrSampleLines / 50) and nbIIZDA > (NbrSampleLines / 50)) :
            dtTrameTypesList = ('$IIZDA')
            xyTrameTypesList = ('$IIGLL')
            print("I;Utilisation des trames IIGLL et IIZDA pour marquage spatial et temporel", file=sys.stderr)
            if (favori == 'G') :
                favori = 'I'
                print("W; ! Les trames preferees deviennent les trames $II !", file=sys.stderr)
            xydt = True
        else :
            if (ttRMC or ttZDA) :
                ##  Test de la quantite de RMC (2% de l'echantillon)
                if (nbRMC > (NbrSampleLines / 50)) :
                    dtTrameTypesList = ('$IIRMC', '$ECRMC', '$GPRMC')
                    print("I;Utilisation exclusive de trames RMC pour marquage temporel", file=sys.stderr)
                    if (favori == 'I') :
                        favori = 'G'
                        print("W; ! Les trames preferees deviennent les trames $GPRMC !", file=sys.stderr)
                else :
                    dtTrameTypesList = ('$IIRMC', '$ECRMC', '$GPRMC', '$IIZDA', '$ECZDA')
                    print("I;Utilisation de trames RMC et ZDA pour marquage temporel", file=sys.stderr)
                    favori = ''
                    print("W; ! Plus de trames preferee !", file=sys.stderr)
                xydt = True
            else :
                print("W; ! Pas de marquage temporel possible !", file=sys.stderr)
            ##  Test si marquage spatial possible
            if (ttRMC or ttGLL or ttGGA) :
                ##  Test de la quantite de RMC (2% de l'echantillon)
                if (nbRMC > (NbrSampleLines / 50)) :
                    xyTrameTypesList = ('$IIRMC', '$ECRMC', '$GPRMC')
                    print("I;Utilisation exclusive de trames RMC pour marquage spatial", file=sys.stderr)
                    if (favori == 'I') :
                        favori = 'G'
                        print("W; ! Les trames preferees deviennent les trames $GPRMC !", file=sys.stderr)
                else :
                    xyTrameTypesList = ('$IIRMC', '$ECRMC', '$GPRMC', '$ECGLL', '$GPGLL', '$ECGGA', '$GPGGA', '$IIGLL', '$IIGGA')
                    print("I;Utilisation trames RMC, GLL et GGA pour marquage spatial", file=sys.stderr)
                    favori = ''
                    print("W; ! Plus de trames preferee !", file=sys.stderr)
                xydt = True
            else :
                print("W; ! Pas de marquage spatial possible !", file=sys.stderr)

    xydtTrameTypesList = xyTrameTypesList + dtTrameTypesList

    #quit()





    ## feed nmeaValues
    lat = lon = latlon = ts = dt = "NULL"
    sql = "INSERT INTO nmeaValues(FileID, FileLineNum, lat, lon, latlon, ts, dt, NmeaID, NmeaVal) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"
    traceInfo = ""
    with open(nmeaFilename, 'r') as fNmea :
        nLine = 0
        for line in fNmea.readlines() :
            line = line.rstrip()
            if (line == "") :
                continue
            if (line[0:3] == "!AI") :
                continue
            nLine += 1
            if (line[0:1] != "$") :
                traceInfo = traceInfo + line
                id = ""
                val = line
            else :
                commaPos = line.find(",")
                id = line[0:commaPos]
                val = line[commaPos + 1:]
                ## Test si trame avec information temporelle ou positionnelle
                if (xydt) :
                    if (favori == 'I' and id[0:3] == '$II') :
                        (retX, retY, retXY, retDT) = getXydtFromInstruments(id, val)
                    elif (favori == 'G' and id[0:3] == '$GP') :
                        (retX, retY, retXY, retDT) = getXydtFromGps(id, val)
                    elif (id in xydtTrameTypesList) :
                        (retX, retY, retXY, retDT) = getXydt(id, val)
                    if (retX != None) :
                        lat = retX
                    if (retY != None) :
                        lon = retY
                    if (retXY != None) :
                        latlon = retXY
                    if (retDT != None) :
                        dt = retDT
                        #19991231235959 --> 1999-12-31 23:59:59
                        ts = dt[0:4] + '-' + dt[4:6] + '-' + dt[6:8] + ' ' + dt[8:10] + ':' + dt[10:12] + ':' + dt[12:14]
                # if (id in dtTrameTypesList) :
                    # pass
                # if (xyTrameType == "") :
                    # pass
            cursor.execute(sql, (fileId, nLine, lat, lon, latlon, ts, dt, id, val))
    ## feed nmeaTraces
    sql = "INSERT INTO nmeaTraces(FileID, TraceName, LineStart, LineStop, TraceInfo) VALUES(?, ?, ?, ?, ?);"
    cursor.execute(sql, (fileId, basename, 1, nLine, traceInfo))
    db.commit()
    print("Import de " + str(nLine) + " lignes (FileID:" + str(fileId) + ")")
except Exception as e :
    db.rollback()
    print("E:Pb avec import de [" + nmeaFilename + "]", file=sys.stderr)
    print(e, file=sys.stderr)





# dTalkers = dict()
# with open(nmeaFilename, 'r') as fNmea :
    # nLine = 0
    # for line in fNmea.readlines() :
        # nLine += 1
        # if (line[0:1] == "$") :
            # idTalker = line[1:3]
            # try :
                # dTalkers[idTalker] = dTalkers[idTalker] + 1
            # except :
                # dTalkers[idTalker] = 1
            # lTalkers.append(idTalker)
# print(dTalkers)
# if (len(dTalkers) > 0) :
    # print("idTalker" + TAB + "Nombre")
    # for (k, v) in dTalkers.items()  :
        # print(k, TAB, v)
# else :
    # print("Pas de talker dans ce fichier NMEA")