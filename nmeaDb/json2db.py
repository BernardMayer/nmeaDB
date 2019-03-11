#!/python
# -*- coding: utf-8 -*-

"""
Importer un fichier JSON de structure connue vers 1 table de DB 
"""

### http://sametmax.com/lencoding-en-python-une-bonne-fois-pour-toute/
from __future__ import unicode_literals
### https://www.systutorials.com/241727/how-to-print-a-line-to-stderr-and-stdout-in-python/
# Permet en python 2.7 print("your message", file=sys.stderr) comme en Python 3
from __future__ import print_function
# http://python-future.org/compatible_idioms.html#long-integers
from builtins import int
# from past.builtins import long

"""
Construire une structure de donnees,
liste ordonnee (clef = timestamp) de 
structure des informations dispo entre 2 timestamps
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

## fichier a traiter
me = sys.argv[0]
#args = sys.argv[1:]
if (len(sys.argv) != 3) :
    print(me + " : Pas le bon nombre de parametres.", file=sys.stderr)
    print("Usage : " + me + " <Chemin et nom du fichier NMEA pivote> <Chemin et nom du fichier NMEA pivote enrichi>", file=sys.stderr)
    quit()
else :
    nmeaFilename = sys.argv[1]
    nmeaRichFilename = sys.argv[2]
    print("I;Enrichissement du fichier NMEA [" + nmeaFilename + "] vers le ficher NMEA [" + nmeaRichFilename + "]", file=sys.stderr)

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
mTimeEpoch = int(os.path.getmtime(nmeaFilename)) # format epoch
# print("mTimeEpoch : " + str(mTimeEpoch))
# print(datetime.datetime.utcfromtimestamp(mTimeEpoch)) # 2017-10-19 13:40:11
mTimeStruct = time.localtime(mTimeEpoch)
# print("mTimeStruct : " + str(mTimeStruct)) # mTimeLocal : time.struct_time(tm_year=2017, tm_mon=10, tm_mday=19, tm_hour=15, tm_min=40, tm_sec=11, tm_wday=3, tm_yday=292, tm_isdst=1)
mTimeIso = time.strftime("%Y%m%d%H%M%S", mTimeStruct)
# print("mTimeIso : " + mTimeIso)

basename = os.path.basename(nmeaFilename)

