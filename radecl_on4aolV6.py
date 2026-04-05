#!/usr/bin/env python

# See http://learn.astropy.org/rst-tutorials/Coordinates-Transform.html?highlight=filtertutorials
# For coordinate transform examples

# ON4AOL , aanpassing om dit script samen te voegen met het JPL script om de RA en DEC op te vragen.
# 5 sept 2022
# Dit programma is een samenraapsel van radecl( onderdeel van skytrack) van ghostop14 op Github 
# https://github.com/ghostop14/skytrack
# en JPLHorizon_OMOTENASHI.py , auteur onbekend 
# Input is nu op de commandoregel en er is niet met een parser gewerkt.
# Afspraken ;	classes met Hoofdletter beginnen en verder CamelCase
#				objecten , beginnen met kleine letter , dus camelCase
#				methodes , beginnen met kleine letter en verder ook camelCase
#				
#				attributen en variabelen , beginnen met kleine letter en eventueel 
#				samenstellen met underscore bv  mijn_variabele
#				return -1   foute aanroep  functie NIET uitgevoerd
#				return 0    aanroep OK , functie uitgevoerd 
# 

# 
# 11.09.2022: check op foutmeldingen komende van JPL , nu in een def
# 12.09.2022: V2 klasse schrijven voor ingave
# 14.09.2022: V3 , zoveel mogelijk in klassen steken
# 15.09.2022: Float conversies eruit genomen , werken enkel met strings voor ra en decl
# 			  V4 , nog meer klassen proberen
# 16.09.2022: V5 : RCmoveToPosition aangepast en heet nu MoveRotor
# 				 elevatielimieten opgesplitst in max en min
# 17.09.2022: V6 : Volledige herwerking volgens flowchart.
# 18.09.2022: Tussen elke " node " een groenlicht situatie , anders foutmelding en afsluiten
# 05.04.2026: Hernemen programma . Artemis II


# $$SOE    Start of ephemeris
# $$EOE    End of ephemeris

import sys
from astropy.coordinates import SkyCoord
from astropy.coordinates import EarthLocation
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import AltAz


import socket
import time
import re
import requests
import datetime
from datetime import timedelta, date,timezone 



# private ( volgens PEP008 ) ik bedoel hiermee constanten die eigenlijk in Pyhon niet bestaan
_lat = 51.2227
_long = 4.0227
_alt = 6
_urlJPL = "https://ssd.jpl.nasa.gov/api/horizons.api"



# -------------------  Global Vars -------------------------------------

lastElevation=-999.0

netPortRotor = None
rotorleftlimit = 90.0
rotorrightlimit=270.0
rotorelevationlimitMax= 50.0
rotorelevationlimitMin = 10.0
serverRotor= "192.168.2.73"
serverPort = 4533
serverAddress = serverRotor + ":" + str(serverPort)
azcorrect = float(0) # Init de azimuth correction ( voor True AZ ofwel kompas AZ ?)
groenlicht = False
foutnr = 0  # init

# -------------------  Global Functions ----------------------------------------

class SocketConnect(object):

	def __init__(self,server,port,netPortRotor):
	
		self.netPortRotor = netPortRotor
		self.server = server
		self.port = port
		
	def getRotorSocket(self):
		return self.netPortRotor
		
		
	def _createSocket(self):
		
		if not self.netPortRotor:
			self.netPortRotor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				self.netPortRotor.connect((self.server, self.port))
				
			except:
				print("ERROR: Unable to connect to " + self.server + ":" + str(self.port), file=sys.stderr)
				self.netPortRotor = None
			
	 

            



            
class MoveRotor(object):
	''' Commando uitgeven naar de rotor'''
	
	def __init__(self,azimuth,elevation,rotorsocket):
		
		
		self.azimuth = azimuth
		self.elevation = elevation
		self.rotorsocket = rotorsocket
		self.moveFout = 0
		
		
		
	def setMoveFout(self,flag):
		self.moveFout = flag
		
	def getMoveFout(self):
		return self.moveFout  
        
	
	def moveCommand (self):
		
		
		cmdString = "P " + str(self.azimuth) + " " + str(self.elevation) + "\n"
		self.rotorsocket.send(cmdString.encode('utf-8'))
		
		self.setMoveFout(0)
		





	
