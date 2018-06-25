#!/usr/bin/env python

'''
nanLidarslam.py based on
xvslam.py : BreezySLAM Python with GetSurreal XV Lidar by D. Levy
https://github.com/simondlevy/BreezySLAM
'''

MAP_SIZE_PIXELS         = 500
MAP_SIZE_METERS         = 10

from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import XVLidar as LaserModel

import logging 
import asyncio 
from aiocoap import *

import nanoLidar
import robotPosition

from pltslamshow import SlamShow

host = 'beagle.modellmarine.de'

#---------------------------------------
async def main():

    #---------------------------------------
    # Setup Lidar unit and SLAM
    #---------------------------------------
    # Connect to Lidar unit
    lidar = nanoLidar.nanoLidar(host)
    # get firmware info 
    print("Lidar Version:") 
    print(lidar.getInfo())

    # Create an RMHC SLAM object with a laser model and optional robot model
    slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

    # Set up a SLAM display
    display = SlamShow(MAP_SIZE_PIXELS, MAP_SIZE_METERS*1000/MAP_SIZE_PIXELS, 'SLAM')

    # Initialize an empty trajectory
    trajectory = []

    # Initialize empty map
    mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)

    #---------------------------------------
    # Setup Robot unit
    #---------------------------------------
    # Connect to robot unit
    robot = robotPosition.robotPosition(host)
    robot.powerOn()
    # get firmware info 
    print("Chassis Version:") 
    print(robot.getInfo())  

    #---------------------------------------
    # main loop
    #---------------------------------------
    run = True
    while run:

        # Update SLAM with current Lidar scan, using first element of (scan, quality) pairs
        slam.update([pair[0] for pair in lidar.getScan()])

        # Get current robot position
        x, y, theta = slam.getpos()

        # Get current map bytes as grayscale
        slam.getmap(mapbytes)

        display.displayMap(mapbytes)

        display.setPose(x, y, theta)

        # Exit on ESCape
        key = display.refresh()
        if key != None and (key&0x1A):
            run = False

        # Movement control
        distance = int(input("Distance [mm]: "))
        angle = int(input("Turn angle [degrees]: "))
        (xp, yp, theta_deg, theta_rad) = robot.setPosition(distance,angle)
        if int(input("Carry on (1/0): ")) == 0: 
            run = False

    # power off stepper motors   
    robot.powerOff()

#-------------------------------------------
if __name__ == '__main__':
    syncio.get_event_loop().run_until_complete(main())
