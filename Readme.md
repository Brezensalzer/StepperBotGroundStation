# StepperBotGroundStation
Two wheeled rover with stepper motors for precision movement. This is the ground station code of the project. The whole rover is "layered" in three slices:

- the chassis layer: https://github.com/Brezensalzer/StepperBotChassis
- the control layer: https://github.com/Brezensalzer/StepperBotController
- the sensor layer: https://github.com/Brezensalzer/StepperBotLidar2
- the ground station code: https://github.com/Brezensalzer/StepperBotGroundStation

Next steps: Add support for the BreezySLAM library
https://github.com/simondlevy/BreezySLAM

## COAP instead of AMQP
I switched from AMQP (Messaging) to COAP for the communication between the ground station and the rover.
A dedicated AMQP Server (rabbitMQ) is no longer needed as the coap server runs on the beaglebone itself.

