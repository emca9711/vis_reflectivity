# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 15:06:37 2019
This is a single pump-probe experiment.


need to use 
set_AI_timing(self, dwell, samples)



@author: Emma Cating-Subramanian
"""
import util, time
import matplotlib.pyplot as plt
import numpy as np
import random as rand
from matplotlib.animation import FuncAnimation

# Import classes
from aerotech_stage import AerotechStage
from ni_PCIe6321 import NI_PCIe6321

class eemcs_xwing_exp:
    """
    Currently this experiment is for no magnetic field. No analog outputs are 
    required, analog inputs only.
    
    Problems to solve:
        2020-01-07 - Emma
        At the moment, you can only have one of these experiments in existance 
        at a time or else the DAQ gets confused. This is probably why JK had 
        written a Framework... May need to revisit this if we don't end up 
        using Bluesky.
        
        2020-01-07 - Emma
        The plot won't scale its axis to match the data. Right now I've delt 
        with that by creating a function to change the default y axis height.
        Needs a better solution.
    
    
    
    
    """
    def __init__(self, min_t, max_t, step_size, dwell):
        """
        dwell is in miliseconds
        min_t is in picoseconds
        max_t is in picoseconds
        step_size is in picoseconds
        """
        
        #-------------lab-specific instrumentation-----------------------------
        # User should update these as needed.
        self.stage1 = AerotechStage() # Primary pump-probe delay stage
        self.stage1_passes = 4 # number of times the beam goes through the retroreflector on the primary delay stage
        self.stage1_t0 = 0.5 # (milimeters) the position of the delay stage at pump-probe overlap
        self.daq = NI_PCIe6321()
        self.initialize(min_t, max_t, step_size, dwell)
        # initialize equipment
        self.stage1.initializeStage()
        
    def initialize(self, min_t, max_t, step_size, dwell):
        """
        Initialize is a separate function from the __init__ so that you can 
        change many of the experiment parameters between runs. Use this rather
        than creating a new experiment, as that can confuse the DAQ card.
        
        Provide the min_t and max_t and step size in mm
        """
        # set up delays, etc.
        self.times = util.delay_times_linear(min_t, max_t, step_size)
        #self.times = util.delay_times_double(min_t, 40, 0.1, max_t, 1)
        self.setDelays(self.times)
        self.dwell = dwell*10**(-3) # units =microseconds
        self.samps_per_chan = 10 # samples per channel the DAQ will collect during each dwell
        
        #set limits on the plot's y axis
        self.setYAxisLim(-.1,10)
        
 
    def startExp(self):
        """This function runs the experiment one time and plots the results as 
        they are collected.
        
        I'm using a 'Try, Except' block here so that if the user wants to stop
        the program running (during data collection, say) they can do so with 
        a KeyboardInterrupt (Ctrl -c) without breaking the code/confusing the 
        DAQ card.
        """
        try:
            self.daq.set_up_DAQ('1', ['ai0'], ['ao0']) # Device number, AI_chans, AO_chans
            
            datay = np.zeros(len(self.positions))
            # Set up the figure
            fig = plt.figure()
            plt.ion()
            ax = fig.add_subplot(111) #https://matplotlib.org/api/_as_gen/matplotlib.figure.Figure.html?highlight=add_subplot#matplotlib.figure.Figure.add_subplot
            line1, = ax.plot(self.positions, datay, 'r-') # Returns a tuple of line objects, thus the comma
            ax.set_ylim(self.lim1, self.lim2)
            # plot the data using pyplot
            i=0
            for pos in self.positions:
                # Move the stage, pause to let lock-in settle before collecting point
                self.stage1.moveStageTo(pos) #note that self.positions are in units of mm!
                time.sleep(3*self.dwell)
                
                # collect a point. This gives an array of data. Average that array.          
                point = np.average(self.daq.collect_point(self.dwell, self.samps_per_chan))
                
                # put the new data into the x and y data arrays
                datay[i] = point
                # Update the plot of the data every nth data point. https://stackoverflow.com/questions/4098131/how-to-update-a-plot-in-matplotlib
                if i % 2 == 0:
                    ax.set_ylim(min(datay)-0.1*max(datay), 1.1*max(datay))
                    line1.set_ydata(datay)
                    fig.canvas.draw()
                    fig.canvas.flush_events()
                    plt.pause(0.2)
                i = i+1
            self.datay = datay
            self.stopExp() #This doesn't work here b/c CollectPoint stops the DAQ task...
        except KeyboardInterrupt:
            self.stopExp()
            print('Interrupted')
            
            
            
    def stopExp(self): 
        """
        Tells the DAQ to stop. Use when you get a -50103 error from the DAQ
        """
        self.daq.close_DAQ()
                
        
    def setYAxisLim(self, lim1, lim2):
        """
        sets the lower and upper limits of the y axis for this experiment. 
        """
        self.lim1 = lim1
        self.lim2 = lim2
    
    def setDelays(self, times):
        #self.times = times # units = picoseconds
        self.positions = util.ps_to_mm(self.times, self.stage1_passes, self.stage1_t0) #convert times into mm of stage travel for primary pump-probe stage
        self.positions = times 
       #Check if the positions are within the stage's bounds
        if min(self.positions)<self.stage1.minPos:
            raise Exception('Desired minimum time is out-of-bounds')
        if max(self.positions) > self.stage1.maxPos:
            raise Exception('Desired max time is out of bounds.')            
         
         
    def set_t0(self, t0):
        self.stage1_t0 = t0