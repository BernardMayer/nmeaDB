#!/python
# -*- coding: utf-8 -*-

### http://sametmax.com/lencoding-en-python-une-bonne-fois-pour-toute/
from __future__ import unicode_literals

"""
Extraire le talker d'une phrase NMEA 0183
$IIVLW,0088.0,N,088.65,N*4E
$IIVHW,,,268.,M,01.44,N,02.66,K*10
!AIVDO,1,1,,,B3HvFrP00?uA@GVjqa@03wc5wP06,0*2D
"""

import cgitb
cgitb.enable(format='text')
import pyodbc
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
if (len(sys.argv) == 1) :
    print("Le fichier NMEA dit etre le 1er parametre de " + me)
    quit()
if (len(sys.argv) >= 2) :
    nmeaFilename = sys.argv[1]
    print("Traitement du fichier NMEA " + nmeaFilename)

## Lecture du fichier
dTalkers = dict()
dPropSentences = dict()
if (not os.path.exists(nmeaFilename)) :
    print("Fichier", nmeaFilename, "introuvable")
    quit()
with open(nmeaFilename, 'r') as fNmea :
    nLine = 0
    for line in fNmea.readlines() :
        nLine += 1
        if (line[0:1] == "$") :
            if (line[0:2] == "$P") :
                pass
                pos = line.find(',')
                if (pos > 0) :
                    propSentence = line[0:pos]
                else :
                    propSentence = line[0:7]
                try :
                    dPropSentences[propSentence] = dPropSentences[propSentence] + 1
                except :
                    dPropSentences[propSentence] = 1
            else :
                idTalker = line[1:3]
                try :
                    dTalkers[idTalker] = dTalkers[idTalker] + 1
                except :
                    dTalkers[idTalker] = 1
                #lTalkers.append(idTalker)
print(dTalkers)
print(dPropSentences)
if (len(dTalkers) > 0) :
    print("idTalker" + TAB + "Nombre")
    for (k, v) in dTalkers.items()  :
        print(k, TAB, v)
else :
    print("Pas de talker dans ce fichier NMEA")