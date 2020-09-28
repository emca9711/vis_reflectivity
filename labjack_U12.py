# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 12:26:56 2019

Documentation (such as it is):  https://labjack.com/support/software/api/ud/overview
and https://labjack.com/support/datasheets/u12
Examples:   http://www.physics.hmc.edu/courses/p057/pmwiki/pmwiki.php/Software/SampleLabJackCode
            https://github.com/labjack/LabJackPython/blob/master/Examples/u6Noise.py

Important information when using this device:
-- Gain on the LabJack needs to be 1 otherwise settling time can be > 1 ms. With
    a gain of 1, the settling time is 10 microseconds.
    https://labjack.com/support/app-notes/SettlingTime
-- Signal source resistance of up to 1 kOhm is acceptable
-- Have the DAQ control the timing of data collection. The computer itself cannot
    promise timing accuracy of better than ~ 10 ms (and that's on a good day) 
    so it's best to have the DAQ do that for you.                                               

Streaming mode: https://labjack.com/support/datasheets/u6/operation/stream-mode
-- The data input buffer on the DAQ can hold up to 984 samples only. After the 
    buffer is full, DAQ will continue streaming BUT will not save any new dats
    to the buffer until it has been emptied.
    
Analog input resolution 12 bit, +/- 10V
Analog output resolution 10 bit +/- the supply voltage (which can have an error 
as large as 5%, so monitor the supply voltage with an analog input channel)
Analog outputs have maximum update rate of 50 Hz https://labjack.com/support/datasheets/u12/hardware-description/ao0-ao1



@author: Emma Cating-Subramanian
"""
import time
import ctypes as c
import u12
from matplotlib import pyplot as plt
labjack=u12.U12() # automatically opens the U6

numChannels = 2
resolutionIndex = 1
gain = 1 # Range = +/- 10 V. This corresponds to the output of the lockin.
sampleRate = 10 # units of samples/second. https://labjack.com/support/datasheets/u6/operation/stream-mode



"""
I'm starting this by doing all the timing in Windows rather than on the DAQ
since the LabJack doesn't have very good timing anyway.
"""
scanRate = sampleRate/numChannels

assert (sampleRate <= 50E3),"LabJack U12 problem: sample rate too high for device!"

def setAO(chan, voltage):
    """
    Set the analog output voltage to a desired value.
    The voltage will be held at whatever it is set to until you set it to something else
    
    I need to add functionality to account for fluctiations in the supply voltage (that is what actually sets the voltage scale on this damn thing)
    """
    assert (voltage <= 5.0),"Desired AO voltage too high for U12."
    voltage1 = 0
    voltage0 = 0
    if chan == 0:
        voltage0 = voltage
    if chan == 1:
        voltage1 = voltage
    u12.eAnalogOut(voltage0, voltage1)

def testAI():
    testing = labjack.eAnalogIn(0)
    print(testing)
'''
Set AO1 = 5
Read AO1
Whatever AO1 actually is, find the ratio of 5/AO1
Multiply the desired voltage for AO0 by that ratio
Problem: How often should this occur? How often *can* this occur when streaming? How stable is the supply voltage and over what time scales?
''' 


""" 
Right now the connections are: 
AI0 - AO0
AI1 -> AO1
AI2 -> +5V
"""
# Collect a data point
def collectPoint(dwell_time):
    # Set AO voltage for the cryostat
    setAO(0,4)
    setAO(1,2)
    
    # Clear stream if it is streaming
    if labjack.streaming:
        labjack.aiStreamClear()

    tic = time.time()
    data = labjack.aiBurst(1, [0], 400, 10)
    toc = time.time()
    print(toc-tic)

    return(data)
    
            
    
    









    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
## stop stream in case there is one ongoing
#if labjack.streamStarted:
#    labjack.streamStop()
#labjack.streamStart()
#dataCount = 0
#packetCount = 0
#errorString =[]
## code here directly from https://github.com/labjack/LabJackPython/blob/master/Examples/streamTest.py
#for r in labjack.streamData():
#    if r is not None:
#        # Our stop condition
#        if dataCount >= float(2):
#            break
#
#        if r["errors"] != 0:
#            errorString.append("Errors counted: %s ; %s\n" % (r["errors"], datetime.now()))
#            print(1)
#
#        if r["numPackets"] != labjack.packetsPerRequest:
#            errorString.append("----- UNDERFLOW : %s ; %s\n" % (r["numPackets"], datetime.now()))
#            print(2)
#
#        if r["missed"] != 0:
#            # missed += r['missed']
#            errorString.append("+++ Missed %s\n" % r["missed"])
#            print(3)
#        dataCount += 1
#        packetCount += r['numPackets']
#    else:
#        # Got no data back from our read.
#        # This only happens if your stream isn't faster than the USB read
#        # timeout, ~1 sec.
#        print("No data ; %s" % datetime.now())
#
#labjack.streamStop()
## Close the LabJack
#labjack.close()

        

           
                



   