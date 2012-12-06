#!/usr/bin/python
# -*- coding: utf-8 -*-

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
		self.informacion= information
	
	
	##
	#	Overload of the 'str' method which indicates the information to show when a class object is used by stdout
	#	@date 23/11/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def __str__(self):
		return repr(self.informacion)








##
#	API responsible of the bluetooth adapter management into UNIX systems based on BlueZ
#	@date		23/11/2012
#	@version	1.0
#	@author 	ManuelDeveloper (manueldeveloper@gmail.com)
class Bluetooth():
	
	"""									Class attributes									"""
	
	# BlueZ system bus attributes
	_systemBus= 			None
	_manager= 				None
	
	
	
	
	"""									Class Builder									"""
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
		except:
			raise BluetoothException("The system does not have an bluetooth connection")
			
			
			
			
	"""									General purpose methods									"""
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
