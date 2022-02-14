#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/opencv.hpp>

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
}