# -------------------  Classes ----------------------------------------	
	
class InputAfhandeling(object):
	''' Lees invoer vanuit de commandolijn en test op geldigheid'''
	def __init__(self):
		
		
		
		self.body = input("Geef target naam in :")
		print( "Uw keuze is :" ,self.body)
		self.date_start = datetime.date.today()
		print( "Startdatum  is :" ,self.date_start)
		self.date_stop = datetime.date.today()+timedelta(hours=24)
		print( "Stopdatum  is :" ,self.date_stop)
		try:
			self.waarde = input("Geef de rotorpacing in sec in  , default is 60 s: ")
			self.pacing = int(self.waarde)
			print ("Pacing is : ", str(self.pacing) + " sec" )
		except ValueError as e:
			print("Getal ingeven aub !")
			self.pacing = 60
			print ("Pacing is nu default : ", str(self.pacing) + " sec" )
			
	def getBody(self):
		return self.body
			
	def getDate_start(self):
		return self.date_start
		
	def getDate_stop(self):
		return self.date_stop
		
	def getPacing(self):
		return self.pacing
	
		
	
	


class CheckJPL(object):
	
	''' check of de aanvraag bij JPL geen fouten bevat '''
	
	def __init__(self,tabel,foutnr):
	
		self.foutnr = foutnr  
		self.tabel = tabel
		
	
	def findPattern(self):
		
		
		pattern = re.compile("Multiple major-bodies")
		fout=pattern.finditer(self.tabel.text)
		for match in fout:
			print("Multiple major-bodies , kies één enkel of gebruik ID# ")
			self.foutnr = 1
		
		
		pattern = re.compile("No matches found")
		fout=pattern.finditer(self.tabel.text)
		for match in fout:
			print("Geen overeenkomst gevonden ! Kijk syntax na of gebruik het ID# ")
			self.foutnr = 2
		
		pattern = re.compile("target disallowed")
		fout=pattern.finditer(self.tabel.text)
		for match in fout:
			print("Dit target (body) is niet toegelaten  , kies een andere !")
			self.foutnr = 3
		
		pattern = re.compile("ValueError")
		fout = pattern.finditer(self.tabel.text)
		for match in fout:
			print(" Onbekende naam voor target ( body ) , kijk syntax na  !")
			self.foutnr =  4
			
		
		pattern = re.compile("No ephemeris")
		fout = pattern.finditer(self.tabel.text)
		for match in fout:
			print("Geen efemeriden voor het target ( body )! Out of date ?")
			self.foutnr =  5
			
		pattern = re.compile("No such record")
		fout = pattern.finditer(self.tabel.text)
		for match in fout:
			print("Geen record gevonden ! , probeer positief nummer ?")
			self.foutnr =  6
			
		pattern = re.compile("API ERROR")
		fout = pattern.finditer(self.tabel.text)
		for match in fout:
			print("API error! Heeft U een geldig target( body) ingegeven ?")
			self.foutnr =  7
		
	def getFoutnr(self):
		
		return self.foutnr
		
		

