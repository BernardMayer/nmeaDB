#!/python
# -*- coding: utf-8 -*-

# http://sametmax.com/gestion-des-erreurs-en-python/
# https://openclassrooms.com/fr/courses/235344-apprenez-a-programmer-en-python/231688-gerez-les-exceptions

### http://sametmax.com/lencoding-en-python-une-bonne-fois-pour-toute/
from __future__ import unicode_literals
### https://www.systutorials.com/241727/how-to-print-a-line-to-stderr-and-stdout-in-python/
# Permet en python 2.7 print("your message", file=sys.stderr) comme en Python 3
from __future__ import print_function
# http://python-future.org/compatible_idioms.html#long-integers
from builtins import int
# from past.builtins import long

import sys, os
import tempfile # https://docs.python.org/fr/2.7/library/tempfile.html

"""
Convertir un log NMEA d'un format a un autre
[brut|NKE|NMEA]
"""


##  
##  Variables golbales
##  

fileIn = False
# https://stackoverflow.com/questions/1450393/how-do-you-read-from-stdin
# for line in sys.stdin :
    # print(line.strip())
# https://www.programcreek.com/python/example/2540/sys.__stdin__
# https://stackoverflow.com/questions/26499860/reading-from-stdin-in-python-2-7-6-sys-stdout-flush-and-python-u-doesnt-wor
fileOut = False
fileFormat = 'BRUT'
fileOffset = 0
fileGps = False


##
##  Fonctions
##

##  Traitement de la ligne de commande
def validCmdline() :
    # python nmeaComplyFiles.py -i toto.in -o toto.out -f NKE -g -123456789
    # ['nmeaComplyFiles.py', '-i', 'toto.in', '-o', 'toto.out', '-f', 'NKE', '-g', '-123456789']
    global fileIn, fileOut, fileFormat, fileOffset, fileGps
    
    ##  Fichier en entree ?
    try :
        i = sys.argv.index('-i')
        try :
            fileIn = sys.argv[i + 1]
            # Le fichier existe ?
            if (not os.path.exists(fileIn)) :
                raise ValueError("Le fichier en entree [" + fileIn + "] existe ?")
        except ValueError as v :
            print(v)
            sys.exit()
    except Exception as e:
        pass 

    ##  Fichier en sortie ?
    try :
        i = sys.argv.index('-o')
        try :
            fileOut = sys.argv[i + 1]
            dir = os.path.dirname(fileOut)
            if (len(dir) == 0) :
                dir = "." + os.sep
                fileOut = dir + fileOut
            # print("dir[" + dir + "] \t fileOut[" + fileOut + "]")            
            if (not os.path.isdir(dir)) :
                raise ValueError("Le repertoire (" + dir + ") du fichier en sortie [" + fileOut + "] existe ?") 
        except ValueError as v :
            print(v)
            sys.exit()
    except Exception as e:
        pass 

    ## Format du log (NKE | NMEA | BRUT) ?
    try :
        i = sys.argv.index('-f')
        try :
            fileFormat = sys.argv[i + 1].upper()
            if (fileFormat not in ('NMEA', 'NKE', 'BRUT', '0')) :
                raise ValueError("[" + fileFormat + "] est different de NKE | NMEA | BRUT")
        except ValueError as v :
            print(v)
            sys.exit()
    except Exception as e:
        pass 

    ##  Valeur de l'offset plausible ?
    ##  410227200  == 1983-01-01
    ##  1000000000 == Sunday 9 September 2001
    ##  2524780800 == 2050-01-03
    # EPOCH du 1983-01-01 = 410227200 sec | 410227200000 msec (2536057289)
    try :
        i = sys.argv.index('-t')
        try :
            fileOffset = sys.argv[i + 1]
            try :
                fileOffset = long(fileOffset)
            except Exception as e :
                print("offset est numerique... [" + fileOffset + "]")
                sys.exit()
            if (fileOffset < 410227200 or fileOffset > 2524780800) : 
                raise ValueError("offset doit etre un epoch plausible [" + str(fileOffset) + "]")
        except ValueError as v :
            print(v)
            sys.exit()
    except Exception as e : 
        pass 

    ##  Usage des infos GPS ?
    try :
        i = sys.argv.index('-g')
        fileGps = True
    except Exception as e:
        pass 
    
    return True
    
