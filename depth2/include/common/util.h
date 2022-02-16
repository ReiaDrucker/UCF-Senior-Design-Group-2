#pragma once

#include <tuple>
#include <array>
#include <utility>

#include <Eigen/Dense>
#include <opencv2/core/eigen.hpp>

#include <opencv2/opencv.hpp>
#include <pybind11/numpy.h>

#include <gtsam/geometry/Point2.h>
#include <gtsam/geometry/Point3.h>
#include <gtsam/base/Vector.h>
#include <gtsam/geometry/Pose3.h>
#include <gtsam/geometry/Rot3.h>

namespace py = pybind11;

namespace util {
  namespace detail {
    template <typename T, typename F, size_t... I>
    auto _for_each(T t, F f, std::index_sequence<I...>) {
      return std::array { (std::forward<F>(f))(std::get<I>(t), I)... };
    }
  }

  template <typename T, typename F>
  auto for_each(T t, F f) {
    constexpr int N = std::tuple_size_v<std::decay_t<T>>;
    return detail::_for_each(std::forward<T>(t), std::forward<F>(f), std::make_index_sequence<N>{});
  }

  template <typename T>
  static py::array_t<T> mat_to_array(cv::Mat mat) {
    constexpr int elem_size = sizeof(T);
    return {
      {mat.rows, mat.cols},
      {mat.cols * elem_size, elem_size},
      (T*)mat.ptr()
    };
  }

  template <typename T>
  static cv::Mat filter_mat(cv::Mat m, cv::Mat mask) {
    std::vector<T> out;
    for(int i = 0; i < m.rows; i++) {
      if(mask.at<uchar>(i))
        out.push_back(m.at<T>(i));
    }

    return cv::Mat(out.size(), 1, m.type(), out.data()).clone();
  }

  static auto eigen2cv(auto m) {
    cv::Mat ret;
    cv::eigen2cv(m, ret);
    return ret;
  }

  template <int N, int M = 1>
  static auto& range() {
    static constexpr auto ret = []() {
      std::array<std::array<int, 2>, N * M> ret;
      for(int i = 0, z = 0; i < N; i++)
        for(int j = 0; j < M; j++, z++)
          ret[z] = {i, j};
      return ret;
    }();

    return ret;
  }

  template <typename T, int... dims>
  static auto flatten_mat(auto&& m) {
    return for_each(range<dims...>(), [&](auto&& i, auto) { return m.template at<T>(i[0], i[1]); });
  }

  template <typename T>
  static auto from_tuple(auto&& t) {
    return std::apply([](auto&&... args) { return T(args...); }, t);
  }

  template <typename Out, typename T, int... dims>
  static auto from_mat(const cv::Mat& m) {
    return from_tuple<Out>(flatten_mat<T, dims...>(m));
  }

  template <typename T = float>
  static gtsam::Pose3 gtsam_pose_from_cv(auto&& R, auto&& t) {
    return gtsam::Pose3(from_mat<gtsam::Rot3, T, 3, 3>(R),
                        from_mat<gtsam::Point3, T, 3>(t));
  }

  static std::array<cv::Mat, 2> cv_from_gtsam_pose(gtsam::Pose3 p) {
    auto R = p.rotation().matrix();
    auto t = p.translation().vector();
    return { eigen2cv(R), eigen2cv(t) };
  }
};
