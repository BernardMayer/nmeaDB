def DMd2Dd(dmd) :
    # DDDMM.d --> DDD.d (S or W negative values)
    # 10601.6986 ---> 106+1.6986/60 = 106.02831 degrees
    # "GLL": "4730.189,N,223.183,W"
    dotPos = dmd.find(".")
    D = float(dmd[0:dotPos - 2])
    M = float(dmd[dotPos - 2:]) / 60
    return (D + M)

print(str(DMd2Dd("10601.6986")), " 106.02831 degrees")

print(str(DMd2Dd("10601.001")), " 106.001 degrees")
print(str(DMd2Dd("10601.002")), " 106.002 degrees")

print(str(DMd2Dd("10601.0001")), " 106.0001 degrees")
print(str(DMd2Dd("10601.0002")), " 106.0002 degrees")

print(str(DMd2Dd("10601.00001")), " 106.00001 degrees")
print(str(DMd2Dd("10601.00002")), " 106.00002 degrees")

print(str(DMd2Dd("10601.000001")), " 106.000001 degrees")
print(str(DMd2Dd("10601.000002")), " 106.000002 degrees")

"""
http://family.mayer.free.fr/bateau/conversion_DMS_DMM_DD/Copie%20de%20calculators.htm
https://www.sunearthtools.com/fr/tools/distance.php
Trajet en latitude (partout pareil)
0.1     = 11113m
0.01    = 1111.3m
0.001   = 111.13m
0.0001  = 11.113m
0.00001 = 1.1113m
Trajet en longitude sous nos latitude (45°N)
45.0, 0.0 --> 45.0, 0.1     = 7886m
45.0, 0.0 --> 45.0, 0.01    = 788.6m
45.0, 0.0 --> 45.0, 0.001   = 78.86m
45.0, 0.0 --> 45.0, 0.0001  = 7.886m
45.0, 0.0 --> 45.0, 0.00001 = 0.7886m
"""
