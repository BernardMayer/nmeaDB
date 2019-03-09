@set oldPath=%PATH%
@set gnuDir="C:\CAT_dskD\myTools\GOW"
@set PATH=%gnuDir%;%PATH%
@set baseDir=C:\RepoGit\nmeaDB\nmeaDb\datas
@echo Recherche des debut de phrases NMEA


popd %baseDir%
@rem https://www.blaess.fr/christophe/2013/04/08/optimiser-les-recherches-recursives-avec-xargs/
@rem https://www.tuteurs.ens.fr/unix/exercices/solutions/grep-sol.html
@rem Bordel de merde d'antislash !
@rem gfind %baseDir% -type f -name *.nmea -print
@rem gfind %baseDir% -type f -name *.nmea -exec grep GPRMC {} \;
@rem %gnuDir%\gfind . -type f -name *.nmea -print | %gnuDir%\xargs %gnuDir%\grep RMC
%gnuDir%\gfind . -type f -name *.nmea -print | %gnuDir%\xargs %gnuDir%\cut -c 1-6 | %gnuDir%\sort | %gnuDir%\uniq --ignore-case > chercheDebutLigne.txt

pushd

@set PATH=%oldPath%