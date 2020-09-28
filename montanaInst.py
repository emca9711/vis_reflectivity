# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 15:24:02 2019

@author: KM Lab
"""




class montanaInst:
    
    def __init__(self, DAQ, daq_chan):
        #Parameters for the analog input to the magneto-optical module. See manual.
        self.currentGain = -3.1 #Amps/Volt
        self.inputMax = 10 #Volts
        self.DAQ = DAQ
        self.daq_chan = daq_chan
    
    #Need to calculate the field strength from the applied voltage. Tricky b/c
    #the curve is nonlinear. 
    
    def set_field(self, field):
        self.field = field
        voltage = self.field_to_volt(field)
        self.DAQ.set_AO(self.daq_chan, voltage)
        
    def field_to_volt(self, field):
        return field