def quelTypeDeLigne(l) :
    # global numLine, maxLine
    # nbrVirgule = 0
    # t = "...."
    # ts = ""
    # Combien de virgules dans la ligne ?
    nbrVirgule = l.count(",")
    dollar = l.find("$")
    nmeaDollar = l.find("\\$")
    if (dollar == 0 and nbrVirgule > 1) :
        # $GPRMC,192907.00,A,4714.34053,N,00131.57102,W,0.045,90.94,030418,,,A*46
        return "BRUT"
        # t = "BRUT"
    elif (nbrVirgule > 1 and nmeaDollar > 6 and l[0:3] == "\\c:") :    
        # \c:1468645546741*60\$WIMWV,44.0,R,11.0,N,A
        return "NMEA"
        # t = "NMEA"
    elif (nbrVirgule > 1 and dollar > 5 and nmeaDollar == -1) :
        #  1.643 $IIXDR,U,12.154,V,BatWiFi*16
        ts = l[0:dollar]
        # print("ts= ", ts)
        try : 
            ts = float(ts)
        except Exception as e :
            pass
        else :
            pass
            return "NKE"
            # t = "NKE"
        
    # print("t=" + t + " deb=" + l[0:3] + " virg=" + str(nbrVirgule) + " $=" + str(dollar) + " nmea$=" + str(nmeaDollar) + " ts=" + str(ts) + "\t\t" + l)

    return None
    
def transformeEnBrut(l, nmeaType) :
    if (not quelTypeDeLigne(l) == nmeaType) :
        return False
    # On retourne tout ce qui a a droite de $, $ compris
    dollar = l.find("$")
    if (dollar > -1) :
        return l[dollar:]
    else :
        return False
    
def transformeEnNmea(l, nmeaType) :
    if (not quelTypeDeLigne(l) == nmeaType) :
        return False
    ##  Quel traitement si format nmeaType == BRUT ?
    global ts
    
    return l
    
def transformeEnNke(l, nmeaType) :
    if (not quelTypeDeLigne(l) == nmeaType) :
        return False
    ##  Quel traitement si format nmeaType == BRUT ?
    global ts
    
    return l
    
    
    
me = sys.argv[0]
#args = sys.argv[1:]
#print(sys.argv)


##  
##  Traitement de la ligne de commande
##  
retCode = validCmdline()

##
##  Quel est le format d'entree ? (brut | NKE | NMEA)
##  Si (fileGps et fileFormat == BRUT) : premier timestamp valide (valide au sens GPS) et intervalle moyen
##

numLine = 0
maxLine = 100
lineType = None

if (fileOut) :
    fOut = open(fileOut, 'w')
if (not fileIn) :
    print("Lecture entree standard STDIN", file=sys.stderr)
    # STDIN est disponible 1 fois, alors fichier temporaire :-) 
    # with tempfile.NamedTemporaryFile('w+t', delete=False) as fTmp :
    fd = tempfile.NamedTemporaryFile('w+t', delete=False)
    for line in sys.stdin :
        fd.write(line)
    fd.seek(0)
else :
    print("Lecture du fichier [" + fileIn + "]", file=sys.stderr)
    fd = open(fileIn, 'r') 
##
##  Maintenant, fd est OU le fichier -i OU sys.stdin   :-)
##

##  Determiner le type de fichier en entree
for line in fd :
    numLine += 1
    if ((lineType is None) and (numLine < maxLine)) :
        lineType = quelTypeDeLigne(line.strip())
        # print(lineType, "\t", line.strip())
print("Type de fichier en entree:" + lineType, file=sys.stderr)

##  Si le type en entree en intelligible...
if (lineType is not None) :
    fd.seek(0)
    numLine = 0
    for line in fd :
        #print(line)
        numLine += 1
        if (fileFormat == 'BRUT') :
            l = transformeEnBrut(line, lineType)
        elif (fileFormat == 'NMEA') :
            l = transformeEnNmea(line, lineType)
        elif (fileFormat == 'NKE') :
            l = transformeEnNke(line, lineType)
        else :
            pass
        if (l) :
            if (fileOut) :
                fOut.write(l)
            else :
                print(l.strip())
# print("Lignes en sortie :", numLine, file=sys.stderr)

fd.close()    
if (fileOut) :
    fOut.close()




print("--------------------------------------")
print(fileIn)
print(fileOut)
print(fileFormat)
print(fileOffset)
print(fileGps)