class CheckRotorLimits(object):
	''' nakijken of er niet buiten de limieten zou worden gewerkt '''
	useRotor = True # Set up rotor if specified

	foutRotorLimit = 0
	usingRotorLimits = False
	rotorLimitsReversed = False
	
	
	
	def __init__(self, rotorleftlimit,rotorrightlimit):
	
		self.rotorleftlimit = rotorleftlimit
		self.rotorrightlimit = rotorrightlimit

	

	def getUsingRotorLimits(self):
		return self.usingRotorLimits
		
	def getRotorLimitsReversed(self):
		return self.rotorLimitsReversed
		
	def setError(self,flag):
		self.foutRotorLimit = flag
		
	def getError(self):
		return self.foutRotorLimit
		
	
		
	def checkLimits(self):
		
		if ((self.rotorleftlimit != -1 and self.rotorrightlimit == -1) or
				(self.rotorleftlimit == -1 and self.rotorrightlimit != -1)):
				print("ERROR: if one limit is provided, both left/right must be set.")
				setError ( -1)
				
		if float(self.rotorleftlimit) > 360.0 or ( float(self.rotorleftlimit) < 0.0 and self.rotorleftlimit != -1):
				print("ERROR: bad limit value.")
				setError ( -1)
				
		if float(self.rotorrightlimit) > 360.0 or ( float(self.rotorrightlimit) < 0.0 and self.rotorrightlimit != -1):
				print("ERROR: bad limit value.")
				setError ( -1)
				
				
		if self.rotorleftlimit != -1 and self.rotorrightlimit != -1:
				self.usingRotorLimits = True
				# Als er valabele waarden zijn ingegeven , dan zijn de limieten geldig
				# Depending on where your target is, left/right could span 0 degrees.  In that scenario,
				# the left limit will be greater than the right limit (e.g. 330 degrees left, 30 degrees right)
				if self.rotorleftlimit <= self.rotorrightlimit:
					self.rotorLimitsReversed = False
				else:
					self.rotorLimitsReversed = True
		else:
				# Er zijn geen limieten ingegeven , dus maak er geen gerbuik van !
				self.usingRotorLimits = False
				self.rotorLimitsReversed = False
				
				
class GetDataJPL(object):
	''' extract de data uit JPL'''
	def __init__(self,textdata,texttabel):
		
		self.textdata = textdata
		self.texttabel = texttabel
		
	def getRaDec(self):
		return [self.ra,self.decl]   # data in tuple
		
	def zoekData(self):
			
		pattern = re.compile(self.textdata) # Haal de recenste data op uit hedendaagse tijd
		efemeriden = pattern.finditer(self.texttabel.text) # zoek de data van de jongste tijd
		for match in efemeriden:# haal RA en DEC op mbv match.end()+offset , we noemen ze raw
			_RAraw= (self.texttabel.text[match.end()+4:match.end()+15])
			_DECraw = (self.texttabel.text[match.end()+16:match.end()+27])
		'''
		
		 converteer:
		 
		_RAraw  naar  '<#>h<#>m<#s>'  hour min sec
		 
		_DECraw naar  '<#>d<#>m<#s>'  degrees min sec
		
		'''	
		
		self.ra = _RAraw[0:2]+"h"+ _RAraw[3:5]+"m"+_RAraw[6:11]+"s"
		self.decl = _DECraw[0:3]+"d"+ _DECraw[4:6]+"m"+_DECraw[7:11]+"s"
		
		
		
class CalcAzEl(object):
	'''# Calculate Az / El mbv UTC tijd , grondlocatie en RA en DECL '''
	
	def __init__(self,obsTime,raDeclTarget,groundLoc):  # obsTime is observing time
		
		self.obsTime = obsTime
		self.raDeclTarget = raDeclTarget
		self.groundLoc = groundLoc
		self.azimuth = 0
		self.elevation =0
		
	
	
	def getAZEL(self):
		
		return ([self.azimuth,self.elevation]) # data in tuple
	
	def dataAZEL(self):
		
		
		altAzCoord = None  # Release any previous memory if looping  ????
		altAzCoord = AltAz(location= self.groundLoc,obstime=self.obsTime)
		
		print("Calculating...", file=sys.stderr)
		altAz=self.raDeclTarget.transform_to(altAzCoord)

		self.azimuth = altAz.az.degree
		self.elevation = altAz.alt.degree
			
		
		
class CheckBounderies (object):
	
	def __init__(self, azimuth,elevatie,rotorleftlimit,rotorrightlimit,rotorelevationlimitMax,rotorelevationlimitMin):
		
		self.azimuth = azimuth
		self.elevation = elevatie
		self.rotorleftlimit = rotorleftlimit
		self.rotorrightlimit = rotorrightlimit
		self.rotorelevationlimitMax = rotorelevationlimitMax
		self.rotorelevationlimitMin = rotorelevationlimitMin
		self.bounderyFout = 0 
		
	def setBounderyFout(self):
		self.bounderyFout = -1
		
	def getBounderyFout(self):
		return self.bounderyFout
		
		
	def bounderies(self):
	
		
		if self.azimuth < self.rotorleftlimit  or self.azimuth > self.rotorrightlimit:
			self.setBounderyFout() 

		if self.elevation < self.rotorelevationlimitMin:
			self.setBounderyFout()
			
		if  self.elevation > self.rotorelevationlimitMax:
			self.setBounderyFout()
			 




				
