#include <opencv2/imgproc.hpp>
#include <opencv2/opencv.hpp>

namespace math {

  static cv::Mat rescale(cv::Mat in, double L) {
    double s = std::min(L / in.cols, L / in.rows);
    cv::Mat ret;
    cv::resize(in, ret, {}, s, s, cv::INTER_LINEAR);
    return ret;
  }

}
