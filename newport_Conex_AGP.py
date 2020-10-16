# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 12:35:41 2020

@author: EEMCS
Initial code taken from Newport Conex documentation https://www.newport.com/mam/celum/celum_assets/resources/CONEX-AGP_-_Command_Interface_Manual.pdf?1


"""
#============================================================
#Initialization Start
#The script within Initialization Start and Initialization End is needed for properly
#initializing IOPortClientLib and Command Interface for CONEX-AGP instrument.
#The user should copy this code as is and specify correct paths here.
import sys
#IOPortClientLib and Command Interface DLL can be found here.
print("Adding location of IOPortClientLib.dll & Newport.CONEXAGP.CommandInterface.dll to sys.path")
sys.path.append(r'C:\Program Files\Newport\Piezo Motion Control\Newport CONEX-AGP Applet\Bin')
# The CLR module provide functions for interacting with the underlying
# .NET runtime
import clr
# Add reference to assembly and import names from namespace
clr.AddReferenceToFile("Newport.CONEXAGP.CommandInterface.dll")
from CommandInterface import *
import System
#============================================================
# Instrument Initialization
# The key should have double slashes since
# (one of them is escape character)
instrumentKey ="CONEX-AGP (A6TLBK3L)"
print('Instrument Key=>', instrumentKey)
# create a device instance
AGP = ConexAGP()
#componentID needs to be used in all commands
componentID = AGP.RegisterComponent(instrumentKey);
print('componentID=>', componentID)

# Get positive software limit
result, response, errString = AGP.SR_Get(componentID,1)
if result == 0 :
    print( 'positive software limit=>', response)
else:
    print( 'Error=>',errString)
# Get negative software limit
result, response, errString = AGP.SL_Get(componentID,1)
if result == 0 :
    print( 'negative software limit=>', response)
else:
    print( 'Error=>',errString)
# Get HOME search type Using HT Command
result, response, errString = AGP.HT_Get(componentID,1)
if result == 0 :
        print('HOME search type=>', response)
else:
    print('Error=>',errString)
# Get controller revision information
result, response, errString = AGP.VE(componentID,1)
if result == 0 :
    print('controller revision=>', response)
else:
    print( 'Error=>',errString)
# Get current position
result, response, errString = AGP.TP(componentID,1)
if result == 0 :
    print('position=>', response)
else:
    print('Error=>',errString)
# unregister device
AGP.UnregisterComponent(componentID);