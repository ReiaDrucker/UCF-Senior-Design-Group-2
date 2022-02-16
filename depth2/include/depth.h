#pragma once
#include "matching.h"
#include <opencv2/calib3d.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/ximgproc.hpp>

struct PointCloud {
  cv::Mat disparity;
  cv::Mat conf;

  void validateTypes() {
    if(disparity.type() != CV_16SC1
       || conf.type() != CV_32FC1)
      throw runtime_error("Unexpected matrix types");
  }

  PointCloud(ImagePair& stereo, int min_disp, int num_disp, int block_size, double sigma_color) {
    auto matcher = cv::StereoSGBM::create(min_disp,
                                          num_disp,
                                          block_size,
                                          0, // P1
                                          0, // P2
                                          0, // disp12maxDiff
                                          0, // preFilterCap
                                          5, // uniquenessRatio
                                          5, // speckleSize
                                          5  // speckleRange 
                                          );

    matcher->compute(stereo.img[0], stereo.img[1], disparity);

    auto right_matcher = cv::ximgproc::createRightMatcher(matcher);

    cv::Mat right_disparity;
    right_matcher->compute(stereo.img[0], stereo.img[1], right_disparity);

    auto wls_filter = cv::ximgproc::createDisparityWLSFilter(matcher);
    wls_filter->setLambda(8000);
    wls_filter->setSigmaColor(sigma_color);

    wls_filter->filter(disparity, stereo.img[0], disparity, right_disparity);
    conf = wls_filter->getConfidenceMap();

    validateTypes();
  }

  auto get_confidence() {
    return util::mat_to_array<float>(conf);
  }

  auto get_disparity(double thresh = 0) {
    cv::Mat mask;
    cv::threshold(conf, mask, thresh-1, 2, cv::THRESH_BINARY);

    mask.convertTo(mask, CV_8UC1);

    auto ret = cv::Mat(disparity.size[0], disparity.size[1], disparity.type(), std::numeric_limits<int16_t>::min());
    disparity.copyTo(ret, mask);

    return util::mat_to_array<int16_t>(ret);
  }
};
