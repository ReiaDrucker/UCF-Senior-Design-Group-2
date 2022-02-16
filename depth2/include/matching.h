#pragma once

#include <array>
#include <opencv2/features2d.hpp>
#include <vector>

#include <opencv2/opencv.hpp>
#include <opencv2/xfeatures2d.hpp>

#include <pybind11/numpy.h>

#include <common/util.h>
#include <common/math.h>

namespace py = pybind11;

struct ImagePair {
  static constexpr int N_FEATURES = 1e5;
  static constexpr double RATIO = .75;
  static constexpr int TARGET_SCALE = 500;
  using Detector = cv::ORB;

  std::array<cv::Mat, 2> img;
  cv::Mat left2;
  std::vector<std::array<cv::Point2f, 2>> matches;

  using array_t = py::array_t<uint8_t, py::array::c_style | py::array::forcecast>;
  ImagePair(array_t left, array_t right) {
    img[0] = cv::Mat(left.shape(0), left.shape(1), CV_8UC1, (uint8_t*)left.data()).clone();
    img[1] = cv::Mat(right.shape(0), right.shape(1), CV_8UC1, (uint8_t*)right.data()).clone();

    img[0] = math::rescale(img[0], TARGET_SCALE);
    img[1] = math::rescale(img[1], TARGET_SCALE);

    left2 = img[0];
  }

  ImagePair& fill_matches() {
    struct kp_and_matches {
      std::vector<cv::KeyPoint> kp;
      cv::Mat des;
    };

    auto detector = Detector::create(N_FEATURES);
    auto features = util::for_each(img, [&](auto&& img, auto) {
      kp_and_matches ret;

      detector->detect(img, ret.kp);
      detector->compute(img, ret.kp, ret.des);

      return ret;
    });

    std::vector<std::vector<cv::DMatch>> matches_;
    auto matcher = cv::BFMatcher(detector->defaultNorm());
    matcher.knnMatch(features[0].des, features[1].des, matches_, 2);

    matches.reserve(matches_.size());
    for(auto p: matches_) {
      if(p[0].distance < RATIO * p[1].distance) {
        auto& u = features[0].kp[p[0].queryIdx].pt;
        auto& v = features[1].kp[p[0].trainIdx].pt;
        matches.push_back({ u, v });
      }
    }

    return *this;
  }

  ImagePair& rectify(auto& pose) {
    img = pose.rectify(img);
    return *this;
  }

  auto get_image(int idx) {
    return util::mat_to_array<uint8_t>(img[idx]);
  }

  auto get_matches() {
    static constexpr int elem_sz = sizeof(float);
    return py::array_t<float>({(int)matches.size(), 2, 2},
                              {2 * 2 * elem_sz, 2 * elem_sz, elem_sz},
                              (float*)matches.data());
  }

  cv::Mat get_matches_mat(int idx) {
    using vec = cv::Vec2f;
    return cv::Mat(matches.size(), 1, CV_32FC2, (vec*)matches.data() + idx, 2 * sizeof(vec));
  }

  auto get_matches_tuple() {
    return std::array<cv::Mat, 2> {
      get_matches_mat(0),
      get_matches_mat(1)
    };
  }
};
