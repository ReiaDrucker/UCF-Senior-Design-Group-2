#pragma once
#include <opencv2/opencv.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

struct ImagePair;

struct PointCloud {
  enum class MatcherType {
    SGBM,
    LOCAL_EXP
  };

  const struct Builder {
    MatcherType MATCHER = MatcherType::LOCAL_EXP;
    int min_disp = 0;
    int max_disp = 10;

    // special options for SGBM
    int block_size = 3;
    double sigma_color = 1.0;

    Builder() = default;
    PointCloud build() { return PointCloud(*this); }

    Builder& set_matcher(MatcherType v) { MATCHER = v; return *this; }
    Builder& set_min_disp(int v) { min_disp = v; return *this; }
    Builder& set_max_disp(int v) { max_disp = v; return *this; }
    Builder& set_block_size(int v) { block_size = v; return *this; }
    Builder& set_sigma_color(double v) { sigma_color = v; return *this; }

    int num_disp(int alignment = 1) const {
      int ret = max_disp - min_disp + 1;
      return ret % alignment ? ret + alignment - (ret % alignment) : ret;
    }
  } config;

  cv::Mat disparity;
  cv::Mat conf;

  PointCloud(const Builder& config): config(config) {}

  PointCloud& load_stereo(ImagePair& stereo);

  py::array_t<float> get_disparity();

  static void init_pybind(py::module_& m);

private:
  void validateTypes();
};
