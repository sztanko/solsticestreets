'''
Created on 15 Dec 2013

@author: demetersztanko
'''

from math import sin, cos, sqrt, atan2, radians, degrees
import ephem
# Radius of the earth    

R = 6373000.0
winterSolsticeDate = ephem.next_solstice('2014')
stats= {'totalLength': 0.0, 'solsticeLength': 0.0, 'hist': []}
stats['hist'] = [0.0 for i in range(0, 181)]

dates = {
'winterSolstice': ephem.previous_solstice('2014'),
'summerSolstice': ephem.next_solstice('2014')
}

azimuthCache = dict()

def getLength(segment):
    
    lat1 = radians(segment[0][1])
    lon1 = radians(segment[0][0])
    lat2 = radians(segment[1][1])
    lon2 = radians(segment[1][0])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat / 2)) ** 2 + cos(lat1) * cos(lat2) * (sin(dlon / 2)) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def lengthFilter(segment, length=10):
    return getLength(segment) > length

def azimuthFilter(segment, threshold=1.5):
    seg_az = getSegmentAzimuth(segment)
    sun_az = getSunAzimuthCached(segment[0])
    sun_az2 = 360.0 - sun_az
    length = getLength(segment)
    stats['hist'][int(seg_az)] += length
    stats['totalLength'] += length
    if abs(sun_az - seg_az) < threshold:
        stats['solsticeLength'] += length
        return True
    return False

#def getTotalLength(ss):
#    l = 0.0
#    for i in range(0, len(ss) - 1):
#        l += getLength((ss[i], ss[i + 1]))
#    return l

def combinedFilter(segment):
    
    return azimuthFilter(segment)

def sortSegment(s):
    if s[0][0] > s[1][0]:
        return (s[1], s[0])
    else:
        return s

def getSegmentAzimuth(s):
    p = (s[0][0], s[1][1])
    
    dy = getLength((s[0], p))
    dx = getLength((p, s[1]))
    if s[0][0] > s[1][0]:
        dx = -dx
    if s[0][1] > s[1][1]:
        dy = -dy
    az = degrees(atan2(dy, dx))
    if az < 0:
        az = az + 180
#     print "dx is %d, dy is %d, azimuth is %d" %(dx, dy, az)
    #     coordinates should be in the right q
#     if s[0][0]>s[1][0]:
#         az = 90.0-az
    az = (-az + 270) % 360
    if az > 180:
        az = az - 180

    return az

def getAzimuth(d, lnglat):
    o = ephem.Observer()
    o.lat = str(lnglat[1])
    o.lon = str(lnglat[0])
    o.date = d
    s = ephem.Sun()
    nextRiseDate = o.next_rising(s)
    o.date = nextRiseDate
    s.compute(o)
    risingAz = degrees(s.az)
    o = ephem.Observer()
    o.lat = str(lnglat[1])
    o.lon = str(lnglat[0])
    o.date = d
    s = ephem.Sun()
    prevSetDate = o.previous_setting(s)
    o.date = prevSetDate
    s.compute(o)
    settingAz = degrees(s.az)
    return risingAz, settingAz

def getSunAzimuthCached(lnglat):
    key="%.2f:%.2f" %(lnglat[0], lnglat[1])
    if key in azimuthCache:
       return azimuthCache[key]
    azimuthCache[key] = getSunAzimuth(lnglat)
    return azimuthCache[key]


def getSunAzimuth(lnglat):
    o = ephem.Observer()
    o.lat = str(lnglat[1])
    o.lon = str(lnglat[0])
    o.date = winterSolsticeDate
    s = ephem.Sun()
    # s.compute(o)
#     o = ephem.Observer()
#     o.lat = str(lnglat[1])
#     o.lon = str(lnglat[0])
    nextRiseDate = o.next_rising(s)
    o.date = nextRiseDate
    s.compute(o)
#     print o
    az = degrees(s.az)
    if az > 180:
        az = az - 180
    # az = (az + 270.0 ) %360
    return az
    
if __name__ == '__main__':
    segment = ((-0.1183418, 51.5815097), (-0.1190998, 51.5823349))  # Ferme park road, 60
#     segment = ((-0.1002803, 51.5490342), (-0.0999796, 51.5490038)) # near Highbury & islington, 8
#     segment = ((-0.1247137, 51.5833561), (-0.1248252, 51.5822201)) # crouch end Topsfield road, 86
#     segment = sortSegment(segment)
    print segment
    print "%f, %f" % (segment[0][1], segment[0][0])
    print "%f, %f" % (segment[1][1], segment[1][0])
    print getLength(segment)
    print getSegmentAzimuth(segment)
#     print getSunAzimuth(segment[0])
