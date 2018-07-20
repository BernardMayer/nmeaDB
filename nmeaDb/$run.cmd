@cls
@setlocal enabledelayedexpansion
@rem 65001 UTF8, 850 	Multilingual (Latin I), 437 	United States, 1252 	West European Latin
@rem cscript.exe //U
@CHCP 65001

@set TAB=\t

@REM @set homeDir=D:\_perso\bateau\TaC\nmeaDb
@REM @set dataDir=C:\RepoGit\Bateau\TaC\Terminal
@REM @set homePosix=D:\myTools\GOW
@REM @set pythonHome=D:\myTools\Python\Python36
@REM @set dbBin=D:\myTools\sqlite\sqlite3.exe

@set homeDir=C:\RepoGit\nmeaDB\nmeaDb
@set dataDir=C:\RepoGit\Bateau\TaC\Terminal
@set homePosix=C:\CAT_dskD\myTools\GOW
@set pythonHome=C:\CAT_dskD\myTools\Python\Python36
@set dbBin=C:\CAT_dskD\myTools\sqlite\sqlite3.exe

@rem Quels sont les differents talkers ?
@rem %pythonHome%\python.exe nmeaTalkers.py %nmeaFile%

@set nmeaDB=nmeaDb.sqlite

del %nmeaDB%
%dbbin% %nmeaDB% < nmeaDb_CreateTablesAndInsert.sql.txt
%homePosix%\sleep 1

set nmeaFile=%dataDir%\Nav_20180608.nmea
%homePosix%\touch -m -t 201806080808.08 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

echo "--- fin import %nmeaFile% ---"
pause

set nmeaFile=%homeDir%\datas\AISSinagot.nmea
touch -m -t 201709090909.09 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\Calibration01.nmea
touch -m -t 201710261510.34 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\Garmin152h.nmea
touch -m -t 201709202135.08 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\NkeLauBen.nmea
touch -m -t 201709202140.20 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\VHF_20151215.nmea
touch -m -t 201512151347.01 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\opcn-20170911-082000.nmea
touch -m -t 201709110820.00 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\opcn-20170911-164500.nmea
touch -m -t 201709111645.00 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\opcn-20170912-081000.nmea
touch -m -t 201709120810.00 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\opcn-20170912-184500.nmea
touch -m -t 201709121845.00 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\opcn-20170913-081500.nmea
touch -m -t 201709130815.00 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\opcn-20170913-163000.nmea
touch -m -t 201709131630.00 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\Sortie_20170922-01.nmea
touch -m -t 201709221204.30 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\Sortie_20170922-02.nmea
touch -m -t 201709221625.20 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%

set nmeaFile=%homeDir%\datas\VHF_20151215.nmea
touch -m -t 201512151347.01 %nmeaFile%
%pythonHome%\python.exe nmeaImportNmeaFile.py  %nmeaFile% %nmeaDB%
