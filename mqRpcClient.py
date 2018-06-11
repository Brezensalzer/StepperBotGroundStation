#!/usr/bin/python3
import robotPosition
import nanoLidar
import matplotlib.pyplot as plt
import numpy as np
#from drawnow import drawnow

#-------------------------------------------
# automatic plot
#-------------------------------------------
plt.ion()          # enable interactivity
plt.figure()       # make a figure
plt.axis('equal') # equal x- and y-spacing, circles instead of eggs
plt.grid()

# plot parameters
color = ['red','blue','orange','magenta']
scale = 50

#-------------------------------------------
# robot objects
#-------------------------------------------
robot = robotPosition.robotPosition()
lidar = nanoLidar.nanoLidar()

#-------------------------------------------
# dynamic chart update
#-------------------------------------------
def updateChart(xp, yp, theta):
    global plt
    # start scan
    print("LIDAR scan...")
    lidar.scan(xp, yp, theta)
    print(lidar.getNumPoints())
    for i in lidar.map:
        plt.scatter(i[1], i[2], c='blue', s=scale, label=color,alpha=0.3, edgecolors='none')

#-------------------------------------------
# main program
#-------------------------------------------
print("-----------------------")
print(" Testfahrt StepperBot")
print("-----------------------")

# get firmware info
print("Chassis Version:")
print(robot.getInfo())

print("Lidar Version:")
print(lidar.getInfo())

#-------------------------------------------
# robot position and view
#-------------------------------------------
robot.powerOn()
(xp, yp, theta, theta_rad) = robot.getPosition()
plt.scatter(xp, yp, color='green', s=scale, label=color,alpha=1.0, edgecolors='none')
updateChart(xp, yp, theta)
plt.pause(0.01)

#-------------------------------------------
# new robot position and view
#-------------------------------------------
run = True

while run:
    distance = int(input("Distance [mm]: "))
    angle = int(input("Turn angle [degrees]: "))
    scan = int(input("Lidar scan (1/0): "))
    (xp, yp, theta, theta_rad) = robot.setPosition(distance,angle)
    plt.scatter(xp, yp, color='green', s=scale, label=color,alpha=1.0, edgecolors='none')
    if scan == 1:
        updateChart(xp, yp, theta)
    plt.pause(0.01)
    if int(input("Carry on (1/0): ")) == 0:
        run = False

print("deaktiviere Motoren")
robot.powerOff()

print("track:")
print(robot.getTrack())

while True:
    plt.pause(0.05)    
