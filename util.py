# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 14:49:26 2019
This is the utility file for ImAGERS, the KM group instrumentation software
(IMage Acquisition and Generalized Experimet Recipe Software).
This file should contain any functions that are common between multiple 
experiment types with the goal of making it easy for users to design their own 
experiment scripts by combining these functions in various ways.

Note: Storing classes in modules for easy loading: http://introtopython.org/classes.html#Storing-a-single-class-in-a-module

@author: ecating
"""
import numpy as np
import matplotlib.pyplot as plt
import time

# Functions to initialize your system -----------------------------------------
def load_config():
    return

def initialize_all():    
    return

# Functions which provide spatial scan coordinates ----------------------------
def fermat_spiral_points(center, beam_diam, overlap, num_points):
    """Takes the central position and beam diameter and calculates positions
    to scan according to a Fermat spiral. Uses the beam diameter and overlap 
    to calculate the necessary step size to achieve the desired overlap.
    Does this for the number of overall positions desired."""
    return spiral

def fermat_spiral_area(center, beam_diam, overlap, area):
    """Takes the central position and beam diameter and calculates positions
    to scan according to a Fermat spiral. Uses the beam diameter and overlap 
    to calculate the necessary step size to achieve the desired overlap.
    Does this for the overall scan area desired."""
    return spiral

def rand_raster(center, step_size, num_points, random):
    """This function takes a center (x,y) coordinate, a desired average step 
    size, and number of point and generates a raster scan based on those 
    parameters. The random parameter is the percentage of the step size that
    the coordinates may be randomly offset by (to prevent periodic sampling
    errors."""
    xscan = []
    yscan = []
    
    xcenter = center[0] # first element of center array
    ycenter = center[1] # second element of center array
    
    scan_size = int(np.sqrt(num_points)) # This assumes a square scan area
    
    xrange = np.arange(xcenter - ((scan_size - 1) * step_size) / 2, xcenter + ((scan_size - 1) * step_size) / 2 + step_size, step_size)
    yrange = np.arange(ycenter - ((scan_size - 1) * step_size) / 2, ycenter + ((scan_size - 1) * step_size) / 2 + step_size, step_size)
    
    # Creates two arrays xscan and yscan
    for step, ystep in enumerate(yrange):
        xscan.append(xrange[::(-1)**step])
        yscan.append(np.ones_like(xrange) * ystep)
        
    xscan = np.concatenate(xscan)
    yscan = np.concatenate(yscan)
        
    # Combine the two arrays into a list of vectors
    raster = []
    
    for i in range(0, len(xscan)):
        scan_element = []
        
        scan_element.append(xscan[i])
        scan_element.append(yscan[i])
        raster.append(scan_element)
    
    return raster

# Functions which provide temporal scan coordinates ---------------------------
def delay_times_linear(min_t, max_t, step_size):
    """This function takes a minimum delay in ps and a maximum delay in ps and 
    a step size and generates a range of delay stage positions"""
    return np.flip(np.arange(max_t, min_t - step_size, -step_size))
def delay_times_double(min_t, t2, step_size1, max_t, step_size2):
    foo = np.arange(t2, min_t - step_size1, -step_size1)
    bar = np.arange(max_t, t2, -step_size2)
    return np.flip(np.concatenate((bar,foo),axis=0))
    
def delay_times_exp(min_t, max_t, t0, min_step, max_step, number_of_steps):
    """Returns an array of delay times in exponential steps given min_t, max_t,
    min_step, and max_step.
    
    min_step and max_step currently not used"""
    delays = []
    
    after_t0 = np.logspace(np.log(min_t), np.log(t0), num = number_of_steps, endpoint = True, base = np.e)
    after_t0 = min_t + t0 - after_t0
    after_t0 = after_t0[::-1]
    after_t0 = after_t0[:-1]
    
    before_t0 = np.logspace(np.log(t0), np.log(max_t), num = number_of_steps / 2, endpoint = True, base = np.e)
    
    delays = np.concatenate([after_t0, before_t0])
    
    delays = delays.tolist()
    
    y = np.zeros_like(delays)
    
    plt.plot(delays, y, 'o')
    
    return delays

# def ps_to_mm(delays, stage_passes, t0_in_ps):
#     """Converts values in ps to values in mm."""
#     mm_delays = (delays + t0_in_ps) * (1/stage_passes) * 0.2998
#     return mm_delays

def ps_to_mm(delays, stage_passes):
    """Converts values in ps to values in mm."""
    mm_delays = (delays) * (1/stage_passes) * 0.2998
    return mm_delays

# def mm_to_ps(delays_in_mm, stage_passes, t0_in_ps):
#     """Converts values in ps to values in mm."""
#     ps_delays = (delays_in_mm * stage_passes)/0.2998 - t0_in_ps
#     return ps_delays

def mm_to_ps(delays_in_mm, stage_passes):
    """Converts values in ps to values in mm."""
    ps_delays = (delays_in_mm * stage_passes)/0.2998 
    return ps_delays
#
## --------------- Testing functions --------------------------------
#
#def alignStage(stage):
#    for i in range(100):
#        stage.moveStageTo(stage.maxPos)
#        time.sleep(5/60)
#        stage.moveStageTo(stage.minPos)
#        time.sleep(5/60)

# Data plotting functions  ---------------------------------------------------
def create_new_fig():
    return plt.figure()

#def plot_point(x,y,fig_handle):
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
