@set oldPath=%PATH%
@set PATH=C:\LOGICIELS\Anaconda2;%PATH%

@rem type .\samples\Nav_20180608.nmea | python nmeaComplyFiles.py -i toto.in -o toto.out -f NKE -g -t 123456789
@rem python nmeaComplyFiles.py -i .\samples\Nav_20180608.nmea -o "./to to.out" -f NKE -g -t 1234567890
@rem python nmeaComplyFiles.py

@rem type .\samples\NKE00895.LOG | python nmeaComplyFiles.py   -f NMEA -g -t 1234567890
@rem type .\samples\Nav_20180608.nmea  | python nmeaComplyFiles.py  -f NMEA -g
@rem type .\samples\kplex-ms.nmea  | python nmeaComplyFiles.py  -f BRUT

@rem python nmeaComplyFiles.py -i .\samples\Nav_20180608.nmea  -f NKE -g -t 1234567890

@rem Transformer du NKE en BRUT, pour pouvoir faire des polaires
@rem type .\samples\NKE00895.LOG | python nmeaComplyFiles.py   -f BRUT -o ./samples/testNke2Brut.txt
@rem python nmeaComplyFiles.py   -f BRUT -o ./samples/testNke2Brut.txt -i .\samples\NKE00895.LOG 
@rem type .\samples\NKE00895.LOG | python nmeaComplyFiles.py   -f BRUT
@rem python nmeaComplyFiles.py   -f BRUT  -i .\samples\NKE00895.LOG

@rem Transformer du NMEA en BRUT, pour pouvoir faire des polaires
@rem type .\samples\kplex-ms.nmea  | python nmeaComplyFiles.py   -f BRUT
@rem python nmeaComplyFiles.py   -f BRUT -i .\samples\kplex-ms.nmea
@rem type .\samples\kplex-ms.nmea  | python nmeaComplyFiles.py   -f BRUT -o ./samples/testTransform2Brut.txt
@rem python nmeaComplyFiles.py   -f BRUT -i .\samples\kplex-ms.nmea -o ./samples/testTransform2Brut.txt

@rem Transformer du NKE en NMEA pour pouvoir l'injecter dans qtVlm
@rem OU addition offset   OU recuperer le TS depuis trace GPS
type .\samples\NKE00895.LOG | python nmeaComplyFiles.py   -f NMEA -g -t 1234567890

@rem --- Detection des infos !!! valides !!! de type TS du GPS ---



@set PATH=%oldPath%
