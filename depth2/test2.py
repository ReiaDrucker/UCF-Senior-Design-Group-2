#!/bin/env python3.9

import cv2 as cv
import open3d as o3d
import numpy as np

import math

from matplotlib import pyplot as plt

import argparse

def display_cloud(rgb, disparity, focal_length, inv = -1, eps = 1e-3):
    h, w = rgb.shape[:2]

    if inv > 0:
        disparity = np.ones(disparity.shape) * disparity.max() * inv - disparity
    else:
        disparity = np.ones(disparity.shape) * disparity.min() + disparity

    depth = np.ones(disparity.shape) / disparity
    depth[disparity == 0] = 0
    depth[depth > .3] = 0

    plt.hist(depth.flatten(), bins=20)
    plt.show()

    depth = (depth * 127 / depth[depth != math.inf].max()).astype(np.uint8)

    # depth[rgb == 0] = 255
    # rgb[rgb != 0] = 127

    rgb = o3d.geometry.Image(rgb)
    depth = o3d.geometry.Image(depth)
    rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(rgb, depth, depth_scale=1)

    print(rgbd)
    plt.subplot(1, 2, 1)
    plt.imshow(rgbd.color)
    plt.subplot(1, 2, 2)
    plt.imshow(rgbd.depth)
    plt.show()

    guess = o3d.camera.PinholeCameraIntrinsic(w, h, focal_length, focal_length, w / 2, h / 2)
    print(guess.intrinsic_matrix)
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd, guess, project_valid_depth_only=True)
    pcd.remove_non_finite_points()
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors = 20,
                                            std_ratio = 2.0)
    # pcd.estimate_normals(
    #    search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

    print(pcd)

    o3d.visualization.draw_geometries([pcd])
    o3d.io.write_point_cloud("stereo.pcd", pcd)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display point cloud for computed disparity')

    parser.add_argument('-f', dest='f', type=int, default=300)
    parser.add_argument('--inv', dest='inv', type=float, default=-1)

    disp = np.load('disp.npy')
    rgb = cv.imread('rgb.png', cv.IMREAD_GRAYSCALE)

    args = parser.parse_args()

    display_cloud(rgb, disp, args.f, args.inv)
