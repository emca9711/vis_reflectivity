# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 13:22:56 2020

@author: KM Lab
"""

# Import classes
from aerotech_stage import AerotechStage
from ni_PCIe6321 import NI_PCIe6321

class Framework:
    def __init__(self):
        # initialize equipment
        self.stage1 = AerotechStage() # Primary pump-probe delay stage
        self.stage1_passes = 4 # number of times the beam goes through the retroreflector on the primary delay stage
        self.stage1_t0 = 0.5 # (picoseconds) the position of the delay stage at pump-probe overlap
        self.daq = NI_PCIe6321()
        self.stage1.initializeStage()