@cls
@setlocal enabledelayedexpansion
@rem 65001 UTF8, 850 	Multilingual (Latin I), 437 	United States, 1252 	West European Latin
@rem cscript.exe //U
@CHCP 65001

@set TAB=\t

@set homeDir=D:\_perso\bateau\TaC\nmeaDb
@set homePosix=D:\myTools\GOW
@set pythonHome=D:\myTools\Python\Python36
@set dbBin=D:\myTools\sqlite\sqlite3.exe

@rem Quels sont les differents talkers ?
@rem %pythonHome%\python.exe nmeaTalkers.py %nmeaFile%

@set nmeaDB=nmeaDb.sqlite


del %nmeaDB%
%dbbin% %nmeaDB% < nmeaDb_CreateTablesAndInsert.sql.txt

set nmeaFile=%homeDir%\datas\VHF_20151215.nmea
touch -m -t 201512151347.01 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\Sortie_20170922-01.nmea
touch -m -t 201709221204.30 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\Sortie_20170922-02.nmea
touch -m -t 201709221625.20 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\AISSinagot.nmea
touch -m -t 201709090909.09 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\Garmin152h.nmea
touch -m -t 201709202135.08 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\NkeLauBen.nmea
touch -m -t 201709202140.20 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\Calibration01.nmea
touch -m -t 201710261510.34 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%
