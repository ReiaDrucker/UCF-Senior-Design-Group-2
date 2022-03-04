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

    // special options for Local Exp
    bool use_gssim_cost = true;
    int max_iters = 10;
    int pm_iters = 5;

    Builder() = default;
    PointCloud build() { return PointCloud(*this); }

    Builder& set_matcher(MatcherType v) { MATCHER = v; return *this; }
    Builder& set_min_disp(int v) { min_disp = v; return *this; }
    Builder& set_max_disp(int v) { max_disp = v; return *this; }
    Builder& set_block_size(int v) { block_size = v; return *this; }
    Builder& set_sigma_color(double v) { sigma_color = v; return *this; }
    Builder& set_use_gssim_cost(bool v) { use_gssim_cost = v; return *this; }
    Builder& set_max_iters(int v) { max_iters = v; return *this; }
    Builder& set_pm_iters(int v) { pm_iters = v; return *this; }

    int num_disp(int alignment = 1) const {
      int ret = max_disp - min_disp + 1;
      return ret % alignment ? ret + alignment - (ret % alignment) : ret;
    }
  } config;

  cv::Mat disparity;
  cv::Mat conf;
  std::array<cv::Mat, 2> vol;

  PointCloud(const Builder& config): config(config) {}

  PointCloud& load_stereo(ImagePair& stereo);

  py::array_t<float> get_disparity();
  py::array_t<float> get_gssim_volume(int idx);

  static void init_pybind(py::module_& m);

private:
  void validateTypes();
};
