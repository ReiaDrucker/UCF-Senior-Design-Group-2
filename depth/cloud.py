from matching import ImageWithFeatures, remove_match_outliers
from disparity import disparity_uncalibrated
import cv2 as cv
import numpy as np
import random
import math

import open3d as o3d

if __name__ == '__main__':
    left = ImageWithFeatures(cv.imread('../data/left.tif', cv.IMREAD_GRAYSCALE), 1024, 0, -3.5)
    right = ImageWithFeatures(cv.imread('../data/right.tif', cv.IMREAD_GRAYSCALE), 1024)

    disparity = disparity_uncalibrated(left, right)
    h, w = disparity.shape

    baseline = .55
    focal_length = 1000 / baseline
    effective_focal_length = baseline * focal_length
    depth = (np.ones(disparity.shape) / disparity) * effective_focal_length
    depth = depth.clip(0, 1000)

    rgb = o3d.geometry.Image(left.img)
    depth = o3d.geometry.Image(np.float32(depth))
    rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(rgb, depth, depth_scale=1)

    guess = o3d.camera.PinholeCameraIntrinsic(w, h, focal_length, focal_length, w / 2, h / 2)
    print(guess.intrinsic_matrix)

    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd, guess)
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors = 20,
                                            std_ratio = 2.0)

    o3d.visualization.draw_geometries([pcd])
