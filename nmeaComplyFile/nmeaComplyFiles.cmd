@set oldPath=%PATH%
@set PATH=C:\LOGICIELS\Anaconda2;%PATH%

@rem type .\samples\Nav_20180608.nmea | python nmeaComplyFiles.py -i toto.in -o toto.out -f NKE -g -t 123456789
@rem python nmeaComplyFiles.py -i .\samples\Nav_20180608.nmea -o "./to to.out" -f NKE -g -t 1234567890
@rem python nmeaComplyFiles.py

@rem type .\samples\NKE00895.LOG | python nmeaComplyFiles.py   -f NMEA -g -t 1234567890
@rem type .\samples\Nav_20180608.nmea  | python nmeaComplyFiles.py  -f NMEA -g
@rem type .\samples\kplex-ms.nmea  | python nmeaComplyFiles.py  -f BRUT

@rem python nmeaComplyFiles.py -i .\samples\Nav_20180608.nmea  -f NKE -g -t 1234567890

@rem Fichier non conforme / sans NMEA
@rem type nmeaComplyFile-algo.txt | python nmeaComplyFiles.py

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

@rem Detection GPS temporalite
@rem GGA dans C:\AncienDisqueD\RepoS\nmeaDB\nmeaDb\datas\opcn-20170912-184500.nmea et 20181226_Sirf3-Boulot.nmea
@rem type C:\AncienDisqueD\RepoS\nmeaDB\nmeaDb\datas\20181226_Sirf3-Boulot.nmea | python nmeaComplyFiles.py   -f NMEA -o ./samples/testTransform2Brut.txt

@rem Transformer du NKE en NMEA pour pouvoir l'injecter dans qtVlm
@rem type .\samples\NKE00895.LOG | python nmeaComplyFiles.py  -o ./samples/testTransform2Brut.txt  -f NMEA
@rem type .\samples\NKE00895.LOG | python nmeaComplyFiles.py  -o ./samples/testTransform2Brut.txt  -f NMEA -t 1000000000
@rem python nmeaComplyFiles.py -i .\samples\NKE00895.LOG -o ./samples/testTransform2Brut.txt  -f NMEA -t 1000000000
type .\samples\Nav_20180601.nmea | python nmeaComplyFiles.py  -o ./samples/testTransform2Brut.txt  -f NMEA -g


@rem OU addition offset   OU recuperer le TS depuis trace GPS
@rem type .\samples\Nav_20180608.nmea | python nmeaComplyFiles.py   -f NMEA -g -t 1234567890 -o ./samples/testTransform2Brut.txt

@rem --- Detection des infos !!! valides !!! de type TS du GPS ---



@set PATH=%oldPath%