def main(args):
    return 0


   
# +++++++++++++++++++++++++++ MAIN +++++++++++++++++++++++++++++++++++++



if __name__ == '__main__':
	
#-------------------------- STAP 1 -------------------------------------
	
	
	''' parameters ophalen van de commandolijn '''
	ingave = InputAfhandeling()
	
	
	print("\n")
	print("*********************************************")
	print("\n")

#-------------------------- STAP 2 -------------------------------------


''' check of er rotorlimieten zijn ingegeven en of ze valabel zijn '''

# maak een instantie aan
checkrotorlimits = CheckRotorLimits(rotorleftlimit,rotorrightlimit)

# doe de check
checkrotorlimits.checkLimits()

print("Gebruik van limits is : " ,checkrotorlimits.getUsingRotorLimits())

print("De tegengestelde draairichting is " ,checkrotorlimits.getRotorLimitsReversed())

if (checkrotorlimits.getError() != 0):
	print ( "Check limieten zijn fout!")
else:
	print ( "Check limieten is OK!")

#--------------------------Groen Licht test ----------------------------

if (checkrotorlimits.getError() == 0):
	groenlicht = True

#-------------------------- STAP 3 -------------------------------------

''' De efemeriden ophalen bij JPL Horizons
    doc -->  : https://ssd-api.jpl.nasa.gov/doc/horizons.html
    
    GET  https://ssd.jpl.nasa.gov/api/horizons.api
    
    param = python dictionary
'''

if groenlicht == True:
	
	param = {     "format": "text"  # output in text (tabel)formaat , geen Json
			, "COMMAND": ingave.getBody()
			, "OBJ_DATA": "YES"
			, "MAKE_EPHEM": "YES"
			, "EPHEM_TYPE": "OBSERVER"
			, "CENTER": "COORD"   ##  gebruik onderstaande coördinaten
			, "COORD_TYPE":"GEODETIC"
			, "SITE_COORD": "'+4.02662,+51.22180,0'" ## opgelet dubbele quotes plus enkele quotes !!!!!
			, "START_TIME":ingave.getDate_start()
			,  "STOP_TIME":ingave.getDate_stop()
			,  "STEP_SIZE": "1m"   ## elke minuut
			, "QUANTITIES": "'1'"  ## enkel Astrometric RA&DEC
			,  "TIME_ZONE": "+00:00" ## relative to UTC
		}
		
	jpl_tabel  = requests.get(_urlJPL, params=param)


#-------------------------- STAP 4 -------------------------------------

''' checken of er geen foutmeldingen zijn komende van JPL '''

checkjpl = CheckJPL(jpl_tabel,foutnr)  # instantie aanmaken
 
checkjpl.findPattern()  # patroon nakijken  checkpatroon = 

foutchecked = checkjpl.getFoutnr()     # foutnummer ophalen , geen fout is 0



if foutchecked < 1 :   # doe verder 
	print("Ingave is OK  ")
	print("\n")
	print("********************************************* ")
	print("\n")
	#print(jpl_tabel.text)
	
	
#--------------------------Groen Licht test ----------------------------

if (checkrotorlimits.getError() == 0):
	groenlicht = True

#-------------------------- STAP 5 -------------------------------------
	''' Maak een socket aan , maak een verbinding met de rotor '''


if groenlicht ==  True:

	rotorSocket = SocketConnect(serverRotor,serverPort,netPortRotor)
	rotorSocket._createSocket()
	rotorTCP = rotorSocket.getRotorSocket()



	
#--------------------------Groen Licht test ----------------------------

	if rotorTCP == None:
		print("Onmogelijk om een socket te maken voor rotor")
		groenlicht = False
	else:
		groenlicht = True



# +++++++++++++++++++++++++++ Ingang Lus +++++++++++++++++++++++++++++++

''' Dit is het ingangspunt van de lus '''

