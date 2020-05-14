#!/python
# -*- c....g: ascii -*-
# -*- coding: utf-8 -*-


### http://sametmax.com/lencoding-en-python-une-bonne-fois-pour-toute/
from __future__ import unicode_literals
### https://www.systutorials.com/241727/how-to-print-a-line-to-stderr-and-stdout-in-python/
# Permet en python 2.7 print("your message", file=sys.stderr) comme en Python 3
from __future__ import print_function
# http://python-future.org/compatible_idioms.html#long-integers
from builtins import int
# from past.builtins import long

"""
The NMEA checksum is an XOR of all the bytes (including delimiters such as "," but excluding the * and $)
 in the message output. It is therefore an 8-bit and not a 32-bit checksum for NMEA logs.
    In Java script:
        var checksum = 0;
        for(var i = 0; i < stringToCalculateTheChecksumOver.length; i++) {
          checksum = checksum ^ stringToCalculateTheChecksumOver.charCodeAt(i);
        }
    In C#:
        int checksum = 0;
        for (inti = 0; i < stringToCalculateTheChecksumOver.length; i++){
        checksum ^= Convert.ToByte(sentence[i]);}
    In VB.Net:
        Dim checksum as Integer = 0
        For Each Character As Char In stringToCalculateTheChecksumOver 
                  checksum = checksum Xor Convert.ToByte(Character)
        Next 
https://nmeachecksum.eqth.net/
http://code.activestate.com/recipes/576789-nmea-sentence-checksum/ (en bas de page)
https://doschman.blogspot.com/2013/01/calculating-nmea-sentence-checksums.html
https://www.numworks.com/fr/ressources/snt/trame-gps/
https://www.tigoe.com/pcomp/code/Processing/127/
$GPGGA,072841.000,4714.3221,N,00131.5486,W,1,08,1.6,36.1,M,48.5,M,,0000*7C
$GPGSA,A,3,03,01,23,09,11,18,31,22,,,,,2.4,1.6,1.7*34
$GPRMC,072841.000,A,4714.3221,N,00131.5486,W,0.13,95.85,271218,,,A*40
\c:0000*0L\$GPGSA,A,3,03,01,23,09,11,18,31,22,,,,,2.4,1.6,1.7*34
\c:1545895721000*34L\$GPGSA,A,3,03,01,23,09,11,18,31,22,,,,,2.4,1.6,1.7*34
\c:1545895722000*34L\$GPGSA,A,3,03,01,23,09,11,18,31,22,,,,,2.4,1.6,1.7*34
\c:1545895723000*34L\$GPGSA,A,3,03,01,23,09,11,18,31,22,,,,,2.4,1.6,1.7*34
\c:1545895724000*34L\$GPGSA,A,3,03,01,23,09,11,18,31,22,,,,,2.4,1.6,1.7*34
\c:1545895725000*34L\$GPGSA,A,3,03,01,23,09,11,18,31,22,,,,,2.4,1.6,1.7*34
\c:1545895726000*34L\$GPGSA,A,3,03,01,23,09,11,18,31,22,,,,,2.4,1.6,1.7*34
\c:1545895727000*34L\$GPGSA,A,3,03,01,23,09,11,18,31,22,,,,,2.4,1.6,1.7*34
\c:1545895728000*34L\$GPGSA,A,3,03,01,23,09,11,18,31,22,,,,,2.4,1.6,1.7*34
\c:1545895729000*34L\$GPGSA,A,3,03,01,23,09,11,18,31,22,,,,,2.4,1.6,1.7*34
\c:1545895730000*35L\$GPGSA,A,3,03,01,23,09,11,18,31,22,,,,,2.4,1.6,1.7*34
"""

import re

def chksum_nmea(sentence):
    ## On fait sentence jolie et propre ...
    ## On supprime ce qu'il y a devant !
    sentence = sentence[sentence.find("$"):]
    # print("sentence", sentence)
    
    ##  https://doschman.blogspot.com/2013/01/calculating-nmea-sentence-checksums.html
    
    # This is a string, will need to convert it to hex for 
    # proper comparsion below
    #############cksum = sentence[len(sentence) - 2:]
    cksum = sentence[len(sentence) - 3:]
    
    # String slicing: Grabs all the characters 
    # between '$' and '*' and nukes any lingering
    # newline or CRLF
    chksumdata = re.sub("(\n|\r\n)","", sentence[sentence.find("$")+1:sentence.find("*")])
    print(chksumdata)
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
    
    return hex(csum)#[2:].upper()
    
    # Do we have a validated sentence?
    if hex(csum) == hex(int(cksum, 16)):
       return True

    return False
    
def xorString(str) :
    ret = 0
    for c in str :
        ret ^= ord(c)
    ##  OK, mais peut ne retourner qu'un seul caractere...
    #return hex(ret)[2:].upper()
    str = hex(ret)[2:].upper()
    if (len(str) == 1) :
        str = "0" + str
    return str


lines = list()
# lines.append("$GPGGA,072841.000,4714.3221,N,00131.5486,W,1,08,1.6,36.1,M,48.5,M,,0000*7C")
# lines.append("$GPGSA,A,3,03,01,23,09,11,18,31,22,,,,,2.4,1.6,1.7*34")
# lines.append("$GPRMC,072841.000,A,4714.3221,N,00131.5486,W,0.13,95.85,271218,,,A*40")
lines.append("1545895721000") # *35
lines.append("1545895722000") # *36
lines.append("1545895723000") # *37
lines.append("1545895724000") # *30
lines.append("1545895725000") # *31
lines.append("1545895726000") # *32
lines.append("1545895727000") # *33
lines.append("1545895728000") # *3C
lines.append("1545895729000") # *3D
lines.append("1545895730000") # *35
lines.append("0")

for line in (lines) : 
    #csum = chksum_nmea(line)
    csum = xorString(line)
    print(line, "->", csum)

