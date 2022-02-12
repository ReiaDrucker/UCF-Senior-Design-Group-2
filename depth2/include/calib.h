#pragma once
#include <opencv2/core/matx.hpp>
#include <opencv2/opencv.hpp>
#include <opencv2/sfm.hpp>

#define CERES_FOUND 1
#include <opencv2/sfm/reconstruct.hpp>

#include "matching.h"

struct CameraPose {
  std::array<cv::Mat, 2> R;
  std::array<cv::Mat, 2> t;
  cv::Mat K;
  std::vector<cv::Vec3f> p;

  CameraPose(ImagePair& stereo, double f) {
    K = (cv::Mat_<float>(3, 3) <<
         f, 0, 0,
         0, f, 0,
         0, 0, f);

    auto [u, v] = stereo.get_matches_tuple();

    u = u - cv::Vec2f(stereo.img[0].cols / 2., stereo.img[0].rows / 2.);
    v = v - cv::Vec2f(stereo.img[1].cols / 2., stereo.img[1].rows / 2.);

    cv::sfm::reconstruct(std::array{u, v}, R, t, K, p, true /* is projective */);
  }
};
