#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tues Jun 11 16:19:14 2019
This is an example experiment script for the KM group instrumentation software. 
The experiment controlled by this script is a dynamic ptychographic scan.
@author: jeremythurston
"""

import util

#----------------------------------Setup---------------------------------------

# Params-----------------------------------------------------------------------
# Delay stage parameters
delayTimeFunction = "exponential"
min_t = 100 # in ps
max_t = 700 # in ps
step_size = 5 # in ps, # only use if delayTimeFunction = "linear"
min_step = 1 # only use if delayTimeFunction = "exp"
max_step = 10 # only use if delayTimeFunction = "exp"
t0 = 600 # in mm?????????
number_of_steps = 20 # used for exponential steps
there_and_back = 1 # Indicates whether than scan goes only direction or there and back.
pump_probe = 1

# Scan position parameters
scanPattern = "raster"
center = [100, 1234] # x, y
beamOnlyPosition = [100, 500, 4000] # x, y, z
scan_step_size = 4
num_points = 64
scanArea = 50000
random = 0
beam_diam = 100 # in microns
overlap = 0.7 
area = 10000 # in microns^2

# Camera parameters
exposureTime = 0.1 # in seconds
xRange = [100, 1026] # min, max
yRange = [500, 1067] # min, max
binning = 4
accumulations = 3
temperature = -60 # in degrees Celsius
readout_rate = 1000 #in kHz

# Instruments
camera = "andor"
delayStage = "aerotech"
sampleStage = "smaract"

# Data destination
dataDestination = "C:\Whatever"

#maybe save to csv file so the user has all the parameters
#somehow save params

#------------------------------------------------------------------------------
# Populates delay times
if delayTimeFunction == "linear":
	delay_times = util.delay_times_linear(min_t, max_t, t0, step_size)
elif delayTimeFunction == "exponential":
    delay_times = util.delay_times_exp(min_t, max_t, t0, min_step, max_step, number_of_steps)
else:
    print("Invalid delay time function type")

# Populate scan positions
if scanPattern == "fermat_points":
    scanPositions = util.fermat_spiral_points(center, beam_diam, overlap, num_points)
elif scanPattern == "fermat_area":
    scanPositions = util.fermat_spiral_area(center, beam_diam, overlap, area)
elif scanPattern == "raster":
    scanPositions = util.rand_raster(center, scan_step_size, num_points, random)
else:
    print("Invalid scan pattern")
#---------------------------------Test-----------------------------------------
# Check if the instruments are communicating with the computer correctly.

#-----------------------------Run Experiment-----------------------------------

#for delayTime in delayTimes:
#    # Move delay stage to position
#    for scanPosition in scanPositions:
#        # Move sample stage to scan position
#        
#        # Record image
#        # Save image
#    