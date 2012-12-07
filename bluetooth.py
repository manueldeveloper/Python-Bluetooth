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
		
		# Obtenemos la referencia al adaptador de bluetooth del dispositivo
		try:
			adapterReference= interfaceManager.DefaultAdapter()			
			self.adapter= dbus.Interface(Bluetooth._systemBus.get_object('org.bluez', adapterReference), 'org.bluez.Adapter')
			self.adapter.connect_to_signal('PropertyChanged', self.propertyListener)
		except:
			raise BluetoothException("The system does not have an bluetooth connection")
			
			
			
			
	""" General purpose methods """
	##
	#	Method which checks if the bluetooth adapter is On or Off
	#	@retval True if the adapter is ON
	#	@retval False if the adapter if OFF
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
		self.propertyLoop.quit()
