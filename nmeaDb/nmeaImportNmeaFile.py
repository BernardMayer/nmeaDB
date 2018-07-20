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


#bShowIdentifier = os.getenv("dsXidentifier", False)

## fichier a traiter
me = sys.argv[0]
#args = sys.argv[1:]
if (len(sys.argv) != 3) :
    print(me + " : Pas le bon nombre de parametres.")
    print("Usage : " + me + " <Chemin et nom du fichier NMEA> <Chemin et nom de la base Sqlite>")
    quit()
else :
    nmeaFilename = sys.argv[1]
    nmeaDbname = sys.argv[2]
    print("I;Import du fichier NMEA [" + nmeaFilename + "] dans la base Sqlite [" + nmeaDbname + "]")

## Tests prealables
if (not os.path.exists(nmeaFilename)) :
    print("E:Fichier", nmeaFilename, "introuvable")
    quit()
if (not os.path.exists(nmeaDbname)) :
    print("E:Base", nmeaDbname, "introuvable")
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
    print("E:Pb avec la DB [" + nmeaDbname + "]")
    db.close()
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
        if (gll[1] == 'N') :
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
            print("I;Utilisation des trames IIGLL et IIZDA pour marquage spatial et temporel")
            if (favori == 'G') :
                favori = 'I'
                print("W; ! Les trames preferees deviennent les trames $II !")
            xydt = True
        else :
            if (ttRMC or ttZDA) :
                ##  Test de la quantite de RMC (2% de l'echantillon)
                if (nbRMC > (NbrSampleLines / 50)) :
                    dtTrameTypesList = ('$IIRMC', '$ECRMC', '$GPRMC')
                    print("I;Utilisation exclusive de trames RMC pour marquage temporel")
                    if (favori == 'I') :
                        favori = 'G'
                        print("W; ! Les trames preferees deviennent les trames $GPRMC !")
                else :
                    dtTrameTypesList = ('$IIRMC', '$ECRMC', '$GPRMC', '$IIZDA', '$ECZDA')
                    print("I;Utilisation de trames RMC et ZDA pour marquage temporel")
                    favori = ''
                    print("W; ! Plus de trames preferee !")
                xydt = True
            else :
                print("W; ! Pas de marquage temporel possible !")
            ##  Test si marquage spatial possible
            if (ttRMC or ttGLL or ttGGA) :
                ##  Test de la quantite de RMC (2% de l'echantillon)
                if (nbRMC > (NbrSampleLines / 50)) :
                    xyTrameTypesList = ('$IIRMC', '$ECRMC', '$GPRMC')
                    print("I;Utilisation exclusive de trames RMC pour marquage spatial")
                    if (favori == 'I') :
                        favori = 'G'
                        print("W; ! Les trames preferees deviennent les trames $GPRMC !")
                else :
                    xyTrameTypesList = ('$IIRMC', '$ECRMC', '$GPRMC', '$ECGLL', '$GPGLL', '$ECGGA', '$GPGGA', '$IIGLL', '$IIGGA')
                    print("I;Utilisation trames RMC, GLL et GGA pour marquage spatial")
                    favori = ''
                    print("W; ! Plus de trames preferee !")
                xydt = True
            else :
                print("W; ! Pas de marquage spatial possible !")
    
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
    print("Pb avec import de [" + nmeaFilename + "]")
    print(e)
    



    
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