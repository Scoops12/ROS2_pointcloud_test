
import sys
import os
import time
import array
from typing import Iterable, List, NamedTuple, Optional

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
            '/world/default/model/mrb3s/link/realsense_d435/Base/sensor/realsense_d435/points', #topic
            # '/camera/depth/color/points',  # topic
            self.pointcloud_callback,      # Function to call
            10                          # QoS
        )

                
    def pointcloud_callback(self, msg):
        # Here we convert the 'msg', which is of the type PointCloud2.
        # I ported the function read_points2 from 
        # the ROS1 package. 
        # https://github.com/ros/common_msgs/blob/noetic-devel/sensor_msgs/src/sensor_msgs/point_cloud2.py

        # Define u,v for depth point to pull.
        # u and v origin is in top left of image.
        # u - moves to the right (defines column)
        # v - moves downwards (defines row)
        u = 120
        v = 6
        start_ind = u*msg.point_step + v*msg.row_step
        my_data = msg.data[start_ind:start_ind+msg.point_step]

        u = 130
        v = 6
        start_ind = u*msg.point_step + v*msg.row_step
        my_data2 = msg.data[start_ind:start_ind+msg.point_step]

        all_my_data = my_data + my_data2

        # my_point = point_cloud2.read_points(msg, uvs=[0,1,2,3,4,5], field_names = ("x", "y", "z"))
        my_point = np.ndarray(
            shape=(2, ),
            dtype=point_cloud2.dtype_from_fields(msg.fields, point_step=msg.point_step),
            buffer=all_my_data)

        # # Used to generate test file
        # temp = np.ndarray(
        #     shape=(msg.width, msg.height, ),
        #     dtype=point_cloud2.dtype_from_fields(msg.fields, point_step=msg.point_step),
        #     buffer=None)
        # for u in range(msg.width):
        #     for v in range(msg.height):
        #         start_ind = u*msg.point_step + v*msg.row_step
        #         my_data = msg.data[start_ind:start_ind+msg.point_step]

        #         my_point = np.ndarray(
        #             shape=(1, ),
        #             dtype=point_cloud2.dtype_from_fields(msg.fields, point_step=msg.point_step),
        #             buffer=my_data)
                
        #         # print(type(my_point))

        #         temp[u,v] = my_point
        
        # np.save('numpy_mat.npy', temp)
        
        # Test read_points_efficient
        uvs = [(50, 6), (130, 6)]
        time1 = time.time()
        my_points = self.read_points_efficient(msg, uvs=uvs, field_names = ("x", "y", "z"))
        time2 = time.time()
        print('efficient: ', time2 - time1)
        print('my_points: ', my_points)

        time1 = time.time()
        my_points_before = point_cloud2.read_points(msg, uvs=range(8), field_names = ("x", "y", "z"))
        time2 = time.time()
        print('shit approach: ', time2 - time1)
        print('my_points_before: ', my_points_before)

        # Inefficient and wrong way of converting entire pointcloud into numpy array
        time1 = time.time()
        pcd_as_numpy_array = point_cloud2.read_points_numpy(msg, reshape_organized_cloud=True)
        time2 = time.time()
        print('super_shit approach: ', time2 - time1)
        print('pcd_as_numpy_array.shape: ', pcd_as_numpy_array.shape)
        # print('pcd_as_numpy_array['+str(u)+','+str(v)+']: ', pcd_as_numpy_array[u,v])

    def read_points_efficient(
        self,
        cloud: sensor_msgs.PointCloud2,
        field_names: Optional[List[str]] = None,
        uvs: Optional[Iterable] = None) -> np.ndarray:

        assert isinstance(cloud, sensor_msgs.PointCloud2), \
            'Cloud is not a sensor_msgs.PointCloud2'        

        # Grab only the data you want
        if uvs is not None:
            select_data = array.array('B', [])

            # Loop through all provided pixel locations
            for u,v in uvs:
                start_ind = u*cloud.point_step + v*cloud.row_step
                curr_data = cloud.data[start_ind:start_ind+cloud.point_step]

                select_data += curr_data
            points_len = len(uvs)
        else:
            select_data = cloud.data
            points_len = cloud.width * cloud.height

        # Cast bytes to numpy array
        points = np.ndarray(
            shape=(points_len, ),
            dtype=point_cloud2.dtype_from_fields(cloud.fields, point_step=cloud.point_step),
            buffer=select_data)
        
        # Keep only the requested fields
        if field_names is not None:
            assert all(field_name in points.dtype.names for field_name in field_names), \
                'Requests field is not in the fields of the PointCloud!'
            # Mask fields
            points = points[list(field_names)]

        return points


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