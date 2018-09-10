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
@set nmeaFileID=5
@set nmeaValeurDuPas=600

%pythonHome%\python.exe nmeaRun.py %homeDir%\%nmeaDB% %nmeaFileID% %nmeaValeurDuPas%

@echo "--- fin import %nmeaFile% ---"
