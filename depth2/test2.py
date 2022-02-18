#!/bin/env python3

import cv2 as cv
import open3d as o3d
import numpy as np

from matplotlib import pyplot as plt

disp = np.load('disp.npy')
rgb = cv.imread('rgb.png', cv.IMREAD_GRAYSCALE)

plt.imshow(disp)
plt.show()

def display_cloud(rgb, disparity, focal_length, baseline):
    w, h = rgb.shape[:2]

    effective_focal_length = baseline * focal_length
    disparity = np.ones(disparity.shape) * disparity.max() - disparity
    depth = (np.ones(disparity.shape) / disparity) * effective_focal_length
    depth = depth.clip(0, 255).astype(np.uint8)

    # depth[rgb == 0] = 255
    # rgb[rgb != 0] = 127

    plt.hist(depth.flatten(), bins=20)
    plt.show()

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

    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd, guess, project_valid_depth_only=False)
    pcd.remove_non_finite_points()
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors = 20,
                                            std_ratio = 2.0)

    print(pcd)

    o3d.visualization.draw_geometries([pcd])

display_cloud(rgb, disp, 150, 1)
