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
# print(dJson)
# print(len(dJson['datas']))

##  Fabriquer une liste des epochs, pour parcourir le dict a rebours
lEpochs = list()
for ep in dJson['datas'] :
    # print(ep)
    lEpochs.append(ep)

##  Combien de valeurs de deplacement a zero ?
nZeroAvant = nZeroApres = 9
nZero = 0

##  Quelles variables contiennent du deplacement ?
## RMCsog, IIVHWsow
temoin = "IIVHWsow"
RMCsog = RMCsog = 0
ep2Del = None

print("initial :", len(dJson['datas']))

for i, ep in enumerate(lEpochs) :
    if (decimal.Decimal(dJson['datas'][ep][temoin]) > 0.0) :
        nZero = 0
        ep2Del = "FinDeAvant"
        ##  On peut sortir de la boucle,
        ##  si on decide qu'une seule valeur > 0 est suffisament symptomatique
        ##  pas sur si on se base sur RMC ...
        ##  quid des bateaux a l'arret dans du courant ?
        break
    else :
        nZero += 1
    if (i < nZeroAvant) :
        continue
    if (nZero >= nZeroAvant and ep2Del != "FinDeAvant") :
        # bingo !
        ep2Del = lEpochs[i - nZeroAvant] # i - nZeroAvant
        del dJson['datas'][ep2Del]
    print("i =", i, ", ep =", ep, ", sow =", dJson['datas'][ep][temoin], ", nZero =", nZero, ", ep2Del =", ep2Del)
        
print("strip le debut :", len(dJson['datas']))

lEpochs.reverse()

for i, ep in enumerate(lEpochs) :
    if (decimal.Decimal(dJson['datas'][ep][temoin]) > 0.0) :
        nZero = 0
        ep2Del = "FinDeApres"
        ##  On peut sortir de la boucle,
        ##  si on decide qu'une seule valeur > 0 est suffisament symptomatique
        ##  pas sur si on se base sur RMC ...
        ##  quid des bateaux a l'arret dans du courant ?
        break
    else :
        nZero += 1
    if (i < nZeroApres) :
        continue
    if (nZero >= nZeroAvant and ep2Del != "FinDeApres") :
        # bingo !
        ep2Del = lEpochs[i - nZeroAvant] # i - nZeroAvant
        del dJson['datas'][ep2Del]
    print("i =", i, ", ep =", ep, ", sow =", dJson['datas'][ep][temoin], ", nZero =", nZero, ", ep2Del =", ep2Del)
    
print("strip la fin :", len(dJson['datas']))

# f = open(nmeaFilename + "-strip.json", 'w')
# json.dump(dJson, f, indent=2, separators=(", ", ": "))  
# f.close()    