if groenlicht ==  True:
	loop = True # First time through we want to execute
	

	while (loop):
		

	#-------------------------- STAP 6 -------------------------------------

		''' Haal data op met de recentste UTC tijd '''



		_date = datetime.datetime.utcnow() # haal UTC tijd op


		_date_text = _date.strftime("%Y""-""%b""-""%d" " " "%H" ":" "%M ") # datum als tekst bv 2022-Sep-08 12:00
		print( "Efemeriden zijn : ",_date_text + "UTC")


		jpldata = GetDataJPL(_date_text,jpl_tabel)
		jpldata.zoekData()
		ra_dec = jpldata.getRaDec()  # data in tuple


		print ("RA is : --> ", ra_dec[0])
		print ("DECL is : --> " ,ra_dec[1])

		print("\n")




		#-------------------------- STAP 7 -------------------------------------

		''' Bereken AZ en EL in functie van de UTC tijd en positie '''


		# Set up Earth observing Location
		_groundLoc = EarthLocation(lat=_lat, lon=_long, height=_alt)

		# Set up our target
		_raDeclTarget = SkyCoord(ra_dec[0], ra_dec[1], frame='icrs')

		# observingtime is UTC tijd

		obsTime = Time.now()

		# maak een instantie aan

		resultCalcAzEl = CalcAzEl(obsTime,_raDeclTarget,_groundLoc)

		# bereken AZ en EL

		resultCalcAzEl.dataAZEL()

		# haal resultaat op ( in tuple)
		calcAzEl = resultCalcAzEl.getAZEL()

		trueAz = calcAzEl[0] 


					
		if (azcorrect != 0.0):
			
			trueAz = trueAz + azcorrect

		if trueAz > 360.0:
			trueAz = trueAz - 360.0
			
		elif trueAz < 0.0:
			trueAz = trueAz + 360.0
				
		print('UTC Time: ' + str(obsTime))

		if (azcorrect == 0.0):
			print('Azimuth: ' + '%.4f' % calcAzEl[0]  + ' degrees')
		else:
			print('Azimuth (Calculated): ' + '%.4f' % calcAzEl[0]  + ' degrees')
			print('Azimuth (Corrected): ' + '%.4f' % trueAz + ' degrees')
				
		print('Elevation: ' + '%.4f' % calcAzEl[1]  + ' degrees')




		#-------------------------- STAP 8 -------------------------------------

		''' Kijk of AZ en EL niet buiten het bereik vallen '''


		checkbounderies = CheckBounderies (trueAz,calcAzEl[1],rotorleftlimit,rotorrightlimit,rotorelevationlimitMax,rotorelevationlimitMin)

		checkbounderies.bounderies()

		print("\n")
		print("**************************************************")
		if checkbounderies.getBounderyFout() == -1:
			print("Object is buiten bereik van de schotel ! " + "\n")
			print("**************************************************")
			print("\n")
			
			executeMove = False
			groenlicht = False
			
		else:executeMove = True  # Toelating tot draaien met rotor
			





		#-------------------------- STAP 9 -------------------------------------
		''' Na alle contoles ,stuur de waarden door naar de rotor '''

		 
		delay= ingave.getPacing()  # Pacingtijd tussen twee bewegingen ophalen
		
		

		try:
			
							
				rotor = MoveRotor ( trueAz, calcAzEl[1],rotorTCP)  # init positioner
				
				if executeMove: # Uiteindelijk  kunnen we de rotor laten draaien.
					
					rotor.moveCommand()
					retVal = rotor.getMoveFout()
				else:
					print("**************************************************")
					print("Er wordt geen commando naar de rotor opgestuurd ! " + "\n")
					print("**************************************************")
					print("\n")
					
						
								
				# Determine if we should loop and if so, delay
					
				if (delay > 0):  
					loop = True
					time.sleep(delay)
				else:
					loop = False
						
		except KeyboardInterrupt:
			loop = False
			groenlicht = False
			pass
	# +++++++++++++++++++++++++++ Einde  Lus +++++++++++++++++++++++++++++++

if groenlicht == False:
	print( "Door fout wordt het programma afgesloten ")
	print("\n")
	#print(jpl_tabel.text)
	pass
		

