# robotPosition.py
# Class for tracking a robot's position
#
import math
import pika
import uuid

#------------------------------------
# setup message queueing
#------------------------------------
class stepperRpcClient(object):
    def __init__(self, hostname, user, passwd):
        self.cred = pika.PlainCredentials(user, passwd)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=hostname,credentials=self.cred))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='stepper_queue',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=n.encode('utf-8'))
        while self.response is None:
            self.connection.process_data_events()
        return self.response

#------------------------------------
# Drive a robot
#------------------------------------
class robotPosition:
    'Class for tracking a robot\'s position'

    def __init__(self):
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
        # initialize message queueing
        self.stepperRpc = stepperRpcClient('x200.modellmarine.de','x200','bone')
        # calibration, todo...
        rc = self.stepperRpc.call('t102.5#').decode('utf-8')

    def getInfo(self):
        return self.stepperRpc.call('i#').decode('utf-8')
		
    def getPosition(self):
        return (self.x, self.y, self.theta_deg, self.theta_rad)

    def powerOn(self):
        self.stepperRpc.call('e#').decode('utf-8')
		
    def powerOff(self):
        self.stepperRpc.call('d#').decode('utf-8')
		
    def setPosition(self, distance, angle):
        # distance in [mm]
        # angle in degrees
        # angle < 0: turn left
        # angle > 0: turn right
        
        # drive
        if distance > 0:  # forward
            cmd = 'f' + str(distance) + '#'
            self.stepperRpc.call(cmd).decode('utf-8')
        if distance < 0:  # backward
            cmd = 'b' + str(abs(distance)) + '#'
            self.stepperRpc.call(cmd).decode('utf-8')

        # turn
        if angle > 0:     # turn left
            cmd = 'l' + str(angle) + '#'
            self.stepperRpc.call(cmd).decode('utf-8')
        if angle < 0:     # turn right
            cmd = 'r' + str(abs(angle)) + '#'
            self.stepperRpc.call(cmd).decode('utf-8')
	            
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

