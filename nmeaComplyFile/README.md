---
title: Conformer le format du fichier log NMEA
---
==============================================


Afin de traiter correctement les fichiers de collecte NMEA, il convient de les conformer.

Fichier brut, une phrase NMEA par ligne
---------------------------------------
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!AIVDO,1,1,,,B3HvFrP007v@>06hO6p03wR5sP06,0*20
$GPRMC,192907.00,A,4714.34053,N,00131.57102,W,0.045,90.94,030418,,,A*46
$GPGBS,192911.00,4.8,4.4,6.8,,,,*40
!AIVDO,1,1,,,B3HvFrP007v@>2VhO6dt;wV5sP06,0*1E
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

NKE
---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
==> Box WiFi V2.1  Start logging
 0.422 $PNKEV,Box WiFi nke 3,V2.1,Aug 23 2017,17:04:14,00.1E.C0.39.41.44,V1.0*04
 1.643 $IIXDR,U,12.154,V,BatWiFi*16
 1.698 $IIDPT,4.7,,*41
 1.700 $IIDBT,15.4,f,4.7,M,,*4A
 1.743 $IIRSA,4.3,A,,V*7E
 1.749 $IIVLW,,N,30.16,N*67
 1.753 $IIVLW,525.16,N,30.16,N*7C
 1.917 $IIXDR,C,11.4,C,AirTemp*22
 1.921 $IIMTW,8.7,C*2C
 2.009 $IIVHW,,T,,M,0.00,N,0.00,K*55
 2.013 $IIMWV,,R,1.4,N,A*16
 2.016 $IIVWR,,,1.4,N,0.7,M,2.6,K*33
 2.020 $IIVHW,,T,230,M,0.00,N,0.00,K*64
 2.023 $IIMWV,173,R,1.4,N,A*23
 2.035 $IIVWR,173,R,1.4,N,0.7,M,2.6,K*54
 2.037 $IIHDG,230,,,,*56
 2.038 $IIHDM,230,M*3D
 3.788 $IIDPT,4.8,,*4E
 3.790 $IIDBT,15.8,f,4.8,M,,*49
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.../...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
268.029 $IIXDR,C,12.6,C,AirTemp*23
268.050 $IIMWV,167,R,8.1,N,A*2A
268.053 $IIVWR,167,R,8.1,N,4.2,M,15.0,K*6C
268.729 $IIMWV,167,R,8.2,N,A*29
268.732 $IIVWR,167,R,8.2,N,4.2,M,15.2,K*6D
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

La norme NMEA-0183v4 TAG (kplex et read183)
-------------------------------------------
[http://www.nmea.org/Assets/may%2009%20rtcm%200183_v400.pdf](http://www.nmea.org/Assets/may%2009%20rtcm%200183_v400.pdf)
[https://groups.google.com/forum/\#!forum/kplex](https://groups.google.com/forum/#!forum/kplex)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\c:1468645546741*60\$WIMWV,44.0,R,11.0,N,A
\c:1468645546784*69\$GPGSA,A,3,27,8,9,16,7,,,30,,,,,4.00,1.70,3.60*32
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Je vais faire un outil qui transforme un de ces formats vers un autre.
Si le TS démarre à zero
, ou on le conserve
, ou on lui donne une autre valeur de depart
, ou on recupere la valeur dans une valeur de temps de GPS

Si le TS est absent, on determine l'increment a partir de valeur de GPS, avec
des valeurs intermediaires approximatives.
