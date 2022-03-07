#pragma once

#include <array>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include <opencv2/opencv.hpp>
#include <common/util.h>

namespace py = pybind11;

struct CameraPose;

struct ImagePair {
  using Detector = cv::ORB; // TODO: move to config, and eat dynamic polymorphism cost :/
  using array_t = py::array_t<uint8_t, py::array::c_style | py::array::forcecast>;

  const struct Builder {
    int TARGET_SCALE = 500;
    int N_FEATURES = 1e5;
    double RATIO = .75;

    Builder() = default;
    ImagePair build() { return ImagePair(*this); }

    Builder& set_target_scale(int v) { TARGET_SCALE = v; return *this; }
    Builder& set_feature_count(int v) { N_FEATURES = v; return *this; }
    Builder& set_test_ratio(double v) { RATIO = v; return *this; }
  } config;

  ImagePair(const Builder& config): config(config) {}
  ImagePair(const ImagePair& o):
    config(o.config),
    img(util::for_each(o.img, [](auto&& img, auto) { return img.clone(); })),
    mask(o.mask.clone()),
    matches(o.matches) {}

  std::array<cv::Mat, 2> img;
  cv::Mat mask;
  std::vector<std::array<cv::Point2f, 2>> matches;

  ImagePair& load_images(array_t left, array_t right);
  ImagePair& fill_matches();
  ImagePair& rectify(CameraPose& pose);

  auto get_image(int idx);
  auto get_matches();

  cv::Mat get_matches_mat(int idx);
  std::array<cv::Mat, 2> get_matches_tuple();

  static void init_pybind(py::module_& m);
};
