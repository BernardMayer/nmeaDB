def DMd2Dd(dmd) :
    # DDDMM.d --> DDD.d (S or W negative values)
    # 10601.6986 ---> 106+1.6986/60 = 106.02831 degrees
    # "GLL": "4730.189,N,223.183,W"
    dotPos = dmd.find(".")
    D = float(dmd[0:dotPos - 2])
    M = float(dmd[dotPos - 2:]) / 60
    return (D + M)

print(str(DMd2Dd("10601.6986")), " 106.02831 degrees")
