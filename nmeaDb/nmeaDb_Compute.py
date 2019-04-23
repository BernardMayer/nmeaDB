#!/python
# -*- coding: utf-8 -*-
"""
Depuis un fichier JSON
provenant d'un fichier NMEA pivote
Calculer depuis la mesure -10, la mesure -100
mediane compas HDM
mediane cap TMG du GPS
mediane vitesse loch VHW
mediane vitesse SOG du GPS
distance loch (VLW_dif010, VLW_dif100)
distance GPS (RMC lat lon)
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

# Pour boucler avec autre chose que des entiers ...
import itertools

TAB = '\t'
FileOutSep = TAB
FileOutHeader = False
Verbose = True
#dIni['verbose'] = Verbose
# dtNow  = datetime.datetime.today()
# tsNow = dtNow.timestamp()
# dt1970 = datetime.datetime(1970, 1, 1)

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

def mediane(maListe):
    # http://kamelnaroun.free.fr/python.html
    N = len(maListe)
    if (N == 0) :
        return None
    if (N == 1) :
        return maListe[0]
    maListe.sort()
    n = N / 2.0
    p = int(n)
    # if (n == p) :
        # return (maListe[p-1] + maListe[p]) / 2.0
    # else:
        # return maListe[p]
    return maListe[p]

def moyenne(tableau):
    # https://fr.wikibooks.org/wiki/Math%C3%A9matiques_avec_Python_et_Ruby/Statistique_inf%C3%A9rentielle_avec_Python
    return sum(tableau, 0.0) / len(tableau)

def variance(tableau):
    # https://fr.wikibooks.org/wiki/Math%C3%A9matiques_avec_Python_et_Ruby/Statistique_inf%C3%A9rentielle_avec_Python
    m=moyenne(tableau)
    return moyenne([(x-m)**2 for x in tableau])

def ecartype(tableau):
    # https://fr.wikibooks.org/wiki/Math%C3%A9matiques_avec_Python_et_Ruby/Statistique_inf%C3%A9rentielle_avec_Python
    return variance(tableau)**0.5

def dRange(x, y, jump) :
    # https://stackoverflow.com/questions/7267226/range-for-floats
    # https://pynative.com/python-range-for-float-numbers/
    # http://sametmax.com/les-nombres-en-python/
    x = decimal.Decimal(x)
    y = decimal.Decimal(y)
    while x < y:
        # http://sametmax.com/comment-utiliser-yield-et-les-generateurs-en-python/
        # yield float(x)
        yield decimal.Decimal(x)
        x += decimal.Decimal(jump)

def seqRange(start, end, step):
    assert(step != 0)
    sample_count = abs(end - start) / step
    return itertools.islice(itertools.count(start, step), sample_count)

def myRange(start, stop, step = 1):
    if (type(step) == "int") :
        arrondi = 0
    else :
        arrondi = str(step)
        pos = arrondi.find(".")
        if (pos > -1) :
            arrondi = len(arrondi) - pos - 1
        else :
            return None
    # print("arrondi =", arrondi)   
    stop = stop - step;
    number = int(round((stop - start) / float(step)))
    if number > 1:
        return([round(start + step * i, arrondi) for i in range(number + 1)])
    elif number == 1:
        return([start])
    else:
        return([])

def getDictCompute() :
    d = dict()
    d['Hdm_med10'] = list()
    d['Hdm_med100'] = list()
    d['RmcTmg_med10'] = list()
    d['RmcTmg_med100'] = list()
    d['VhwSow_med10'] = list()
    d['VhwSow_med100'] = list()
    d['RmcSog_med10'] = list()
    d['RmcSog_med100'] = list()
    # d[''] = list()
    return d
"""
  "timeRef": "GPRMC", 
  "posRef": "IIGLL", 
  "datas": {
    "1527837978.0": {
      "nLine": 2102, 
      "ts": 20180601072618.0, 
      "ECAPB": [], 
      "GPAPB": [], 
      "IIDBT": 4.8, 
      "IIHDM": 326.0, 
      "IIGLLlatNum": 47.50315, 
      "IIGLLlonNum": -1.613617, 
      "IIMTA": 18.8, 
      "IIMTW": 19.7, 
      "IIMWDtws": 2.2, 
      "IIMWDtwd": 224.0, 
      "RMCep": 1527837978.0, 
      "RMCts": 20180601072618.0, 
      "RMClatlon": "4730.18762,N,223.18327,W", 
      "RMClatNum": 47.503127, 
      "RMClonNum": -1.613612, 
      "RMCsog": 0.018, 
      "RMCtmg": [], 
      "IIVHWsow": 0.0, 
      "IIVLW": 36.73, 
      "IIVLWtotal": 135.0, 
      "IIVWRrl": "L", 
      "IIVWRawa": -102.0, 
      "IIVWRaws": 2.2, 
      "IIVWTrl": "L", 
      "IIVWTtwa": -102.0, 
      "IIVWTtws": 2.2, 
      "ZDAep": 1527837962.0, 
      "ZDAts": 20180601072602.0
    }, 
"""
##
##  MAIN
##

##  Parametres

##  Beaucoup de mesures dependent du GPS.
##  Cela implique un deplacement. En consequence, une vitesse minimale est requise
referenceCap = "IIHDM" # IIHDM RMCtmg
referenceVitesse = "IIVHWsow" # RMCsog IIVHWsow 
vitesseMini = 2

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

print("La reference cap est " + referenceCap + ". La reference vitesse est " + referenceVitesse + ", avec un mini a " + str(vitesseMini))

##  Comparer HDM vs TMG par dizaines
dHdmList = dict()
dTmgList = dict()
dDiffHdmTmg = dict()
dHdmTmg = dict()
for cap10 in range(0, 359, 10) :
    # print("cap10 =", cap10)
    dHdmList[cap10] = list()
    dTmgList[cap10] = list()
    dDiffHdmTmg[cap10] = list()
    dHdmTmg[cap10] = dict()

for ep in dJson['datas'] :
    if (dJson['datas'][ep][referenceVitesse] < vitesseMini) :
        continue
    if (dJson['datas'][ep][referenceCap]) :
        ##  cap10 est la partie dizaine de la valeur 359.7 --> 350 ; 45.1 --> 40 ; 7.3 --> 0
        # int pour supprimer la partie decimale, ouis str pour supprimer le dernier chiffre et le remplacer par 0, puis de nouveau int
        cap10 = int(str(int(dJson['datas'][ep][referenceCap]))[0:-1] + "0")
    else :
        continue
    # print("cap10 =", cap10, "\t\t\t", dJson['datas'][ep][referenceCap])
    hdm = int(dJson['datas'][ep]['IIHDM'])
    tmg = int(dJson['datas'][ep]['RMCtmg'])
    dHdmList[cap10].append(hdm)
    dTmgList[cap10].append(tmg)
    dDiffHdmTmg[cap10].append(hdm - tmg)

print(dHdmList)
print(dTmgList)
print(dDiffHdmTmg)

quit()
    
print("cap\tHDM\tTMG\tHDM-TMG\tnbrHDM\tnbrTMG")
for i, cap10 in enumerate(dHdmList) :
    if (dHdmList[cap10]) :
        dHdmTmg[cap10]['HDM'] = round(moyenne(dHdmList[cap10]), 1)
        dHdmTmg[cap10]['TMG'] = round(moyenne(dTmgList[cap10]), 1)
        dHdmTmg[cap10]['HDM-TMG'] = round(moyenne(dHdmTmg[cap10]), 1)
        dHdmTmg[cap10]['nbrHDM'] = len(dHdmList[cap10])
        dHdmTmg[cap10]['nbrTMG'] = len(dTmgList[cap10])
        # print(cap10, dHdmTmg[cap10]['HDM'], "\t", dHdmTmg[cap10]['TMG'], "\t",dHdmTmg[cap10]['HDM-TMG'], "\t", dHdmList[cap10], "\t", dTmgList[cap10])
        print(cap10, "\t", dHdmTmg[cap10]['HDM'], "\t", dHdmTmg[cap10]['TMG'], "\t",dHdmTmg[cap10]['HDM-TMG'], "\t", dHdmTmg[cap10]['nbrHDM'], "\t", dHdmTmg[cap10]['nbrTMG'])
    else :
        print(cap10, "\t -- \t -- \t -- \t0\t0")
dHdmList = dTmgList = dHdmTmg = None

quit()



    
    
dOut = dict()
calcul10 = calcul100 = False
lHdm_med10     = list()
lHdm_med100    = list()
lRmcTmg_med10  = list()
lRmcTmg_med100 = list()
lVhwSow_med10  = list()
lVhwSow_med100 = list()
lRmcSog_med10  = list()
lRmcSog_med100 = list()


lEpochs = list()
for ep in dJson['datas'] :
    # print(ep)
    lEpochs.append(ep)
iMax = len(lEpochs) - 1

# for i, ep in enumerate(lEpochs) :
for i in range(1, iMax) :
    ep = lEpochs[i]
    si = str(i)
    if (dJson['datas'][ep][referenceVitesse] < vitesseMini) :
        continue
    if (si[-1] == "0") :
        # Calcul a 10eme mesure
        dOut[ep] = getDictCompute()
        dOut[ep]['Hdm_med10'] = mediane(lHdm_med10)
        lHdm_med10.clear()
        dOut[ep]['RmcTmg_med10'] = mediane(lRmcTmg_med10)
        lRmcTmg_med10.clear()
        dOut[ep]['VhwSow_med10'] = mediane(lVhwSow_med10)
        lRmcTmg_med10.clear()
        dOut[ep]['RmcSog_med10'] = mediane(lRmcSog_med10)
        lRmcSog_med10.clear()
        if (si[-2] == "0") :
            # Calcul a 100eme mesure
            dOut[ep]['Hdm_med100'] = mediane(lHdm_med100)
            lHdm_med100.clear()
            dOut[ep]['RmcTmg_med100'] = mediane(lRmcTmg_med100)
            lRmcTmg_med100.clear()
            dOut[ep]['VhwSow_med100'] = mediane(lVhwSow_med100)
            lVhwSow_med100.clear()
            dOut[ep]['RmcSog_med100'] = mediane(lRmcSog_med100)
            lRmcSog_med100.clear()
    else :
        if (dJson['datas'][ep]['IIHDM']) :
            lHdm_med10.append(dJson['datas'][ep]['IIHDM'])
            lHdm_med100.append(dJson['datas'][ep]['IIHDM'])
        if (dJson['datas'][ep]['IIVHWsow']) :
            lVhwSow_med10.append(dJson['datas'][ep]['IIVHWsow'])
            lVhwSow_med100.append(dJson['datas'][ep]['IIVHWsow'])
        # Les infos GPS n'ont de sens que s'il y a déplacement...
        if (dJson['datas'][ep]['RMCsog'] > 0.7 and dJson['datas'][ep]['IIVHWsow'] > 0.7) :
            if (dJson['datas'][ep]['RMCtmg']) :
                lRmcTmg_med10.append(dJson['datas'][ep]['RMCtmg'])
                lRmcTmg_med100.append(dJson['datas'][ep]['RMCtmg'])
            if (dJson['datas'][ep]['RMCsog']) :
                lRmcSog_med10.append(dJson['datas'][ep]['RMCsog'])
                lRmcSog_med100.append(dJson['datas'][ep]['RMCsog'])
"""
ep : 1527850266.0    {'Hdm_med10': 91.0, 'Hdm_med100': [], 'RmcTmg_med10': 95.0, 'RmcTmg_med100': [], 'VhwSow_med10': 3.87, 'VhwSow_med100': [], 'RmcSog_med10': 3.571, 'RmcSog_med100': []}
ep : 1527850305.0    {'Hdm_med10': 84.0, 'Hdm_med100': 106.0, 'RmcTmg_med10': 89.0, 'RmcTmg_med100': 103.0, 'VhwSow_med10': 3.86, 'VhwSow_med100': 3.6, 'RmcSog_med10': 3.377, 'RmcSog_med100': 3.692}
ep : 1527850345.0    {'Hdm_med10': 83.0, 'Hdm_med100': [], 'RmcTmg_med10': 88.0, 'RmcTmg_med100': [], 'VhwSow_med10': 3.85, 'VhwSow_med100': [], 'RmcSog_med10': 3.319, 'RmcSog_med100': []}
"""



# print(dHdmList)
for ep in dOut :
    # if (dOut[ep]['RmcSog_med10'] and dOut[ep]['RmcSog_med10'] < 2) :
        # continue

    cap10 = int(dOut[ep]['Hdm_med10'] / 10) * 10
    cap = dOut[ep]['Hdm_med10']
    if (cap) :
        dHdmList[cap10].append(cap)
    tmg = dOut[ep]['RmcTmg_med10']
    if (tmg) :
        dTmgList[cap10].append(tmg)
print("cap\tHDM\tTMG\tHDM-TMG\tnbrHDM\tnbrTMG")
for i, cap10 in enumerate(dHdmList) :
    if (dHdmList[cap10] and dTmgList[cap10]) :
        dHdmTmg[cap10]['HDM'] = round(moyenne(dHdmList[cap10]), 1)
        dHdmTmg[cap10]['TMG'] = round(moyenne(dTmgList[cap10]), 1)
        dHdmTmg[cap10]['HDM-TMG'] = round(dHdmTmg[cap10]['HDM'] - dHdmTmg[cap10]['TMG'], 1)
        dHdmTmg[cap10]['nbrHDM'] = len(dHdmList[cap10])
        dHdmTmg[cap10]['nbrTMG'] = len(dTmgList[cap10])
        # print(cap10, dHdmTmg[cap10]['HDM'], "\t", dHdmTmg[cap10]['TMG'], "\t",dHdmTmg[cap10]['HDM-TMG'], "\t", dHdmList[cap10], "\t", dTmgList[cap10])
        print(cap10, "\t", dHdmTmg[cap10]['HDM'], "\t", dHdmTmg[cap10]['TMG'], "\t",dHdmTmg[cap10]['HDM-TMG'], "\t", dHdmTmg[cap10]['nbrHDM'], "\t", dHdmTmg[cap10]['nbrTMG'])
    else :
        print(cap10, "\t -- \t -- \t -- \t0\t0")
dHdmList = dTmgList = dHdmTmg = None

##  Comparer VHW / SOG par 0.2
dVhwList = dict()
dSogList = dict()
dVhwSog = dict()
# for vitesse in range(2.4, 24, 0.2) :
# for vitesse in myRange(2.4, 24, 0.287) :
for vitesse in range(vitesseMini, 24, 1) :
    print("vitesse =", vitesse)
    dVhwList[vitesse] = list()
    dSogList[vitesse] = list()
    dVhwSog[vitesse] = dict()
    
for ep in dOut :
    sog = dOut[ep]['VhwSow_med10']
    vhw = dOut[ep]['RmcSog_med10']
    if (dOut[ep]['VhwSow_med10'] and dOut[ep]['RmcSog_med10'] and dOut[ep]['VhwSow_med10'] > vitesseMini and dOut[ep]['RmcSog_med10'] > vitesseMini) :
        vitesse = round(sog)
        dVhwList[vitesse].append(dOut[ep]['VhwSow_med10'])
        dSogList[vitesse].append(dOut[ep]['RmcSog_med10'])
    
    
    
    
    
    
    
    
    
    
    
    
    
    
quit()



# print(dOut)
for ep in dOut :
    print("ep :", ep, "\t", dOut[ep])





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
