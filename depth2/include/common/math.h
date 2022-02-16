#pragma once

#include <opencv2/calib3d.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/opencv.hpp>

#include "util.h"

namespace math {
  static cv::Mat rescale(cv::Mat in, double L) {
    double s = std::min(L / in.cols, L / in.rows);
    cv::Mat ret;
    cv::resize(in, ret, {}, s, s, cv::INTER_LINEAR);
    return ret;
  }

  static cv::Mat construct_proj_mat(auto R, auto t, auto K) {
    cv::Mat RT;
    cv::hconcat(R.t(), -R.t()*t, RT);

    return K * RT;
  }

  static auto focal_from_fov(auto size, auto fov) {
    auto L = sqrt(size[0] * size[1] * 1.0F);
    return (L / 2) / tan(fov / 2);
  }

  static auto angle(auto a, auto b) {
    auto v = a[0] * b[1] - a[1] * b[0];
    auto m1 = a[0] * a[0] + a[1] * a[1];
    auto m2 = b[0] * b[0] + b[1] * b[1];
    return asin(v / sqrt(m1 * m2));
  }

  static std::tuple<std::array<cv::Mat, 2>, cv::Size>
  get_optimal_homography(const std::array<cv::Mat, 2>& H, const std::array<cv::MatSize, 2>& s) {
    double x0, x1, y0, y1;
    x0 = x1 = y0 = y1 = 0;

    util::for_each(s, [&](auto&& s, auto i) {
      cv::Matx34d corners(0, s[1], 0, s[1],
                          0, 0, s[0], s[0],
                          1, 1, 1, 1);

      corners = cv::Mat(H[i] * corners);

      for(int i = 0; i < 4; i++) {
        corners(0, i) /= corners(2, i);
        corners(1, i) /= corners(2, i);
        x0 = min(x0, corners(0, i));
        x1 = max(x1, corners(0, i));
        y0 = min(y0, corners(1, i));
        y1 = max(y1, corners(1, i));
      }

      return 0;
    });

    double scale = max((x1 - x0) / s[0][0], (y1 - y0) / s[0][1]);

    cv::Matx33d T(1, 0, -x0,
                  0, 1, -y0,
                  0, 0, scale);

    auto h_ = util::for_each(H, [&](auto&& H, auto) {
      return cv::Mat(T * H);
    });

    cv::Size size((x1 - x0) / scale, (y1 - y0) / scale);
    std::cout << s[1] << " " << size << std::endl;

    return {h_, size};
  }

  static cv::Mat warp_points(const cv::Mat& pts, const cv::Mat& H) {
    cv::Mat ret;
    cv::convertPointsToHomogeneous(pts, ret);

    ret = ret.reshape(1).t();
    ret.convertTo(ret, H.type());
    ret = H * ret;

    ret = ret.t();
    cv::convertPointsFromHomogeneous(ret, ret);

    ret.convertTo(ret, pts.type());
    return ret;
  }
}

