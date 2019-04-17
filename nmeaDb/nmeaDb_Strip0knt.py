#!/python
# -*- coding: utf-8 -*-
"""
Depuis un fichier JSON 
provenant d'un fichier NMEA pivote
Supprimer les parties au debut et a la fin pendant lesquelles le bateau ne bouge pas.
"""

### http://sametmax.com/lencoding-en-python-une-bonne-fois-pour-toute/
from __future__ import unicode_literals
### https://www.systutorials.com/241727/how-to-print-a-line-to-stderr-and-stdout-in-python/
# Permet en python 2.7 print("your message", file=sys.stderr) comme en Python 3
from __future__ import print_function
# http://python-future.org/compatible_idioms.html#long-integers
from builtins import int
# from past.builtins import long

import sys
import os

# Pour calcul de distance...
from math import sin, cos, acos, pi

import cgitb
cgitb.enable(format='text')
### http://sametmax.com/faire-manger-du-datetime-a-json-en-python/
import json

import decimal
decimal.getcontext().prec = 2

TAB = '\t'
FileOutSep = TAB
FileOutHeader = False
Verbose = True
#dIni['verbose'] = Verbose
# dtNow  = datetime.datetime.today()
# tsNow = dtNow.timestamp()
# dt1970 = datetime.datetime(1970, 1, 1)

##  Parametres
me = sys.argv[0]
#args = sys.argv[1:]
if (len(sys.argv) != 2) :
    print(me + " : Pas le bon nombre de parametres.", file=sys.stderr)
    print("Usage : " + me + " <Chemin et nom du fichier NMEA/JSON>", file=sys.stderr)
    quit()
else :
    nmeaFilename = sys.argv[1]
    if (nmeaFilename[-5:].upper() != ".JSON") :
        nmeaFilename = nmeaFilename + ".json"
    ## Tests prealables, fichier NMEA 
    if (not os.path.exists(nmeaFilename)) :
        print("E:Fichier", nmeaFilename, "introuvable", file=sys.stderr)
        quit()

## Ouvrir le fichier JSON
# https://www.w3resource.com/JSON/python-json-module-tutorial.php
# https://www.quennec.fr/trucs-astuces/langages/python/python-le-module-json
# https://docs.python.org/2/library/json.html
# https://code.tutsplus.com/tutorials/how-to-work-with-json-data-using-python--cms-25758
dJson = dict()
with open(nmeaFilename, "r") as fJson:
    dJson = json.load(fJson)   
print(dJson)
