# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 11:50:43 2019
Class for the Aerotech stages
@author: Emma Cating-Subramanian
"""
import ctypes as c
import ctypes.wintypes as cw
import sys
import time

class AerotechStage:
    
    def __init__(self):
        # These dlls contain all the "support" functions for the EnsembleC64 dll.
        c.WinDLL("C:\\Users\\KM Lab\\Documents\\CLibrary_Aero\\Bin64\\AeroBasic64.dll")
        c.WinDLL("C:\\Users\\KM Lab\\Documents\\CLibrary_Aero\\Bin64\\EnsembleCore64.dll")
        #the dll containing all the user-callable functions
        self.ensemble = c.WinDLL("C:\\Users\\KM Lab\\Documents\\CLibrary_Aero\\Bin64\\EnsembleC64.dll")
        # Create the pointers needed for communication with the stage.
        self.cHandleArray = c.pointer(c.c_void_p(0))
        self.cHandleCount = cw.DWORD(0)
        self.cAxisMask = c.c_ulong(0)
        # This is the offset value found in the Ensemble Configuration Manager. It might change. Eventually the code will search for this value.
        self.offset = -55 #units = mm
        self.minPos = 110 + self.offset
        self.maxPos = 0 + self.offset
#    def runCommand():
        """
        Ultimately I want this function to run a command and check the error.
        May refactor to include it later on.
        """
    
    def initializeStage(self):
        #Connect computer to all available ensemble stages
        self.ensemble.EnsembleConnect(c.pointer(self.cHandleArray), c.pointer(self.cHandleCount))
        print('stage connected')
        # Check if we only have 1 stage. Assume we only have one handle (i.e. one stage)
#assert self.cHandleCount.value == 1, 'More than one stage present!'
        # Assign the generated handle to variable cHandle
        self.cHandle = self.cHandleArray.contents
        # EnsembleMotionSetupAbsolute tells the stage we will be using absolute coordinates
        # rather than relative/incremental coordinates for motion.
        # ensemble.EnsembleMotionSetupAbsolute(cHandle) should return 1 if the action was successful
        if not self.ensemble.EnsembleMotionSetupAbsolute(self.cHandle):
            print('Problem setting Ensemble stage motion to absolute.')
            self.getEnsembleError()
        # Get the AXISMASK, the list of all axes on the stage. This needs to be passed to other functions.
        if not self.ensemble.EnsembleInformationGetAxisMask(self.cHandle, c.pointer(self.cAxisMask)):
            print('Problem getting Axis Mask.')
            self.getEnsembleError()
        # Enable motion for the axes in the AXISMASK    
        if not self.ensemble.EnsembleMotionEnable(self.cHandle, self.cAxisMask):
            print('Problem enabling motion.')
            self.getEnsembleError()
        # Send the stage to its home position. Passing it the handle to the stage and
        # the axes that we are using (just 1 in this case)                
   
    def homeStage(self):
        if not  self.ensemble.EnsembleMotionHome(self.cHandle, self.cAxisMask):
            print('Problem homing Ensemble stage.')
            self.getEnsembleError()
        
    def moveStageTo(self, position):
        """
        EnsembleMotionMoveAbs moves the stage by a DISTANCE at a SPEED in mm/s
        This stage (in X-wing) uses home type "Home To Limit And Reverse To Marker"
        Limit high: 110
        Limit low: 0
        This means the stage can move between 0 + home offset to 110 + home offset
        look up AXISFAULT, AXISSTATUS, DATASIGNAL_LatchedMarkerPosition , DATASIGNAL_PositionFeedback 
        EnableStatusPositionMarkerLatched
        EnsembleDataCollectionConfigAddSignal     
        
        position that is passed to the stage should be independent of the offset.
        Position should also be in units of milimeters.
        """
        if position <= self.minPos and position >= self.maxPos:
            self.cSpeed = c.pointer(c.c_double(50))
            self.cPosition = c.pointer(c.c_double(position))
            if not  self.ensemble.EnsembleMotionMoveAbs(self.cHandle, self.cAxisMask, self.cPosition, self.cSpeed):
                print('Problem moving Ensemble stage.')
                self.getEnsembleError()
        else:
           print('Desired move location is out of bounds!')
        
    def getEnsembleError(self):
        cErrStr = c.create_string_buffer(100)
        # EnsembleGetLastErrorString returns 1 if an error string was successfully retrieved (even if the error is {0} = no error)
        # This asserts that the error code was retrieved. Then we need to check what it actually is.
        assert self.ensemble.EnsembleGetLastErrorString(cErrStr, cw.DWORD(c.sizeof(cErrStr))), 'Ensemble call failed - cannot fetch error.'
        print(str(cErrStr.raw).decode('base64', 'strict') )
        sys.exit()
        
    def alignStage(self, iterations, dwell):
        """
        This sends the stage to the end of its travel and waits for 'dwell' seconds.
        It then sends it to the opposite end of its travel and waits again.
        This repeats 'iterations' number of times. Aids in stage alignment.
        """
        for i in range(iterations): 
            self.moveStageTo(self.minPos)
            time.sleep(dwell)
            self.moveStageTo(self.maxPos)
            time.sleep(dwell)






