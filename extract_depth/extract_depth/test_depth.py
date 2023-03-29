
import sys
import os

import rclpy 
from rclpy.node import Node
import sensor_msgs.msg as sensor_msgs
from sensor_msgs_py import point_cloud2


import numpy as np

class PCDListener(Node):

    def __init__(self):
        super().__init__('pcd_subsriber_node')


        # Set up a subscription to the 'pcd' topic with a callback to the 
        # function `listener_callback`
        self.pcd_subscriber = self.create_subscription(
            sensor_msgs.PointCloud2,    # Msg type
            '/camera/depth/color/points',  # topic
            self.listener_callback,      # Function to call
            10                          # QoS
        )

                
    def listener_callback(self, msg):
        # Here we convert the 'msg', which is of the type PointCloud2.
        # I ported the function read_points2 from 
        # the ROS1 package. 
        # https://github.com/ros/common_msgs/blob/noetic-devel/sensor_msgs/src/sensor_msgs/point_cloud2.py

        pcd_as_numpy_array = point_cloud2.read_points_numpy(msg, reshape_organized_cloud=True)
        print('pcd_as_numpy_array.shape: ', pcd_as_numpy_array.shape)
        print('pcd_as_numpy_array[0]: ', pcd_as_numpy_array[0])



def main(args=None):
    # Boilerplate code.
    rclpy.init(args=args)
    pcd_listener = PCDListener()
    rclpy.spin(pcd_listener)
    
    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    pcd_listener.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()