#pragma once
#include <iostream>

#include <opencv2/core/hal/interface.h>
#include <opencv2/core/matx.hpp>
#include <opencv2/opencv.hpp>
#include <opencv2/sfm.hpp>

#define CERES_FOUND 1
#include <opencv2/sfm/reconstruct.hpp>

#include "matching.h"

struct CameraPose {
  cv::Matx33d K;
  std::vector<cv::Mat> R;
  std::vector<cv::Mat> t;
  std::vector<cv::Mat> p;

  CameraPose(ImagePair& stereo, double f) {
    K = cv::Matx33d(f, 0, 0,
                    0, f, 0,
                    0, 0, f);

    auto pts = stereo.get_matches_tuple();
    for(int i = 0; i < 2; i++) {
      pts[i] = pts[i] - cv::Scalar(stereo.img[i].cols / 2., stereo.img[i].rows / 2.);
      pts[i] = pts[i].reshape(1).t();
      pts[i].convertTo(pts[i], CV_64FC1);
    }

    std::cout << pts[0].size << std::endl;

    cv::sfm::reconstruct(pts, R, t, K, p, true /* is projective */);

    std::cout << R.size() << std::endl;
    std::cout << R[0].size << std::endl;
  }

  
};
