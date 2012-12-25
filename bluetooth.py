#!/usr/bin/python
# -*- coding: utf-8 -*-

import types
import gobject
import subprocess
import dbus
from dbus.mainloop.glib import DBusGMainLoop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)



##
#	Class which will manage all the errors that this API will send
#	@date 23/11/2012
#	@version 1.0
#	@author ManuelDeveloper (manueldeveloper@gmail.com)
class BluetoothException(Exception):
	
	##
	#	Builder of the class whose objective is save the error message
	#	@param information Relative information about the error
	#	@date 11/10/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def __init__(self, information):
		self.information= information
	
	
	##
	#	Overload of the 'str' method which indicates the information to show when a class object is used by stdout
	#	@date 23/11/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def __str__(self):
		return repr(self.information)








##
#	API responsible of the bluetooth adapter management into UNIX systems based on BlueZ
#	@date		23/11/2012
#	@version	1.0
#	@author 	ManuelDeveloper (manueldeveloper@gmail.com)
class Bluetooth():
	
	""" Class attributes """
	
	# BlueZ system bus attributes
	_systemBus= None
	_manager= None
	
	# OpenOBEX session bus attributes
	_sessionBus= None
	_managerOBEX= None
	_savePath= '/home/manuel/'
	
	
	
	""" Class Builder """
	##
	#	Builder of the class whose objective is check if the system has a bluetooth adapter and then, gets the reference to it
	#
	#	@retval		Bluetooth Object class which lets interact with the bluetooth adapter
	#	@exception	BluetoothException
	#	@date 		23/11/2012
	#	@version 	1.0
	#	@author 	ManuelDeveloper (manueldeveloper@gmail.com)
	def __init__(self):
		
		# Get access to the system bus
		Bluetooth._systemBus= dbus.SystemBus()		
		
		# Get the reference to BlueZ in the system
		Bluetooth._manager= Bluetooth._systemBus.get_object('org.bluez', '/')
		interfaceManager= dbus.Interface(Bluetooth._manager, 'org.bluez.Manager')
		
		# Get the reference to the bluetooth adapter
		try:
			adapterReference= interfaceManager.DefaultAdapter()			
			self.adapter= dbus.Interface(Bluetooth._systemBus.get_object('org.bluez', adapterReference), 'org.bluez.Adapter')
			self.adapter.connect_to_signal('PropertyChanged', self.propertyListener)
			self.adapter.connect_to_signal('DeviceFound', self.deviceFound)
			Bluetooth._systemBus.add_signal_receiver(self.propertyListenerAD2P, dbus_interface= 'org.bluez.Audio', signal_name='PropertyChanged')
		except:
			raise BluetoothException("The system does not have an bluetooth connection")
			
		# Get the reference to the session bus
		Bluetooth._sessionBus= dbus.SessionBus()
		
		# Get the reference to the OpenOBEX
		Bluetooth._managerOBEX= Bluetooth._sessionBus.get_object('org.openobex', '/org/openobex')
		self.OBEX= dbus.Interface(Bluetooth._managerOBEX, 'org.openobex.Manager')
		self.OBEX.connect_to_signal('SessionConnected', self.establishedOBEX)
			
		# Initialize the internal flags
		self.isDiscovering= False
		self.isRegistering= False
		self.transferState= None
			
			
			
			
	""" General purpose methods """
	##
	#	Method which checks if the bluetooth adapter is On or Off
	#	@retval True if the adapter is ON
	#	@retval False if the adapter is OFF
	#	@date 27/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def getPower(self):
		
		# Return the bluetooth adapter status
		properties= self.adapter.GetProperties()
		if properties['Powered'] == 1:
			return True
		else:
			return False
			
	
	##
	#	Method which turns On/Off the bluetooth adapter
	#	@param power Indicates if we want to turn On(True) or Off(False) the bluetooth adapter
	#	@date 27/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def setPower(self, power):
		
		# Check the action
		if power is True:
			if self.getPower() is False:
				self.adapter.SetProperty('Powered', power) # Turn On
				self.propertyLoop= gobject.MainLoop()
				self.propertyLoop.run()	
				
		elif power is False:
			if self.getPower() is True:
				self.adapter.SetProperty('Powered', power) # Turn Off
				self.propertyLoop= gobject.MainLoop()
				self.propertyLoop.run()
	
	
	##
	#	Method which checks if the bluetooth visibility is On or Off
	#	@retval True if the bluetooth visibility is ON
	#	@retval False if the bluetooth visibility if OFF
	#	@exception	BluetoothException
	#	@date 27/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def getVisibility(self):
		
		# Check if the bluetooth adapter is ON
		if self.getPower() is True:
			
			# Return the bluetooth visibility status
			properties= self.adapter.GetProperties()
			if properties['Discoverable'] == 1:
				return True
			else:
				return False
				
		else:
			raise BluetoothException("The bluetooth adapter is turned off")
	
	
	##
	#	Method which turns On/Off the bluetooth visibility
	#	@param visible Indicates if we want to make the bluetooth adapter Visible(True) or Invisible(False)
	#	@exception	BluetoothException
	#	@date 27/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def setVisibility(self, visible):
		
		try:
			if (self.getVisibility() is False) and (visible is True): # Set visible
				self.adapter.SetProperty('Discoverable', visible)
				self.propertyLoop= gobject.MainLoop()
				self.propertyLoop.run()
				
			elif (self.getVisibility() is True) and (visible is False): # Set invisible
				self.adapter.SetProperty('Discoverable', visible)
				self.propertyLoop= gobject.MainLoop()
				self.propertyLoop.run()
				
		except BluetoothException as ex:
			raise ex
				
	
	##
	#	Method which returns the ASCII name of the bluetooth adapter
	#	@retval String with the name of the bluetooth adapter
	#	@date 27/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def getName(self):
		
		# Return the name
		properties= self.adapter.GetProperties()
		return properties['Name']
		
	
	##
	#	Method which sets the ASCII name of the bluetooth adapter
	#	@param name String with the name of the bluetooth adapter
	#	@exception BluetoothException
	#	@date 27/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def setName(self, name):

		# Check if the name is right
		if type(name) is types.StringType:
			# Sets the new name
			self.adapter.SetProperty('Name', name)
		
		else:
			raise BluetoothException("The name has an incorrect type (must be a string)")
			
			
	##
	#	Method which will receive all the signals that inform of the value change of the bluetooth adapter properties 
	#	@param name Name of the property changed
	#	@param value New value of the property
	#	@date 27/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)			
	def propertyListener(self, name, value):
		
		# Stop the loop needed to update the value of the property
		try:
			self.propertyLoop.quit()
		except:
			pass
		print name
		#if name != "Discovering":
		#	self.propertyLoop.quit()
		
	
	
	""" Search methods """
	##
	#	Method which starts up the search process
	#	@param timeOut Duration in seconds of the search process, by default, are 5s
	#	@retval List List object whose content are tuples with the information of all devices found (MAC, Name, Type, CoD)
	#	@retval None If the adapter has not found any device
	#	@exception BluetoothExecption
	#	@date 14/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def search(self, timeOut= 5):
		
		# Check if the timeOut is right
		if type(timeOut) is types.IntType:
		
			# Check if there is a search process right now
			if self.isDiscovering is False:
				
				# Set up the internal flags
				self.devices= []
				self.isDiscovering= True
				self.searchLoop= gobject.MainLoop()
				
				# Start up the search process
				self.adapter.StartDiscovery()
				gobject.timeout_add(timeOut * 1000, self.searchTimeOut)		
				self.searchLoop.run()
				
				# Return the the information
				if len(self.devices) is 0:
					return None
				else:
					return self.devices
			
			else:
				raise BluetoothException("Right now, there is a search process")
		else:
			raise BluetoothException("The timeOut has an incorrect type (must be an int)")
	
	
	##
	#	Method which will called when the timeout of search process is reached and stops the process
	#	@date 14/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def searchTimeOut(self):
		
		self.adapter.StopDiscovery()
		self.isDiscovering= False
		self.searchLoop.quit()
		return False
	
	
	##
	#	Method which will called when the bluetooth adapter find a new device and will save its information in a general list
	#	@param address Bluetooth MAC of the discovered device
	#	@param properties Dictionary with all the information about the discovered device
	#	@date 14/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def deviceFound(self, address, properties):
		
		# First, check if there is a search process running
		if self.isDiscovering is True:
			
			# Get the important information about the discovered device
			address= properties['Address']
			cod= properties['Class']
			
			if 'Name' in properties:
				name= properties['Name']
			else:
				name= None
				
			if 'Icon' in properties:
				icon= properties['Icon']
			else:
				icon= None
			
			# Add the information to the general list
			self.devices.append( (address, name, icon, cod) )
			
			
			
			
	""" AD2P methods """
	##
	#	Method which starts up the connection process of an AD2P device
	#	@param devicePath String with the BlueZ address of the device
	#	@retval True If the device is finally connected
	#	@retval False If the device is not connected
	#	@exception BluetoothExecption
	#	@date 21/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def connectAD2P(self, devicePath):
		
		# Check if the device is connected
		device= dbus.Interface( Bluetooth._systemBus.get_object('org.bluez', devicePath), 'org.bluez.Audio' )
		properties= device.GetProperties()
		
		if properties['State'] == "disconnected": # The device is disconnected		
			self.deviceConnected= False					
			self.propertyLoopAD2P= gobject.MainLoop()
					
			try:
				device.Connect() # Connect the device
				self.propertyLoopAD2P.run()
			except:
				raise BluetoothException("Error during the connection process")
				
		elif properties['State'] == "connected": # The device is connected			
			self.deviceConnected= True
			
		else:
			raise BluetoothException("The device is busy right now")
			
		# Return the result of the connection process	
		return self.deviceConnected
	
	
	##
	#	Method which will receive all the signals that inform of the state of the AD2P connection process
	#	@param name Name of the property changed
	#	@param value New value of the property
	#	@date 15/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def propertyListenerAD2P(self, name, value):

		# Check the state of the connection
		if name == 'State':
			
			# The device is correctly connected
			if value == "connected":
				self.deviceConnected= True
				self.propertyLoopAD2P.quit()
			
			# The device is not connected for some reason
			elif value == "disconnected":
				self.deviceConnected= False
				self.propertyLoopAD2P.quit()
			
			
			
	""" Input devices methods """
	##
	#	Method which starts up the connection process of an bluetooth input device
	#	@param devicePath String with the BlueZ address of the device
	#	@retval True If the device is finally connected
	#	@exception BluetoothExecption
	#	@date 21/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def connectInput(self, devicePath):
		
		# Check if the device is connected
		device= dbus.Interface( Bluetooth._systemBus.get_object('org.bluez', devicePath), 'org.bluez.Input' )
		properties= device.GetProperties()
		
		if properties['Connected'] == 0: # The device is disconnected
		
			try:
				device.Connect() # Connect the device
				self.deviceConnected= True
			except:
				raise BluetoothException("Error during the connection process")
		
		else: # The device is connected
			self.deviceConnected= True
		
		# Return the result of the connection process	
		return self.deviceConnected


			
	""" Connection methods """
	##
	#	Method which indicates if the given device is connected or not in the system
	#	@param address MAC bluetooth address of the device
	#	@retval True If the device is connected
	#	@retval False If the device is not connected
	#	@exception BluetoothException
	#	@date 21/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def isConnected(self, address):
		
		# Check if the device is already registered
		try:
			reference= self.adapter.FindDevice( address )
		except:
			raise BluetoothException("Unknown device")			
			
		# Get the status of the device
		device= dbus.Interface( Bluetooth._systemBus.get_object('org.bluez', reference), 'org.bluez.Device' )
		properties= device.GetProperties()
			
		# Return the information
		if properties['Connected'] is 1:
			return True
		else:
			return False
			

	##
	#	Method which disconnects the device indicated by its address
	#	@param address MAC bluetooth address of the device
	#	@retval True If the device is disconnected
	#	@retval False If the device is not disconnected
	#	@exception BluetoothException
	#	@date 21/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def disconnectDevice(self, address):
		
		# Check if the device is already registered
		try:
			reference= self.adapter.FindDevice( address )
		except:
			raise BluetoothException("Unknown device")
			
		# Get the reference to the device
		device= dbus.Interface( Bluetooth._systemBus.get_object('org.bluez', reference), 'org.bluez.Device' )
			
		# Disconnect the device
		try:
			device.Disconnect()
		except:
			pass
				
		return True

				
	##
	#	Method which starts up the register process of the bluetooth devices
	#	@param address MAC bluetooth address of the device
	#	@retval String with the reference of the device in the system
	#	@exception BluetoothException
	#	@date 21/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def register(self, address):
		
		# Check if the device is already registered
		try:
			reference= self.adapter.FindDevice( address )
		except:
			reference= None
			
		if reference == None:
			
			# Register the device in the system
			try:
				reference= self.adapter.CreateDevice( address )
			except:
				raise BluetoothException("Error during the registration process")
		
		# Return the result of the registration process
		return reference
		
	
	##
	#	Method which connects a bluetooth device with the system
	#	@param address MAC bluetooth address of the device
	#	@retval True If the device is finally connected
	#	@exception BluetoothException
	#	@date 21/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def connectDevice(self, address):
		
		# Check if the device is registered in the system
		try:
			reference= self.register( address )
		except BluetoothException as ex:
			raise ex
			
		# Get the Icon of the device and connect with it according to the gotten icon
		device= dbus.Interface( Bluetooth._systemBus.get_object('org.bluez', reference), 'org.bluez.Device' )
		properties= device.GetProperties()
			
		# Audio
		if properties['Icon'].find("audio") != -1:
			try:
				print "conectar audio"
				return self.connectAD2P( reference )					
			except BluetoothException as ex:					
				raise ex
			
		# Input
		elif properties['Icon'].find("input") != -1:
			try:
				self.connectInput( address )
			except BluetoothException as ex:
				raise ex
			
		# Error		
		else:
			raise BluetoothException("Incorrect device type to set a connection")


			
	""" File transfering methods """
	##
	#	Method which sends a file over OPP bluetooth protocol
	#	@param address MAC bluetooth address of the device that will receive the file
	#	@param pathFile Path of the file
	#	@pararm progressBar gtk.ProgressBar object used to indicate the progress of the sending process (by default, None)
	#	@retval True If the file is finally sended
	#	@exception BluetoothException
	#	@date 21/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def sendFile(self, address, pathFile, label= None, progressBar= None):
		
		# Check if there is other transfering process
		if self.transferState is None:
			
			# Indicate that there is one transfering in process
			self.transferState= 'send'
			
			# Create an internal reference for the file's path and progressBar
			self.pathFile= pathFile
			self.progressBar= progressBar
			
			# Create a session with the device
			try:
				self.pathSession= self.OBEX.CreateBluetoothSession(address, '00:00:00:00:00:00', 'opp')
			except:
				raise BluetoothException("The device don't accept this kind of connection")
				
			# Get the information about the connection
			self.OBEXSession= dbus.Interface(Bluetooth._sessionBus.get_object('org.openobex', self.pathSession) , 'org.openobex.Session')
			
			# Indicate the methods which will receive all the signals
			self.OBEXSession.connect_to_signal('TransferStarted', self.startOBEX)
			self.OBEXSession.connect_to_signal('TransferProgress', self.progressOBEX)
			self.OBEXSession.connect_to_signal('TransferCompleted', self.endOBEX)
			self.OBEXSession.connect_to_signal('ErrorOccurred', self.errorOBEX)
			self.OBEXSession.connect_to_signal('Cancelled', self.cancelOBEX)
			
			# Start the transfering process
			self.loopOBEX= gobject.MainLoop()
			self.loopOBEX.run()
			
			# Return the result of the transfering process
			if self.transferState == "sended":
				self.transferState= None
				return True
			
			elif self.transferState == "error":
				self.transferState= None
				raise BluetoothException("Error during the transfering process")
				
			elif self.transferState == "cancel": 
				self.transferState= None
				raise BluetoothException("The transfering process have been cancelled")
				
			elif self.transferState == "timeout":
				self.transferState = None
				raise BluetoothException("Request timeout")
		else:
			raise BluetoothException("There is another sending process in action")
			
	
	##
	#	Method which receives the signal when the OBEX connection will be established
	#	@param path D-Bus reference of the connection
	#	@date 21/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)		
	def establishedOBEX(self, path):
		
		# Check if the right session
		if path == self.pathSession:			
			self.OBEXSession.SendFile(self.pathFile)
			
	
	##
	#	Method which receives a file over OPP bluetooth protocol
	#	@pararm progressBar gtk.ProgressBar object used to indicate the progress of the sending process (by default, None)
	#	@retval True If the file is finally received
	#	@exception BluetoothException
	#	@date 23/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def receiveFile(self, progressBar= None):
		
		# Check if there is other transfering process
		if self.transferState is None:
		
			# Indicate that there is one transfering in process
			self.transferState= 'receive'
				
			# Create an internal reference for the progressBar
			self.progressBar= progressBar
			
			# Create a BluetoothServer
			servers= self.OBEX.GetServerList()
			
			self.serverInterface= dbus.Interface(Bluetooth._sessionBus.get_object('org.openobex', servers[0]), 'org.openobex.Server')
			self.serverInterface.connect_to_signal('SessionCreated', self.clientConnected)
			
			# Start the transfering process
			self.loopOBEX= gobject.MainLoop()
			self.loopOBEX.run()
				
			# Return the result of the transfering process
			if self.transferState == "received":
				self.transferState= None
				return True
				
			elif self.transferState == "error":
				self.transferState= None
				raise BluetoothException("Error during the transfering process")
					
			elif self.transferState == "cancel": 
				self.transferState= None
				raise BluetoothException("The transfering process have been cancelled")
					
			elif self.transferState == "timeout":
				self.transferState = None
				raise BluetoothException("Request timeout")	
		
	
	##
	#	Method which receives the signal that indicates that a client wants send us a file
	#	@pararm path D-Bus reference of the connection
	#	@date 23/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def clientConnected(self, path):
		
		# Get the reference to the created client session
		self.clientSession= dbus.Interface(Bluetooth._sessionBus.get_object('org.openobex', path), 'org.openobex.ServerSession')
		
		# Indicate the methods which will receive all the signals
		self.clientSession.connect_to_signal('TransferStarted', self.startOBEX)
		self.clientSession.connect_to_signal('TransferProgress', self.progressOBEX)
		self.clientSession.connect_to_signal('TransferCompleted', self.endOBEX)		
		self.clientSession.connect_to_signal('ErrorOccurred', self.errorOBEX)
		self.clientSession.connect_to_signal('Cancelled', self.cancelOBEX)	
			
	
	##
	#	Method which receives the signal when the transfer has begun
	#	@param filename Name of the file
	#	@param local_path Path of the file
	#	@param total_bytes Size of the file in bytes
	#	@date 21/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def startOBEX(self, filename, local_path, total_bytes):
		
		"""if self.transferState == 'receive':			
			# Accept the incoming file
			#self.clientSession.Accept()"""
		
		# Get the size of the transfered file
		self.sizeFile= total_bytes
	
	
	##
	#	Method which receives the signal when a bluetooth packet is transfered
	#	@param transfered Sent bytes
	#	@date 21/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def progressOBEX(self, transferred):
		
		# Update the UI indicating the progress of the transfering
		if self.progressBar is not None:
			self.progressBar.set_fraction(float(transferred)/float(self.sizeFile))
			if self.transferState == "send":
				self.progressBar.set_text("Enviando...")
			else:
				self.progressBar.set_text("Recibiendo...")
		
		print "progress: ", (float(transferred)/float(self.sizeFile)) * 100
	
	
	##
	#	Method which receives the signal when the transfer is ended
	#	@date 21/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)		
	def endOBEX(self):
		
		if self.transferState == 'send':
			# Set the result of the transfering
			self.transferState= "sended"
			
			# Close the connection
			try:
				self.OBEXSession.Close()
			except:
				pass
				
		else:
			# Set the result of the transfering
			self.transferState= "received"
			
			# Close the connection
			try:
				self.clientSession.Close()
			except:
				pass			
		
		self.loopOBEX.quit()
	
	
	##
	#	Method which receives the signal when an error appears during the transfering
	#	@param name_error Name of the error
	#	@param message_error Message of the error
	#	@date 21/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def errorOBEX(self, name_error, message_error):
		
		# Check the error
		if message_error == 'Request timeout':
			self.transferState= "timeout"
		else:
			self.transferState= "error"
			
		if self.transferState == 'send':
			
			# Close the connection
			try:
				self.OBEXSession.Close()
			except:
				pass
				
		else:
			
			# Close the connection
			try:
				self.clientSession.Close()
			except:
				pass
				
		self.loopOBEX.quit()
	
	
	##
	#	Method which receives the signal when the transfering is cancelled
	#	@date 21/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def cancelOBEX(self):
		
		self.transferState= "cancel"
		
		if self.transferState == 'send':
			
			# Close the connection
			try:
				self.OBEXSession.Close()
			except:
				pass
				
		else:
			
			# Close the connection
			try:
				self.clientSession.Close()
			except:
				pass
		
		self.loopOBEX.quit()		
