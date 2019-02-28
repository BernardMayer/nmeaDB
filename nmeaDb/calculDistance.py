#!/usr/bin/python3
# -*- coding: utf-8 -*-
 
"""
source : https://www.developpez.net/forums/d1868942/autres-langages/python-zope/contribuez/distance-entre-2-lieux-connus-leurs-coordonnees-gps/
Source pour le calcul: https://geodesie.ign.fr/contenu/fichiers/Distance_longitude_latitude.pdf
Voir aussi :
generalites https://fr.wikipedia.org/wiki/Coordonn%C3%A9es_g%C3%A9ographiques
en PSQL https://www.zebulon.fr/questions-reponses/calcul-de-distance-entre-deux-points-geographiques-121760.html
en PHP https://phpsources.net/code/php/maths/459_distance-en-metre-entre-deux-points-avec-coordonnees-gps
GeoPy :
https://geopy.readthedocs.io/en/stable/
https://pypi.org/project/geopy/

"""
 
from math import sin, cos, acos, pi
 
#############################################################################
def dms2dd(d, m, s):
    """Convertit un angle "degrés minutes secondes" en "degrés décimaux"
    """
    return d + m/60 + s/3600
 
#############################################################################
def dd2dms(dd):
    """Convertit un angle "degrés décimaux" en "degrés minutes secondes"
    """
    d = int(dd)
    x = (dd-d)*60
    m = int(x)
    s = (x-m)*60
    return d, m, s
 
#############################################################################
def deg2rad(dd):
    """Convertit un angle "degrés décimaux" en "radians"
    """
    return dd/180*pi
 
#############################################################################
def rad2deg(rd):
    """Convertit un angle "radians" en "degrés décimaux"
    """
    return rd/pi*180
 
#############################################################################
def distanceGPS(latA, longA, latB, longB):
    """Retourne la distance en mètres entre les 2 points A et B connus grâce à
       leurs coordonnées GPS (en radians).
    """
    # Rayon de la terre en mètres (sphère IAG-GRS80)
    RT = 6378137
    # angle en radians entre les 2 points
    S = acos(sin(latA)*sin(latB) + cos(latA)*cos(latB)*cos(abs(longB-longA)))
    # distance entre les 2 points, comptée sur un arc de grand cercle
    return S*RT
 
#############################################################################
if __name__ == "__main__":
 
    # cooordonnées GPS en radians du 1er point (ici, mairie de Tours)
    latA = deg2rad(47.390668) # Nord
    longA = deg2rad(0.689319) # Est
 
    # cooordonnées GPS en radians du 2ème point (ici, mairie de Limoges)
    latB = deg2rad(45.826516) # Nord
    longB = deg2rad(1.260290) # Est
 
    dist = distanceGPS(latA, longA, latB, longB)
    print(int(dist))