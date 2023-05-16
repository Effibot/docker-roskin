#!/home/dock/venvs/py27/bin/python

"""Naoqi Laser Listener and Republisher
        /naoqi_driver/laser publishes a laserscan message with 60 ranges, 0,0698132 (4 degrees) radians between each range.
        The first range is -0,523599 radians (-30 degrees), the last is at 3,83972 radians (220 degrees).
        Every 15 ranges a gap of eight '-1' values are inserted to simulate the void between the three laserscanners.
        The first 15 ranges are the right laserscanner, the next 15 are the front laserscanner and the last 15 are the left laserscanner.
        Ranges are in meters.
        We are exploiting the fact that the driver publishes the ranges after a transformation to the base_footprint frame, so we don't have to do it.
"""

import argparse

from numpy import linspace
import rospy
import numpy as np
from sensor_msgs.msg import LaserScan

class laser_listener():

    def __init__(self, factor = 2, use_center = False, rate = 10):
        self.angle_min = -0.523599 # -30 degrees in radians
        self.right_angle_max = 0.523599 # 30 degrees in radians
        self.center_angle_min = 1.0472 # 60 degrees in radians
        self.center_angle_max = 2.0944 # 120 degrees in radians
        self.left_angle_min = 2.61799 # 150 degrees in radians
        self.angle_max = 3.66519 # 210 degrees in radians
        self.angle_increment = 0.0698132 # 4 degrees in radians
        self.factor = factor
        rospy.Subscriber("/naoqi_driver/laser",LaserScan, self.listen_callback)
        self.pub = rospy.Publisher("/laser_expander",LaserScan, queue_size=10)
        rospy.init_node("laser_expander")
        self.rate = rospy.Rate(rate)
        self.use_center = use_center

    def listen_callback(self,msg):
        # get the ranges from the laserscanner
        scan_data = np.array(msg.ranges)
        right_scan = scan_data[0:15]
        #rospy.loginfo("Right Scan: (%d): %s", len(right_scan), right_scan)
        right_void = scan_data[15:23]
        #rospy.loginfo("Right Void (%d): %s", len(right_void), right_void)
        center_scan = scan_data[23:38]
        #rospy.loginfo("Center Scan (%d): %s", len(center_scan), center_scan)
        left_void = scan_data[38:46] # useless
        #rospy.loginfo("Left Void (%d): %s", len(left_void), left_void)
        left_scan = scan_data[46:]
        #rospy.loginfo("Left Scan: (%d): %s", len(left_scan), left_scan)

        # expand the scan to get a higher resolution
        expanded_right_scan = self.expand_scan(right_scan, self.factor, self.angle_min, self.right_angle_max)
        #rospy.loginfo("Expanded Right Scan (%d): %s\n", len(expanded_right_scan), expanded_right_scan)
        expanded_rigth_void = -1*np.ones(self.factor*len(right_void)-1)
        expanded_center_scan = self.expand_scan(center_scan, self.factor, self.center_angle_min, self.center_angle_max)
        expanded_left_void = expanded_rigth_void
        expanded_left_scan = self.expand_scan(left_scan, self.factor, self.left_angle_min, self.angle_max)

        #rospy.loginfo("Expanded Left Scan (%d): %s\n", len(expanded_left_scan), expanded_left_scan)
        expanded_msg = msg

        # concatenate the expanded scans
        if self.use_center:
            expanded_scan = expanded_center_scan
            expanded_msg.angle_min = self.center_angle_min
            expanded_msg.angle_max = self.center_angle_max
        else:
            expanded_scan = np.concatenate((expanded_right_scan, expanded_rigth_void, expanded_center_scan, expanded_left_void, expanded_left_scan))
        #rospy.loginfo("Expanded Scan (%d): %s\n", len(expanded_scan), expanded_scan)

        # re-publish the expanded scan with /naoqi_driver/laser message's header
        expanded_msg.angle_increment = msg.angle_increment/self.factor
        expanded_msg.ranges = expanded_scan
        self.pub.publish(expanded_msg)

    def min_interpolation(self, scan, scan_length, factor):
        expanded_scan = np.zeros(factor*scan_length)
        expanded_scan[0] = scan[0]
        expanded_scan[-1] = scan[-1]
        for i in range(1, scan_length):
            # pre-fill the expanded scan with the true scan points
            expanded_scan[i*factor] = scan[i]
            rho = min(scan[i-1], scan[i])
            start = i*factor - factor + 1
            end = i*factor+1
            expanded_scan[start:end] = [rho for j in range(factor)]
        return expanded_scan

    def mid_interpolation(self, scan, scan_length, angle_span, factor):
        expanded_scan = np.zeros(factor*scan_length-1)
        expanded_scan[0] = scan[0]
        expanded_scan[-1] = scan[-1]
        for i in range(1, scan_length):
            # get previous and current scan point x,y coordinates
            pred = [scan[i-1]*np.cos(angle_span[i-1]),scan[i-1]*np.sin(angle_span[i-1])]
            curr = [scan[i]*np.cos(angle_span[i]),scan[i]*np.sin(angle_span[i])]
            # get the midpoint between the previous and current scan point
            mid = [(pred[0]+curr[0])/2, (pred[1]+curr[1])/2]
            # pre-fill the expanded scan with the true scan points
            expanded_scan[i*factor] = scan[i]
            # now expand
            #line = self.linear_interpolation(pred, mid, factor)
            for j in range(1,factor):
                # fill the expanded scan with the expanded scan points
                #expanded_scan[(i-1)*factor+j] = np.sqrt(line[j][0]**2 + line[j][1]**2)
                expanded_scan[(i-1)*factor+j] = np.sqrt(mid[0]**2 + mid[1]**2)
        return expanded_scan
    
    def expand_scan(self, scan, factor, angle_start, angle_end):
        scan_length = len(scan) # 15
        # pre-fill the expanded scan with the true scan points
        angle_span = [angle_start + i*self.angle_increment for i in range(scan_length)]
        angle_span_fitted = [angle_start + i*self.angle_increment/factor for i in range(factor*scan_length-1)]
        expanded_scan = self.min_interpolation(scan, scan_length, factor)
        return expanded_scan
    
if __name__ =='__main__':
    factor = rospy.get_param("/laser_expander/expand_factor")
    center = rospy.get_param("/laser_expander/use_center")
    listener = laser_listener(factor=factor, use_center=center)
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting Down")
