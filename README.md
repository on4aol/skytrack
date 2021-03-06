# SkyTrack

## Overview
SkyTrack is a set of Python-based comand-line tools that helps track solar system and other celestial body positions (Azimuth / Elevation) in relation to the specified latitude and longitude.  This information can be used to do basic target-rise/set calculations, or taken to feed a radio and rotor system for radio reception or observation.  Think of it as tools such as gpredict or Orbitron taken from earth-based satellites out to solar system and other celestial bodies such as the Moon, Mars, and Jupiter's moons.  

Skytrack contains two command-line tools: one called skytrack.py and one called radecl.py.  skytrack.py is used to track solar system objects and radecl.py can be used given any Right Ascention and Declinination coordinates to calculate Az/El.

### Skytrack
Skytrack can be connected to GQRX, SDRSharp, the GNURadio OOT gr-gpredict-doppler fork in my github repositories, and/or any Hamlib rotctld-compatible rotor system.  It can provide both frequency doppler shifted radio control and azimuth/elevation control to point observing systems at any solar system body in the Skyfield python library database (https://rhodesmill.org/skyfield/).

Observer coordinates define your place on Earth from which Azimuth and Elevation are determined.  Moreover, the tool can automatically control a radio receiver (gqrx-compatible or SDRSharp) to set a given receiver frequency with doppler shift due to the body's motion relative to Earth.  It can also control rotors (based on rotctl/hamlib protocol) setting appropriate azimuth and elevation.  SkyTrack can be run natively on both Linux and Windows (With Python and skyfield installed - see windows setup below).  However since receiver and rotor control is TCP-based, SkyTrack can be run on different system types.  For instance, the gr-gpredict-doppler modules can be run in GNURadio on Linux, and the skytrack script run on WIndows if need be.

The following help shows its usage:
```
usage: skytrack.py [-h] [--body BODY] [--lat LAT] [--long LONG] [--listbodies]
                   [--freq FREQ] [--radio RADIO] [--sdrsharp SDRSHARP]
                   [--delay DELAY] [--rotor ROTOR] [--rotortype ROTORTYPE]
                   [--rotorbaud ROTORBAUD] [--rotorleftlimit ROTORLEFTLIMIT]
                   [--rotorrightlimit ROTORRIGHTLIMIT]
                   [--rotorelevationlimit ROTORELEVATIONLIMIT]
                   [--utcdate UTCDATE]

Solar System Planet/Moon Tracker

optional arguments:
  -h, --help            show this help message and exit
  --body BODY           [Required] Planet/Moon from the skyfield library to
                        track. Use --listbodies to see options.
  --lat LAT             [Required] Observer Latitude
  --long LONG           [Required] Observer Longitude
  --listbodies          List options for the --body parameter
  --freq FREQ           If provided, a doppler shift will be calculated
  --radio RADIO         If provided, gqrx/gpredict-compatible frequency
                        control commands will be sent to the specified
                        host:port (Note: This disables any value in the --date
                        parameter and the --freq parameter is required and
                        causes the program to continue to loop)
  --send-aos-los        Send AOS/LOS messages to radio above the specified
                        elevation (Default is not to send)
  --aos-elevation AOS_ELEVATION
                        Set the AOS/LOS elevation boundary in degrees (Default
                        is 10 degrees)
  --sdrsharp SDRSHARP   If provided, frequency control commands will be sent
                        the NetRemote plugin for SDRSharp on the specified
                        host:port (Note: This disables any value in the --date
                        parameter and the --freq parameter is required and
                        causes the program to continue to loop)
  --delay DELAY         Time in seconds between radio and rotor updates
                        (default=30 seconds)
  --rotor ROTOR         HamLib compatible rotor control (matches gpredict
                        rotor/rotctl). Can be <ip>:<port> or device like
                        /dev/ttyUSB0
  --rotortype ROTORTYPE
                        rotctl rotor type (use rotctl -l to show numbers).
                        Default is 2 (hamlib/net), Celestron is 1401, SPID is
                        901 or 902 depending on mode.
  --rotorbaud ROTORBAUD
                        If needed, can provide a rotor baud. Default is 9600
  --rotorleftlimit ROTORLEFTLIMIT
                        If needed, can provide a rotor 'left' limit in
                        degrees. For instance if obstructions block rotation
                        or view. Default is no restriction. Note: if either
                        left/right limit is noted, both are required.
  --rotorrightlimit ROTORRIGHTLIMIT
                        If needed, can provide a rotor 'right' limit in
                        degrees. For instance if obstructions block rotation
                        or view. Default is no restriction. Note: if either
                        left/right limit is noted, both are required.
  --rotorelevationlimit ROTORELEVATIONLIMIT
                        If needed, can provide a rotor 'elevation' limit in
                        degrees. For instance if obstructions block rotation
                        or view. Default is 90 degrees (straight up).
  --utcdate UTCDATE     [Alternate date] If provided, the UTC date and time
                        will be used for the rise/set calculation rather than
                        the current date/time. Format: year/month/day hh:mm:ss
```

### radecl
radecl.py is designed such that knowing any RA/DEC target and the local observing location (lat, long, and altitude), local azimuth and elevation parameters can be calculated using either current time or a specified UTC time.  radecl has the ability to talk to rotctld-compatible rotor systems to automatically point systems at the specified target.  It also suppports an azcorrect parameter if adjustments to output azimuth values need to be made, such as accounting for true versus magnetic north.  The following shows the supported parameters for radecl.py:

The following help shows its usage:
```
usage: radecl.py [-h] --ra RA --dec DEC --lat LAT --long LONG --altitude
                 ALTITUDE [--azcorrect AZCORRECT] [--rotor ROTOR]
                 [--delay DELAY] [--rotorleftlimit ROTORLEFTLIMIT]
                 [--rotorrightlimit ROTORRIGHTLIMIT]
                 [--rotorelevationlimit ROTORELEVATIONLIMIT]
                 [--utcdate UTCDATE]

RA/DEC to Az/El Converter with Rotor Control (via rotctld)

optional arguments:
  -h, --help            show this help message and exit
  --ra RA               Target Right Ascention (can just be degrees '9.81625'
                        or can be '<#>h<#>m<#s>')
  --dec DEC             Target Declination (can just be degrees '10.88806' or
                        can be '<#>d<#>m<#s>'
  --lat LAT             Observer Latitude (decimal notation. Example: 40.1234)
  --long LONG           Observer Longitude (decimal notation)
  --altitude ALTITUDE   Observer Altitude (in meters)
  --azcorrect AZCORRECT
                        Degrees to adjust calculated azimuth. For example,
                        useful if accounting for magnetic vs. true north.
  --rotor ROTOR         Rotctld-compatible network rotor controller. Specify
                        as <ip>:<port>
  --delay DELAY         Time in seconds between updates (default is single
                        shot)
  --rotorleftlimit ROTORLEFTLIMIT
                        If needed, can provide a rotor 'left' limit in
                        degrees. For instance if obstructions block rotation
                        or view. Default is no restriction. Note: if either
                        left/right limit is noted, both are required.
  --rotorrightlimit ROTORRIGHTLIMIT
                        If needed, can provide a rotor 'right' limit in
                        degrees. For instance if obstructions block rotation
                        or view. Default is no restriction. Note: if either
                        left/right limit is noted, both are required.
  --rotorelevationlimit ROTORELEVATIONLIMIT
                        If needed, can provide a rotor 'elevation' limit in
                        degrees. For instance if obstructions block rotation
                        or view. Default is 90 degrees (straight up).
  --utcdate UTCDATE     [Alternate date] If provided, the UTC date and time
                        will be used for the calculation rather than the
                        current date/time. Format: year/month/day hh:mm:ss
```


## Examples

### Skytrack
Running with a radio for the moon and notify the receiver with acquisition of signal (AOS) / loss of signal (LOS) above/below 12 degrees:

``./skytrack.py --body=moon --lat=<mylat> --long=<mylong> --freq=144000000 --radio=127.0.0.1:7356 --send-aos-los --aos-elevation=12``


Running with a radio and rotor for Mars:

``./skytrack.py --body=mars --lat=<mylat> --long=<mylong> --freq=144000000 --radio=127.0.0.1:7356 --rotor=localhost:4533``

### radecl
Pointing at Cassiopeia A:

``./radecl.py --lat=<mylat> --long=<mylong> --altitude=<my alt in meters> --ra=23h23m24s --dec=58d48.9m``

Running with rotor control:

``./radecl.py --lat=<mylat> --long=<mylong> --altitude=<my alt in meters> --ra=23h23m24s --dec=58d48.9m --delay=10 --rotor=127.0.0.1:4533``

## Installation

### Linux Prerequisites
pip3 install skyfield astropy tzlocal python-dateutil

For rotor control you will also need to either install hamlib from source (https://sourceforge.net/projects/hamlib/files/hamlib/3.3/) or use the repo version, which will undoubtedly be a bit older and have fewer rotor choices:
sudo apt-get install hamlib-utils python-libhamlib2


### Windows Setup
You can run skytrack.py natively on Windows.  If you would like rotor control, go to https://sourceforge.net/projects/hamlib/files/hamlib/3.3/ and download the windows zip version.  Download it somewhere and unzip it, then add the bin directory to your path.

On Windows, you will need to install Python 3 (latest at this time is 3.7).  Install python and instruct the installer to add python to the environment paths.  Then the pip3 command should succeed:
pip3 install skyfield tzlocal python-dateutil

## Receiver Integration

### Integrating with GQRX
Pretty straightforward, just turn on the TCP listener in the UI.  NOTE: It only listens on the local loopback by default so if you're using it across a network you'll need to change the listening IP to something more network-friendly (like 0.0.0.0 for all IP's).

### Integrating with GNURadio
The gr-gpredict-doppler fork in my repos here https://github.com/ghostop14/gr-gpredict-doppler.git have new and updated blocks that support receiving both frequencies and azimuth/elevation rotor control values from skytrack.  Just drop the appropriate doppler or rotor block in your GNURadio flowgraph, specify the listening port, then use those same parameters (for instance localhost:7356) for the appropriate skytrack parameter (radio or rotor).

### Integrating with SDRSharp:
This uses the SDRSharp plugin located here:
https://github.com/EarToEarOak/SDRSharp-Net-Remote

If you can't compile it, there's a precompiled version in the sdrsharp subdirectory.  Copy the DLL into your SDRSharp installation directory then add the following magic line to your Plugins.xml file:
  <add key="NetRemote" value="SDRSharp.NetRemote.NetRemotePlugin,SDRSharp.NetRemote" />

