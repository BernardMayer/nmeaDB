#!/python
# -*- coding: utf-8 -*-

# http://sametmax.com/gestion-des-erreurs-en-python/
# https://openclassrooms.com/fr/courses/235344-apprenez-a-programmer-en-python/231688-gerez-les-exceptions

# https://stackoverflow.com/questions/1450393/how-do-you-read-from-stdin
# for line in sys.stdin :
    # print(line.strip())
# https://www.programcreek.com/python/example/2540/sys.__stdin__
# https://stackoverflow.com/questions/26499860/reading-from-stdin-in-python-2-7-6-sys-stdout-flush-and-python-u-doesnt-wor

# The NMEA checksum is an XOR of all the bytes (including delimiters such as ‘,’ but
# excluding the * and $) in the message output. It is therefore an 8-bit and not a 32-bit
# checksum for NMEA logs.
# https://nmeachecksum.eqth.net/
# http://code.activestate.com/recipes/576789-nmea-sentence-checksum/ (en bas de page)
# https://doschman.blogspot.com/2013/01/calculating-nmea-sentence-checksums.html
# https://www.numworks.com/fr/ressources/snt/trame-gps/

# // calculate the checksum:
# char checkSum(String theseChars) {
  # char check = 0;
  # // iterate over the string, XOR each byte with the total sum:
  # for (int c = 0; c < theseChars.length(); c++) {
    # check = char(check ^ theseChars.charAt(c));
  # } 
  # // return the result
  # return check;

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
import datetime
import re # pour le chksum_nmea...
import operator # pour le nmeaChecksum


"""
Convertir un log NMEA d'un format a un autre
[brut|NKE|NMEA]
"""


##  
##  Variables golbales
##  

fileIn = False
fileOut = False
fileFormat = 'BRUT'
fileOffset = 0
fileGps = False

nmeaGpsValid = False
epoch = 0

##
##  Fonctions
##


def nmeaChecksum(sentence) :
    ## On fait sentence jolie et propre ...
    ## On supprime ce qu'il y a devant !
    sentence = sentence[sentence.find("$"):]
    # print("sentence", sentence)
    
    # http://code.activestate.com/recipes/576789-nmea-sentence-checksum/ (en bas de page)
    sentence = sentence.strip('\n')
    nmeadata,cksum = sentence.split('*', 1)
    calc_cksum = reduce(operator.xor, (ord(s) for s in nmeadata), 0)
    return nmeadata,int(cksum,16),calc_cksum

def chksum_nmea(sentence):
    ## On fait sentence jolie et propre ...
    ## On supprime ce qu'il y a devant !
    # sentence = sentence[sentence.find("$"):]
    # print("sentence", sentence)
    
    ##  https://doschman.blogspot.com/2013/01/calculating-nmea-sentence-checksums.html
    
    # This is a string, will need to convert it to hex for 
    # proper comparsion below
    cksum = sentence[len(sentence) - 2:]
    
    # String slicing: Grabs all the characters 
    # between '$' and '*' and nukes any lingering
    # newline or CRLF
    chksumdata = re.sub("(\n|\r\n)","", sentence[sentence.find("$")+1:sentence.find("*")])
    
    # Initializing our first XOR value
    csum = 0 
    
    # For each char in chksumdata, XOR against the previous 
    # XOR'd char.  The final XOR of the last char will be our 
    # checksum to verify against the checksum we sliced off 
    # the NMEA sentence
    
    for c in chksumdata:
       # XOR'ing value of csum against the next char in line
       # and storing the new XOR value in csum
       csum ^= ord(c)
    
    return hex(int(csum))[2:].upper()

def xorString(str) :
    ret = 0
    for c in str :
        ret ^= ord(c)
    #return hex(ret)[2:].upper()
    ##  OK, mais peut ne retourner qu'un seul caractere...
    str = hex(ret)[2:].upper()
    if (len(str) == 1) :
        str = "0" + str
    return str

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
    elif (nbrVirgule > 1 and nmeaDollar > 6) :    
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

