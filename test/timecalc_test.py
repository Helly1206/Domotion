import sys
sys.path.insert(0,"..")

from utilities import timecalc

tc = timecalc()
lon = 5.9825
lat = 51.19722222
zone = 1 # +UTC
trise,tset = tc.SunRiseSet(2017, 1, 22, lon, lat, zone)

h,m = tc.GetTimeMOD(trise)
print "SunRise= "+str(h)+":"+str(m)
h,m = tc.GetTimeMOD(tset)
print "SunSet= "+str(h)+":"+str(m)

del tc