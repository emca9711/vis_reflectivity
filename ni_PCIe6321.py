# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 17:20:02 2019

Class for the National Instruments DAQ card

Information:
    Installing the NIDAQMX for python package
        https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019Pf1SAE&l=en-US
    API Reference
        https://nidaqmx-python.readthedocs.io/en/latest/
    Example code 
        https://github.com/ni/nidaqmx-python/tree/master/nidaqmx_examples
        https://github.com/ni/nidaqmx-python/tree/master/nidaqmx/_task_modules
    PyDAQmx and NIDAQmx references:
        https://pythonhosted.org/PyDAQmx/usage.html
        http://zone.ni.com/reference/en-XX/help/370471AA-01/TOC3.htm
    
Steps (per http://www.ni.com/tutorial/5409/en/)
    Create a Task and Virtual Channels
    Configure the Timing Parameters
    Start the Task
    Perform a Read and/or Write operation from the DAQ
    Stop and Clear the Task.

From my previous software:
    Calculate the sampling rate, # samples/chan, and create a place they will be stored
    Set up trigger AI line
        DAQmxCreateTask
        DAQmxCreateAIVoltageChan
        DAQmxCfgSampClkTiming
    set up trigger DO line
        DAQmxCreateTask
        DAQmxCreateDOChan
    Create all the input voltage channels for data collection
        DAQmxCreateAIVoltageChan
    Go to the point you want to collect data at
    start the DAQ
        DAQmxStartTask
    Collect a data point
        (I'm going to try a new way of doing this.)
    Read data
        DAQmxReadAnalogF64
    Stop the DAQ card
        DAQmxStopTask


Ok. Let's try this without a trigger line and see what happens. Cheeeeeeho.

DAQmxCreateTask returns 'taskHandle'
DAQmxCfgSampClkTiming(taskHandle, [], rate, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, samps_per_chan)
    [] or NULL uses clock on DAQ
    rate = samples per second per channel. 
    Therefore, time = rate * #samples / channel
    Returns status (int32). 0 if successful, other value = error code
    
@author: Emma Cating-Subramanian
"""
import PyDAQmx as daq
import ctypes as c
import numpy as np
#import time

class NI_PCIe6321:
    
    def __init__(self):
        self.name = 'PCIe6321'
        self.max_AO_V = 10
        self.min_AO_V = -10
        self.tasks = []
        
    def set_up_DAQ(self, device_number, AIchans, AOchans):
        # When you install this on a new computer, or are using a different DAQ
        # card you will need to use the appropriate device number. Check using 
        # the NI MAX software.
        # You must provide this function with an array of channel numbers for
        # the analog input (AIchans) and analog output (AOchans) you wish to use.
        # The arrays may be empty, e.g. []
        # 'ai1'
        self.dev = 'Dev'+ device_number # needs to be binary string for PyDAQmx
        
        self.analog_input = daq.Task() # Create the analog input task
        self.tasks.append(self.analog_input)
        for chan in AIchans: # Set up the channels for the AI task   
            self.analog_input.CreateAIVoltageChan(self.dev + '/' + chan, "",daq.DAQmx_Val_Cfg_Default,-10.0,10.0,daq.DAQmx_Val_Volts, None)
        self.numAIchans = len(AIchans)
        
        
        if len(AOchans) != 0: # If there are analog outputs, set up the AO task and channels
            self.analog_output = daq.Task()
            self.tasks.append(self.analog_output)
            for chan in AOchans: 
                # Make sure the inputs are acceptable
                assert (chan == 'ao0' or chan == 'ao1'),"AO channel is incorrect. Please provide either 'ao0' or 'a01'!"
                self.analog_output.CreateAOVoltageChan(self.dev +  '/' + chan,"",-10.0, 10.0, daq.DAQmx_Val_Volts,None)
            self.analog_output.StartTask() #start the analog output task
#            
    def collect_point(self, dwell, samps_per_chan):
        """
        This function takes some number of AI channels in an array
        It reads the voltage on those channels and with some rate and for some
        amount of time. Then returns the data.
        dwell needs to be in miliseconds
        samples = number of samples per channel to collect within the dwell time
        """
#        t = time.time()
        
#        dwell = dwell*10**(-3) # convert from miliseconds to seconds
        total_samples = self.numAIchans*samps_per_chan # calculate total # samples to collect over all active AI channels
        rate = (samps_per_chan/dwell) 
        self.analog_input.CfgSampClkTiming("", rate, daq.DAQmx_Val_Rising, daq.DAQmx_Val_FiniteSamps, samps_per_chan)
                
        
        # Create a pointer to a # which will be populated by the DAQ (value will
        # be the number of samples per chan actually read from the DAQ)
        read = c.c_int32()
        # Create an array of zeros the size of your expected data set from the DAQ
        data = np.zeros((total_samples,), dtype=np.float64)
        
        
        self.analog_input.StartTask()
        self.analog_input.ReadAnalogF64(samps_per_chan,2,daq.DAQmx_Val_GroupByChannel,data,total_samples,c.byref(read),None)
                          # numSampsPerChan, timeout, fillMode, readArray[], arraySizeInSamps, *sampsPerChanRead, bool32 reserved
        self.analog_input.StopTask()
        # Need some tests here. Will get to that later.
        
#        print('time to collect_point: ' + str(time.time() - t))
        
        return data        
    
    def set_AO(self, chan, voltage):
        """
        This function sets AO channel "chan" to voltage "voltage." This is a 
        point-by-point function. If necessary another can be written to take a
        series of voltages and have the DAQ handle the timing. Do not use this
        if you need better than 30 ms of confidence in your AO timing.
        
        chan must be either 'ao0' or 'ao1'
        Voltage must be in Volts and may only be between -10 and 10
        
        references:
            https://pythonhosted.org/PyDAQmx/examples/analog_output.html
            http://zone.ni.com/reference/en-XX/help/370471AA-01/daqmxcfunc/daqmxwriteanalogscalarf64/
        """        
        # Make sure the inputs are acceptable
        assert (chan == 'ao0' or chan == 'ao1'),"AO channel is incorrect. Please provide either 'ao0' or 'a01'!"
        assert (self.min_AO_V  <= voltage <= self.max_AO_V ),"AO Channel voltage is out of range. Must be between -10 V and +10 V!"
        AO_error = self.analog_output.WriteAnalogScalarF64(1, 1, voltage, None)
            # autoStart, timeout, value, *reserved
            # value should be a float64. PyDAQmx claims it will handle that. But if there's an error, it could be b/c of this.
        print(AO_error)
#        assert (AO_error == 0), "set_AO: error writing voltage to DAQ. Error code " + AO_error
        
    
    def close_DAQ(self):
        for task in self.tasks:
            #task.StopTask()
            task.ClearTask()