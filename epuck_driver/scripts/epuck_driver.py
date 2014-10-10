#!/usr/bin/env python

import sys
sys.path.append("../src/")

import rospy
from geometry_msgs.msg import Twist

from ePuck import ePuck

CAMERA_ZOOM = 8
# Wheel Radio (cm)
R = 4
# Separation between wheels (cm)
B = 5.3

class EPuckDriver(object):

    def __init__(self, epuck_name, epuck_address):
        self._bridge = ePuck(epuck_address, False)
        self._bridge.enable(
            'accelerometer'
            'camera',
            'motor_position',
            'proximity',
        )

        self._bridge.set_camera_parameters('RGB_365', 40, 40, CAMERA_ZOOM)

        self._name = epuck_name

    def greeting(self):
        self._bridge.set_front_led(1)
        self._bridge.set_body_led(1)

    def disconnect(self):
        self._bridge.close()

    def connect(self):
        self._bridge.connect()

    def run(self):
        # Connect with the ePuck
        self.connect()
        # Disconnect when rospy is going to down
        rospy.on_shutdown(self.disconnect)

        self.greeting()

        self._bridge.step()

        # Subscribe to Commando Velocity Topic
        rospy.Subscriber("mobile_base/cmd_vel", Twist, self.handler_velocity)

        # Sensor Publishers
        # rospy.Publisher("/%s/mobile_base/" % self._name, )

        # Spin almost forever
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            self._bridge.step()
            self.update_sensors()

            rate.sleep()

    def update_sensors(self):
        pass

    def handler_velocity(self, data):
        linear = data.linear.x
        angular = data.angular.z

        wl = (linear - (B / 2.) * angular) / R
        wr = (linear + (B / 2.) * angular) / R

        left_vel = wl * 1000.
        right_vel = wr * 1000.

        print left_vel
        print right_vel

        self._bridge.set_motors_speed(left_vel, right_vel)

def run():
    rospy.init_node("epuck_drive", anonymous=True)

    epuck_address = rospy.get_param("~epuck_address")
    epuck_name = rospy.get_param("~epuck_name", "epuck")

    EPuckDriver(epuck_name, epuck_address).run()

if __name__ == "__main__":
    run()
