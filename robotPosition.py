# robotPosition.py
# Class for tracking a robot's position
#
import math
import logging 
import asyncio  
from aiocoap import *  

logging.basicConfig(level=logging.INFO)

#------------------------------------
# Drive a robot
#------------------------------------
class robotPosition:
    'Class for tracking a robot\'s position'

    def __init__(self, host):
        # coap target
        self.host = host
        # coordinates in [mm]
        self.x = 0
        self.y = 0
        # direction in degrees
        self.theta_deg = 0
        # direction in radians
        self.theta_rad = math.radians(self.theta_deg)
        # track
        self.track = []
        self.track.append((self.x, self.y, self.theta_deg, self.theta_rad))
        # calibration, todo...
        #response = await self.__coapPut('coap://'+self.host+'/robot/command','t102.5#') 

    async def __coapGet(self,coap_uri): 
        # initialize coap 
        protocol = await Context.create_client_context()
        request = Message(code=GET, uri=coap_uri)
        try: 
            response = await protocol.request(request).response
        except Exception as e: 
            print('Failed to fetch resource:') 
            print(e)
        else: 
            # print('Result: %s\n%r'%(response.code, response.payload)) 
            return response.payload.decode('utf-8')

    async def __coapPut(self,coap_uri,payload): 
        # initialize coap 
        protocol = await Context.create_client_context()
        request = Message(code=PUT, uri=coap_uri, payload=payload.encode('utf-8'))
        try: 
            response = await protocol.request(request).response
        except Exception as e: 
            print('Failed to fetch resource:') 
            print(e)
        else: 
            # print('Result: %s\n%r'%(response.code, response.payload)) 
            return response.payload.decode('utf-8')

    async def listMethods(self): 
        # list available coap methods 
        response = await self.__coapGet('coap://'+self.host+'/.well-known/core') 
        return response

    async def getInfo(self):
        response = await self.__coapPut('coap://'+self.host+'/robot/command','i#') 
        return response
		
    def getPosition(self):
        return (self.x, self.y, self.theta_deg, self.theta_rad)

    async def powerOn(self):
        response = await self.__coapPut('coap://'+self.host+'/robot/command','e#') 
		
    async def powerOff(self):
        response = await self.__coapPut('coap://'+self.host+'/robot/command','d#') 
		
    async def setPosition(self, distance, angle):
        # distance in [mm]
        # angle in degrees
        # angle > 0: turn left
        # angle < 0: turn right
        
        # drive
        if distance > 0:  # forward
            cmd = 'f' + str(distance) + '#'
            response = await self.__coapPut('coap://'+self.host+'/robot/command',cmd) 
        if distance < 0:  # backward
            cmd = 'b' + str(abs(distance)) + '#'
            response = await self.__coapPut('coap://'+self.host+'/robot/command',cmd) 

        # turn
        if angle > 0:     # turn left
            cmd = 'l' + str(angle) + '#'
            response = await self.__coapPut('coap://'+self.host+'/robot/command',cmd) 
        if angle < 0:     # turn right
            cmd = 'r' + str(abs(angle)) + '#'
            response = await self.__coapPut('coap://'+self.host+'/robot/command',cmd) 

        # calculate new position
        self.x = self.x + int(distance * math.cos(self.theta_rad))
        self.y = self.y + int(distance * math.sin(self.theta_rad))
        # calculate new direction
        self.theta_deg = self.theta_deg + angle
        # normalize to one full circle
        if self.theta_deg >= 360:
            self.theta_deg = self.theta_deg - 360
        # we stay to positive degrees
        if self.theta_deg < 0:
            self.theta_deg = self.theta_deg + 360
        self.theta_rad = math.radians(self.theta_deg)
        # append to track
        self.track.append((self.x, self.y, self.theta_deg, self.theta_rad))
        return (self.x, self.y, self.theta_deg, self.theta_rad)

    def getTrack(self):
        return self.track

