# -*- coding: utf-8 -*-
#########################################################
# SERVICE : timecalc                                    #
#           Calculate sunrise/sunset and some other     #
#                timer related things for home control  #
#           I. Helwegen 2017                            #
#########################################################

#SUNRISET.C - computes Sun rise/set times, start/end of twilight, and
#             the length of the day at any date and latitude

#Written as DAYLEN.C, 1989-08-16

#Modified to SUNRISET.C, 1992-12-01

#(c) Paul Schlyter, 1989, 1992

#Released to the public domain by Paul Schlyter, December 1992


####################### IMPORTS #########################
import math


#########################################################

####################### GLOBALS #########################

#########################################################
# Class : timecalc                                      #
#########################################################


class timecalc(object):
    def __init__(self):
        pass

    def __del__(self):
        pass

    def SetTimeMOD(self, hour, minute):
        return (hour*60+minute)

    def GetTimeMOD(self, time):
        return (time/60,time%60)

    def SunRiseSet(self, y, m, d, lon, lat, zone):
        ret,drise,dset=self.__sunriset(y, m, d, lon, lat, -35.0/60.0, 1)
        if (ret == 0):
           srise=self._showMOD(drise, zone)
           sset=self._showMOD(dset, zone)
        else:
           srise = 30*60 #never
           sset = 30*60 #never

        return srise,sset


    #***************************************************************************/
    #* Note: year,month,date = calendar date, 1801-2099 only.             */
    #*       Eastern longitude positive, Western longitude negative       */
    #*       Northern latitude positive, Southern latitude negative       */
    #*       The longitude value IS critical in this function!            */
    #*       alt = the altitude which the Sun should cross                */
    #*               Set to -35/60 degrees for rise/set, -6 degrees       */
    #*               for civil, -12 degrees for nautical and -18          */
    #*               degrees for astronomical twilight.                   */
    #*         upper_limb: non-zero -> upper limb, zero -> center         */
    #*               Set to non-zero (e.g. 1) when computing rise/set     */
    #*               times, and to zero when computing start/end of       */
    #*               twilight.                                            */
    #* Return value:  0 = sun rises/sets this day, times stored at        */
    #*                    *trise and *tset.                               */
    #*               +1 = sun above the specified "horizon" 24 hours.     */
    #*                    *trise set to time when the sun is at south,    */
    #*                    minus 12 hours while *tset is set to the south  */
    #*                    time plus 12 hours. "Day" length = 24 hours     */
    #*               -1 = sun is below the specified "horizon" 24 hours   */
    #*                    "Day" length = 0 hours, *trise and *tset are    */
    #*                    both set to the time when the sun is at south.  */
    #*         rise = where to store the rise time                        */
    #*         set  = where to store the set  time                        */
    #*                Both times are relative to the specified altitude,  */
    #*                and thus this function can be used to compute       */
    #*                various twilight times, as well as rise/set times   */
    #*                                                                    */
    #**********************************************************************/
    def __sunriset(self, year, month, day, lon, lat, alt, upper_limb):
        rc = 0 # Return cde from function - usually 0

        # Compute d of 12h local mean solar time
        d = self._DaysSince2000Jan0(year,month,day) + 0.5 - lon/360.0

        # Compute local sidereal time of this moment
        sidtime = self._revolution( self._GMST0(d) + 180.0 + lon )

        # Compute Sun's RA + Decl at this moment
        sRA, sdec, sr = self._sun_RA_dec(d)

        # Compute time when Sun is at south - in hours UT
        tsouth = 12.0 - self._rev180(sidtime - sRA)/15.0

        # Compute the Sun's apparent radius, degrees
        sradius = 0.2666/sr

        #Do correction to upper limb, if necessary
        if (upper_limb):
            alt -= sradius

        # Compute the diurnal arc that the Sun traverses to reach
        # the specified altitude altit:
        cost = (math.sin(math.radians(alt)) - math.sin(math.radians(lat)) * math.sin(math.radians(sdec))) / (math.cos(math.radians(lat)) * math.cos(math.radians(sdec)) )
        if (cost >= 1.0): # Sun always below altit
            rc = -1
            t = 0.0
        elif (cost <= -1.0): # Sun always above altit
            rc = +1
            t = 12.0
        else: # The diurnal arc, hours
            t = math.degrees(math.acos(cost))/15.0
      
        # Store rise and set times - in hours UT
        trise = tsouth - t
        tset  = tsouth + t

        return rc, trise, tset

    # A macro to compute the number of days elapsed since 2000 Jan 0.0 
    # (which is equal to 1999 Dec 31, 0h UT)                           
    def _DaysSince2000Jan0(self, y, m, d):
        return (367L*(y)-((7*((y)+(((m)+9)/12)))/4)+((275*(m))/9)+(d)-730530L)


    #*****************************************/
    #* Reduce angle to within 0..360 degrees */
    #*****************************************/
    def _revolution(self, x):
        return (x - 360.0*math.floor(x*(1.0/360.0)))

    #*********************************************/
    #* Reduce angle to within +180..+180 degrees */
    #*********************************************/
    def _rev180(self, x):
        return (x - 360.0*math.floor(x*(1.0/360.0)+0.5))


    #*******************************************************************/
    #* This function computes GMST0, the Greenwich Mean Sidereal Time  */
    #* at 0h UT (i.e. the sidereal time at the Greenwhich meridian at  */
    #* 0h UT).  GMST is then the sidereal time at Greenwich at any     */
    #* time of the day.  I've generalized GMST0 as well, and define it */
    #* as:  GMST0 = GMST - UT  --  this allows GMST0 to be computed at */
    #* other times than 0h UT as well.  While this sounds somewhat     */
    #* contradictory, it is very practical:  instead of computing      */
    #* GMST like:                                                      */
    #*                                                                 */
    #*  GMST = (GMST0) + UT * (366.2422/365.2422)                      */
    #*                                                                 */
    #* where (GMST0) is the GMST last time UT was 0 hours, one simply  */
    #* computes:                                                       */
    #*                                                                 */
    #*  GMST = GMST0 + UT                                              */
    #*                                                                 */
    #* where GMST0 is the GMST "at 0h UT" but at the current moment!   */
    #* Defined in this way, GMST0 will increase with about 4 min a     */
    #* day.  It also happens that GMST0 (in degrees, 1 hr = 15 degr)   */
    #* is equal to the Sun's mean longitude plus/minus 180 degrees!    */
    #* (if we neglect aberration, which amounts to 20 seconds of arc   */
    #* or 1.33 seconds of time)                                        */
    #*                                                                 */
    #*******************************************************************/
    def _GMST0(self, d):
        #* Sidtime at 0h UT = L (Sun's mean longitude) + 180.0 degr  */
        #* L = M + w, as defined in sunpos().  Since I'm too lazy to */
        #* add these numbers, I'll let the C compiler do it for me.  */
        #* Any decent C compiler will add the constants at compile   */
        #* time, imposing no runtime or code overhead.               */
        return self._revolution((180.0 + 356.0470 + 282.9404) + (0.9856002585 + 4.70935E-5)*d)


    #******************************************************/
    #* Computes the Sun's ecliptic longitude and distance */
    #* at an instant given in d, number of days since     */
    #* 2000 Jan 0.0.  The Sun's ecliptic latitude is not  */
    #* computed, since it's always very near 0.           */
    #******************************************************/
    def _sunpos(self, d):
        # Compute mean elements
        # Mean anomaly of the Sun
        M = self._revolution(356.0470 + 0.9856002585*d) 
        # Mean longitude of perihelion, Note: Sun's mean longitude = M + w
        w = 282.9404 + 4.70935E-5*d
        # Eccentricity of Earth's orbit
        e = 0.016709 - 1.151E-9*d 

        # Compute true longitude and radius vector
        # Eccentric anomaly
        E = M + math.degrees(e)*math.sin(math.radians(M)) * (1.0 + e*math.cos(math.radians(M)))
        # x, y coordinates in orbit
        x = math.cos(math.radians(E)) - e
        y = math.sqrt(1.0 - e*e) * math.sin(math.radians(E))  
        # Solar distance
        r = math.hypot(x, y)
        # True anomaly
        v = math.degrees(math.atan2(y, x))
        # True solar longitude
        lon = self._revolution(v + w)

        return lon, r

    def _sun_RA_dec(self, d):
        # Compute Sun's ecliptical coordinates
        lon,r = self._sunpos(d)

        # Compute ecliptic rectangular coordinates (z=0)
        x = r*math.cos(math.radians(lon))
        y = r*math.sin(math.radians(lon))

        # Compute obliquity of ecliptic (inclination of Earth's axis)
        obl_ecl = 23.4393 - 3.563E-7*d

        # Convert to equatorial rectangular coordinates - x is unchanged
        z = y*math.sin(math.radians(obl_ecl))
        y = y*math.cos(math.radians(obl_ecl))

        # Convert to spherical coordinates
        RA = math.degrees(math.atan2(y, x))
        dec = math.degrees(math.atan2(z, math.hypot(x, y)))

        return RA, dec, r


    def _showhrm(self, dhr, zone):
        hr = int(dhr) + zone
        mn = int(((dhr + zone) - hr)*60)
        hr %= 24
        return hr,mn

    def _showMOD(self, dhr, zone):
        hr,mn = self._showhrm(dhr, zone)
        return self.SetTimeMOD(hr, mn)





