# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 15:06:37 2019
This is a single pump-probe experiment.


need to use 
set_AI_timing(self, dwell, samples)



@author: Emma Cating-Subramanian
"""
import util, time, datetime, csv
import matplotlib.pyplot as plt
import numpy as np
import random as rand
from matplotlib.animation import FuncAnimation

# Import classes
from aerotech_stage import AerotechStage
from ni_PCIe6321 import NI_PCIe6321
from framework import Framework

class eemcs_xwing_exp:
    """
    
    """
    def __init__(self, min_t, max_t, step_size, dwell, *args):
        """
        dwell is in miliseconds
        min_t  is in picoseconds
        max_t  is in picoseconds
        step_size is in picoseconds
        args[0] = transition time from short steps to long steps
        args[1] = large step size
        
        """
        
        #-------------lab-specific instrumentation-----------------------------
        # User should update these as needed.
        # self.stage1 = AerotechStage() # Primary pump-probe delay stage
        # self.stage1_passes = 4 # number of times the beam goes through the retroreflector on the primary delay stage
        # self.stage1_t0 = 0.5 # (milimeters) the position of the delay stage at pump-probe overlap
        # self.daq = NI_PCIe6321()
        self.framework = Framework()
        self.stage1 = self.framework.stage1
        self.stage1_passes = self.framework.stage1_passes
        self.stage1_t0 = self.framework.stage1_t0
        self.daq = self.framework.daq
        
        self.data_file = r'C:\Users\KM Lab\Dropbox (KM JILA)\X1B51_Magnetics\VisibleBeamline_Data\2020'
        
        if len(args) == 0:
            self.scan_type = "linear"
        else:
            self.scan_type = "nonlinear"
        
        self.initialize(min_t, max_t, step_size, dwell, *args)
        
        
    def initialize(self, min_t, max_t, step_size, dwell, *args):
        """
        Initialize is a separate function from the __init__ so that you can 
        change many of the experiment parameters between runs. Use this rather
        than creating a new experiment, as that can confuse the DAQ card.
        
        Provide the min_t and max_t and step size in mm
        """
        # set up delays, etc.
        if self.scan_type == "linear": 
            self.times = util.delay_times_linear(min_t, max_t, step_size)
        else:
            self.times = util.delay_times_double(min_t, args[0], step_size, max_t, args[1])
        self.setDelays(self.times)
        self.dwell = dwell*10**(-3) # units =milliseconds
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
            line1, = ax.plot(self.times, datay, 'r-') # Returns a tuple of line objects, thus the comma
            ax.set_ylim(self.lim1, self.lim2)
            
            #set up for saving the data
            self.experiment_time = datetime.datetime.now()
            
                
            
            # plot the data using pyplot
            i=0
            for pos in self.positions:
                # Move the stage, pause to let lock-in settle before collecting point
                self.stage1.moveStageTo(pos) #note that self.positions are in units of mm!
                time.sleep(30*10**(-3))
                # collect a point. This gives an array of data. Average that array.          
                datay[i] = np.average(self.daq.collect_point(self.dwell, self.samps_per_chan))
                # Update the plot of the data every nth data point. https://stackoverflow.com/questions/4098131/how-to-update-a-plot-in-matplotlib
                if i % 2 == 0:
                    self.datay = datay
                    ax.set_ylim(min(datay)-0.1*max(datay), 1.1*max(datay))
                    line1.set_ydata(datay)
                    fig.canvas.draw()
                    fig.canvas.flush_events()
                    plt.pause(0.01)
                i = i+1
            self.stopExp() 
        except KeyboardInterrupt:
            self.stopExp()
            #add a self.save_date call here?
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
        self.positions = util.ps_to_mm(self.times, self.stage1_passes) #convert times into mm of stage travel for primary pump-probe stage
        #self.positions = times
       #Check if the positions are within the stage's bounds
        if min(self.positions)<self.stage1.minPos:
            raise Exception('Desired minimum time is out-of-bounds')
        if max(self.positions) > self.stage1.maxPos:
            raise Exception('Desired max time is out of bounds.')            
         
         
    def set_t0(self, t0):
        self.stage1_t0 = t0
        #provide this in ps
        
    def saveData(self):
        name = str(self.experiment_time.year) +str(self.experiment_time.month)+str(self.experiment_time.day) +'-'+str(self.experiment_time.hour) +str(self.experiment_time.minute) 
        with open(self.data_file + name + '.csv','a', ) as data_file:
            wr = csv.writer(data_file, delimiter=',')
            
            for i in range(len(self.datay)):
                wr.writerow([self.times[i], self.datay[i]])
            