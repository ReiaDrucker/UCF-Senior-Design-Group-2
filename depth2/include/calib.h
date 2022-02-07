#pragma once

#include <opencv2/core/matx.hpp>
#include <opencv2/opencv.hpp>

#include "matching.h"

struct CameraPose {
  std::vector<cv::Mat> K;
  std::vector<cv::Mat> R;
  std::vector<cv::Mat> t;
  std::vector<cv::Mat> dist;
  std::vector<cv::Mat> matches;

  static CameraPose from_images(ImagePair& stereo, double f) {
    cv::Mat K = (cv::Mat_<float>(3, 3) <<
                 f, 0, 0,
                 0, f, 0,
                 0, 0, f);
    
    auto [u, v] = stereo.get_matches_tuple();

    // TODO: center the points to make K the same

    auto E = cv::findEssentialMat(u, v, K, cv::LMEDS);

    cv::Mat R, t;
    cv::recoverPose(E, u, v, R, t);

    auto z3 = cv::Mat::zeros(3, 1, CV_32FC1);
    auto z5 = cv::Mat::zeros(5, 1, CV_32FC1);

    return CameraPose {
      .K = { K, K },
      .R = { cv::Mat::eye(3, 3, CV_32FC1), R },
      .t = { z3, t },
      .dist = { z5, z5 },
      .matches = { u, v }
    };
  }

  CameraPose& bundle_adjustment() {
    

    return *this;
  }
};

// TODO: https://www.uco.es/investiga/grupos/ava/node/39
