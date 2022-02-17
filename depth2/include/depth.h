#pragma once
#include <opencv2/opencv.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

struct ImagePair;

struct PointCloud {
  cv::Mat disparity;
  cv::Mat conf;

  PointCloud(ImagePair& stereo, int min_disp, int num_disp, int block_size, double sigma_color);

  py::array_t<float> get_confidence();
  py::array_t<int16_t> get_disparity(double thresh = 0);

  static void init_pybind(py::module_& m);

private:
  void validateTypes();
};
