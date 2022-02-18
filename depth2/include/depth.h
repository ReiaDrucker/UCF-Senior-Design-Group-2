#pragma once
#include <opencv2/opencv.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

struct ImagePair;

struct PointCloud {
  cv::Mat disparity;
  cv::Mat conf;

  enum class MatcherType {
    SGBM,
    LOCAL_EXP
  };

  static constexpr auto MATCHER = MatcherType::LOCAL_EXP;

  PointCloud(ImagePair& stereo, int min_disp, int num_disp, int block_size, double sigma_color);

  py::array_t<float> get_disparity();

  static void init_pybind(py::module_& m);

private:
  void validateTypes();
};