def estNmeaTemporelle(l) :
    ##
    global nmeaGpsValid, lineType # False, None
    dt = None
    hr = None
    # $IIZDA	194020,20,09,2017,,*5E
    # $IIGLL	4732.541,N,00253.770,W,151436,A,x*40                           A indique GPS valid
    # $--GGA,hhmmss.ss,llll.ll,a,yyyyy.yy,a,x,xx,x.x,x.x,M,x.x,M,x.x,xxxx*hh
    # $GPGGA,193428,4729.9205,N,00222.6770,W,2,11,1.0,-0.4,M,48.9,M,,*79       2 (ou 1) indique GPS fix
    # $--GLL,llll.ll,a,yyyyy.yy,a,hhmmss.ss,A*hh
    # $GPGLL,4729.9205,N,00222.6770,W,193428,A,D*57                            A indique GPS valid
    # $--RMB,A,x.x,a,c--c,c--c,llll.ll,a,yyyyy.yy,a,x.x,x.x,x.x,A*hh
    # $ECRMB,A,0.039,R,002,003,4728.046,N,00247.518,W,2.533,110.468,3.700,V*1F A indique GPS valid
    ## Suivant les materiels, l'heure peut etre hhmmss ou hhmmss.fff
    # $--RMC,hhmmss.ss,A,llll.ll,a,yyyyy.yy,a,x.x,x.x,xxxx,x.x,a*hh
    # $GPRMC,193428,A,4729.9205,N,00222.6770,W,0.0,143.5,200917,2.9,W,D*1C     A indique GPS valid
    nbrDollar = l.count("$")
    if (nbrDollar != 1) :
        return False
    dollar = l.find("$")
    nmea = l[dollar + 3:dollar + 6]
    lNmea = l[dollar + 7:].split(",")
    if (nmea == "RMC") :
        # print(lNmea)
        if (lNmea[1] == "A") :
            nmeaGpsValid = True
            # hr = lNmea[0]
            (hms, ms) = lNmea[0].split(".")
            dt = lNmea[8]
            ddmm = dt[0:4]
            dd = dt[0:2]
            mm = dt[2:4]
            yy = dt[4:]
            if (int(yy) < 70) :
                yy = "20" + yy
            else :
                yy = "19" + yy
            # print("  hms:", hms, " ms:", ms, " dd:", dd, " mm:", mm, " yy:", yy)
            temps = datetime.datetime.strptime(yy + mm + dd + "_" + hms, '%Y%m%d_%H%M%S')
            # temps.replace(tzinfo=None) # Pas necessaire, car on travaille en "naive", UTC par defaut
            epoch = (temps - datetime.datetime(1970, 1, 1)).total_seconds() # 1545895748.0
            return int(epoch)

    if (nmea == "ZDA") :
        # IIZDA [ $IIZDA,072558,01,06,2018,,*5E ] ts 20180601072558.0     ep 1527837958.0
        nmeaGpsValid = True
        hms = lNmea[0]
        dd = lNmea[1]
        mm = lNmea[2]
        yy = lNmea[3]
        temps = datetime.datetime.strptime(yy + mm + dd + "_" + hms, '%Y%m%d_%H%M%S')
        # temps.replace(tzinfo=None) # Pas necessaire, car on travaille en "naive", UTC par defaut
        epoch = (temps - datetime.datetime(1970, 1, 1)).total_seconds() # 1545895748.0
        return int(epoch)    

    return False
    
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
    global epoch
    if (not quelTypeDeLigne(l) == nmeaType) :
        return False
    if (nmeaType == 'NMEA') :
        return l
    if (nmeaType == 'NKE') :
        ##  il peut y avoir un offset a ajouter.  -t 1234567890
        ##  ou bien, on peut vouloir utiliser les infos GPS   -g
        # 0.422 $PNKEV,Box WiFi nke 3,V2.1,Aug 23 2017,17:04:14,00.1E.C0.39.41.44,V1.0*04
        #10.074 $IIRSA,4.0,A,,V*7D
        #268.729 $IIMWV,167,R,8.2,N,A*29
        (secms, nmea) = l.lstrip().split("$")
        nmea = "$" + nmea
        secms = secms.strip()
        (ts, ms) = secms.split(".")
        if (not fileGps) :
            if (fileOffset > 0) :
                ##  On ajoute un offset
                ret = str(long(ts) + long(fileOffset)) + ms
            else : 
                ret = secms
            ret = ret.replace(".", "")
            checksum = xorString(ret)
            return "\\c:" + ret + "*" + str(checksum) + "\\" + nmea
        else :
            ##  Transformation du format NKE en format BRUT 
            l = nmea

    ##  Dans tout les cas...
    ep = estNmeaTemporelle(l)
    if (ep > epoch) :
        epoch = ep
    # on ajoute les millisecondes a EPOCH
    ret = str(epoch) + "000"
    # checksum = chksum_nmea(str(epoch))
    checksum = xorString(ret)
    # (d, c, checksum) = nmeaChecksum(l)
    return "\\c:" + ret + "*" + str(checksum) + "\\" + l
    
