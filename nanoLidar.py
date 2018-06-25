# nanoLidar.py 
# Class for the self made nanoLidar
#

import logging
import asyncio
from aiocoap import *
import math

#------------------------------------
# LIDAR class
#------------------------------------
class nanoLidar:
    'Class for the self made nanoLidar'
    
    def __init__(self,host):
        # coap target
        self.host = host
        # 360 elements (distance in mm), indexed by angle
        self.map = []
        # scan number
        self.scan_num = -1
        # sensor offset from center [mm]
        self.offset = 17
        # angle correction?
        self.squint = 7.5
        # BreezSLAM compatibility
        self.lidar_data = [()]*360 # 360 elements (distance,quality), indexed by angle
        self.speed_rpm = 0

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

    async def listMethods(self):
        # list available coap methods
        response = await self.__coapGet('coap://'+self.host+'/.well-known/core')
        return response

    async def getInfo(self):
        # read firmware information
        response = await self.__coapGet('coap://'+self.host+'/lidar/info')
        return response

    async def getScan(self):
        # BreezySLAM
        # Returns 360 (distance, quality) tuples.
        # start 360 degree scan
        lines = await self.__coapGet('coap://'+self.host+'/lidar/scan').split('\r\n')
        # read scan data
        for line in lines:
            if line != '':
                (angle, dist_cm, strength) = line.split(',')
                self.lidar_data[int(angle)] = (int(dist_cm)*10,int(strength))

        return [pair if len(pair) == 2 else (0,0) for pair in self.lidar_data]

    def getRPM(self):
        return self.speed_rpm

    def scan(self, xp, yp, theta):
        # robot position xp, yp in [mm]
        # robot direction theta in degrees
        self.scan_num = self.scan_num + 1

        # start 360 degree scan
        lines = self.lidarRpc.call('scan#').decode('utf-8').split('\r\n')
        # read scan data
        for line in lines:
            if line != '':
                (angle, dist_cm, strength) = line.split(',')
                rad = math.radians(int(angle) - self.squint + theta)
                dist = int(dist_cm)*10 + self.offset
                # maximum reliable distance: 6000 mm
                if dist <= 6000:
                    x = xp + (dist * math.cos(rad))
                    y = yp + (dist * math.sin(rad))
                    self.map.append((self.scan_num,x,y))        

        # done
        return True

    def getNumPoints(self):
        return len(self.map)

    def getNumScans(self):
        return self.scan_num
		        
