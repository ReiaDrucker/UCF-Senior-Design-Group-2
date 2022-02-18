#pragma once
#include <iostream>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include <opencv2/opencv.hpp>

struct ImagePair;

namespace py = pybind11;

struct CameraPose {
  double f;
  double skew;
  std::array<cv::Mat, 2> pts;
  std::array<cv::Mat, 2> R;
  std::array<cv::Mat, 2> t;
  cv::Mat p;

  std::array<cv::Scalar, 2> center;

  double e1, e2;

  CameraPose(ImagePair& stereo, double fov);

  void refine();
  std::array<cv::Mat, 2> rectify(const std::array<cv::Mat, 2>& img, cv::Mat& mask);

  py::array_t<float> get_matches();
  friend std::ostream& operator<<(std::ostream& os, const CameraPose& pose);

  static void init_pybind(py::module_& m);

private:
  void validateTypes();
};
