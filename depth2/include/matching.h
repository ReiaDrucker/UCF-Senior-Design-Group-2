#pragma once

#include <array>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include <opencv2/opencv.hpp>

namespace py = pybind11;

struct CameraPose;

struct ImagePair {
  static constexpr int N_FEATURES = 1e5;
  static constexpr double RATIO = .75;
  static constexpr int TARGET_SCALE = 500;
  using Detector = cv::ORB;
  using array_t = py::array_t<uint8_t, py::array::c_style | py::array::forcecast>;

  std::array<cv::Mat, 2> img;
  cv::Mat mask;
  std::vector<std::array<cv::Point2f, 2>> matches;

  ImagePair(array_t left, array_t right);

  ImagePair& fill_matches();
  ImagePair& rectify(CameraPose& pose);

  auto get_image(int idx);
  auto get_matches();

  cv::Mat get_matches_mat(int idx);
  std::array<cv::Mat, 2> get_matches_tuple();

  static void init_pybind(py::module_& m);
};