def transformeEnNke(l, nmeaType) :
    # 0.422 $PNKEV,Box WiFi nke 3,V2.1,Aug 23 2017,17:04:14,00.1E.C0.39.41.44,V1.0*04
    #10.074 $IIRSA,4.0,A,,V*7D
    #268.729 $IIMWV,167,R,8.2,N,A*29
    if (not quelTypeDeLigne(l) == nmeaType) :
        return False
    global epoch
    
    if (nmeaType == 'NKE') :
        if (not fileOffset and not fileGps) : 
            return l
        (secms, nmea) = l.lstrip().split("$")
        nmea = "$" + nmea
        secms = secms.strip()
        (ts, ms) = secms.split(".")
        if (not fileGps) :
            ##  On ajoute l'offset
            ret = str(long(ts) + long(fileOffset))
        else : 
            ##  On recupere l'info GPS
            ep = estNmeaTemporelle(l)
            if (ep > epoch) :
                epoch = ep
            if (epoch > long(ts)) :
                ret = str(epoch)
                ##  Quand il n'y a pas d'infos GPS pendant plus d'une seconde, les ms sont incohérentes
                ms = "000"
            else :
                ret = ts
        ## Conserver la bizzarerie de l'espace au debut des premiers timestamp..
        if (len(ret) == 1) :
            ret = " " + ret
        return ret + "." + ms + " " + nmea
            
    if (nmeaType == 'BRUT') : 
        if (not fileOffset and not fileGps) : 
            return  " 0.000 " + l
        elif (fileOffset > 0) :
            ret = str(fileOffset)
            if (ret.find(".") > -1) :
                (ts, ms) = ret.split(".")
            else :    
                ts = ret
                ms = "000"
            if (len(ts) == 1) :
                ts = " " + ts
            return ts + "." + ms + " " + l    
        else :
            ##  On recupere l'info GPS
            ep = estNmeaTemporelle(l)
            if (ep > epoch) :
                epoch = ep
            if (epoch > 0) :
                ret = str(epoch)
            else :
                ret = "0"
            ## Conserver la bizzarerie de l'espace au debut des premiers timestamp..
            if (len(ret) == 1) :
                ret = " " + ret
            return ret + ".000 " + l

    if (nmeaType == 'NMEA') : 
        ##  On ignore -t et -g
        (pre, nmea) = l.split("$")
        posTs = pre.find("\\c:")
        pre = pre[posTs + 3:]
        ts = pre[:pre.find("*")]
        ## un TS de longueur > 10 est en ms, 
        ## car une longueur de 10 (TS = 9999999999) en sec nous emmene jusqu'au 2020-5-15
        if (len(ts) > 10) :
            ##  TS en millisecondes
            ts = ts[:-3] + "." + ts[-3:]
        else :
            ts = ts + ".000"
        return ts + " " + nmea    


    
    return "?"
    
    
    
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
countType = dict()
countType['????'] = 0
countType['BRUT'] = 0
countType['NKE'] = 0
countType['NMEA'] = 0

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
##  Maintenant, fd est   OU le fichier -i   OU sys.stdin   :-)
##

##  Determiner le type de fichier en entree
##  Detecter les infos TS dans les trames GPS
for line in fd :
    numLine += 1
    if (numLine < maxLine) :
        line = line.strip()
        lineType = quelTypeDeLigne(line)
        if (lineType) :
            countType[lineType] += 1
        else :
            countType['????'] += 1
            
        # print(lineType, "\t", line.strip())
        # if (lineType not in ('NMEA"', 'NKE')) :
            # ret = estNmeaTemporelle(line)
            # if (ret) :
                # epoch = epoch
        # print("epoch:", ret)
#print(countType)
maxVal = max(countType['????'], countType['BRUT'], countType['NKE'], countType['NMEA'])
##  Methode 2 : utiliser une liste de comprehension
##  https://waytolearnx.com/2019/04/recuperer-une-cle-dans-un-dictionnaire-a-partir-dune-valeur-en-python.html
lMax = [k for (k, val) in countType.items() if val == maxVal]
if (len(lMax) == 1) :
    lineType = lMax[0]
else :
    fd.close()    
    if (fileOut) :
        fOut.close()
    sys.exit()

print("Type de fichier en entree : " + str(lineType), file=sys.stderr)

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



