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
    print("Import du fichier NMEA [" + nmeaFilename + "] dans la base Sqlite [" + nmeaDbname + "]")

## Tests prealables
if (not os.path.exists(nmeaFilename)) :
    print("Fichier", nmeaFilename, "introuvable")
    quit()
if (not os.path.exists(nmeaDbname)) :
    print("Base", nmeaDbname, "introuvable")
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
    print("Pb avec la DB [" + nmeaDbname + "]")
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

## Verification de la presence de ces donnees ...
#sql = "SELECT DISTINCT fileName, fileTsWrite FROM nmeaFiles WHERE fileName LIKE '%" + "ZZZ" + basename + "%' OR fileCheck LIKE '" + fileCheck + "ZZZ" + "' OR fileTsWrite = " + mTimeIso + "999" + ";"
sql = "SELECT DISTINCT FileName, FileTsWrite FROM nmeaFiles WHERE FileName LIKE '%" + basename + "%' OR FileCheck LIKE '" + fileCheck + "' OR FileTsWrite = " + mTimeIso + ";"
cursor.execute(sql)
res = cursor.fetchone()
#print("res =", res)
if (res != None) :
    (candidatName, candidatTsWrite) = res
    print("Un fichier " + candidatName + " du " + str(candidatTsWrite) + ", fort similaire, existe dans la base.")
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
    ## feed nmeaValues
    sql = "INSERT INTO nmeaValues(FileID, FileLineNum, NmeaID, NmeaVal) VALUES (?, ?, ?, ?);" # " + fileId + ", " + nLine + ", '" + id + "', '" + val + "'
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
            cursor.execute(sql, (fileId, nLine, id, val))    
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