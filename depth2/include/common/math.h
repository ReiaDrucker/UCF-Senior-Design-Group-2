#pragma once

#include <array>

#include <limits>
#include <opencv2/calib3d.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/opencv.hpp>

#include "util.h"

namespace math {
  static cv::Mat rescale(cv::Mat in, double L) {
    double s = std::max(L / in.cols, L / in.rows);
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

    auto h_ = util::for_each(H, [&](auto&& H, auto k) {
      cv::Mat ret(T * H);

      int h = s[k][0], w = s[k][1];
      cv::Matx34d mid(w / 2., w, w / 2., 0,
                      0, h / 2., h, h / 2.,
                      1, 1, 1, 1);

      cv::Mat mid_ = cv::Mat((ret * mid).t()).reshape(3);

      cv::convertPointsFromHomogeneous(mid_, mid_);

      auto x = mid_.at<cv::Vec2d>(1) - mid_.at<cv::Vec2d>(3);
      auto y = mid_.at<cv::Vec2d>(2) - mid_.at<cv::Vec2d>(0);

      auto k1 = (h*h*x[1]*x[1] + w*w*y[1]*y[1]) / (h*w*(x[1]*y[0] - x[0]*y[1]));
      auto k2 = (h*h*x[0]*x[1] + w*w*y[0]*y[1]) / (h*w*(x[0]*y[1] - x[1]*y[0]));

      if(k1 < 0) {
        k1 = -k1;
        k2 = -k2;
      }

      cv::Matx33d S(k1, k2, 0,
                    0, 1, 0,
                    0, 0, 1);

      std::cout << k1 << " " << k2 << std::endl;

      return cv::Mat(S * ret);
    });

    cv::Size size((x1 - x0) / scale, (y1 - y0) / scale);

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

  static void fill_out_of_view(cv::Mat& volume, int mode, int margin = 0) {
    int D = volume.size.p[0];
    int H = volume.size.p[1];
    int W = volume.size.p[2];

    if (mode == 0) {
      for (int d = 0; d < D; d++) {
        for (int y = 0; y < H; y++) {
          auto p = volume.ptr<float>(d, y);
          auto q = p + d + margin;
          float v = *q;
          while (p != q){
            *p = v;
            p++;
          }
        }
      }
    } else {
      for (int d = 0; d < D; d++) {
        for (int y = 0; y < H; y++) {
          auto q = volume.ptr<float>(d, y) + W;
          auto p = q - d - margin;
          float v = p[-1];
          while (p != q){
            *p = v;
            p++;
          }
        }
      }
    }
  }

  // Source: Structural Similarity Measurement Based Cost Function for Stereo Matching of Automotive Applications
  static float gssim(const std::array<cv::Mat, 4>& p, float alpha, float beta, float gamma, float eps) {
    int h = p[0].rows, w = p[0].cols;
    int N = w * h - 1;

    auto mean = util::for_each(p, [](auto&& p, auto) { return cv::mean(p)[0]; });
    auto var = util::for_each(p, [&](auto&& p, auto k) {
      float ret = 0;
      for(int u = 0; u < h; u++) {
        for(int v = 0; v < w; v++) {
          float x = (p.template at<float>(u, v) - mean[k]);
          ret += x * x;
        }
      }

      return ret / N;
    });

    // luminence, contrast, structure
    float l = 0, c = 0, s = 0;
    for(int i = 0; i < 2; i++) {
      for(int j = 2; j < 4; j++) {
        l += (2 * mean[i] * mean[j] + eps) / (mean[i] * mean[i] + mean[j] * mean[j] + eps);

        c += (2 * sqrt(var[i]) * sqrt(var[j]) + eps) / (var[i] + var[j] + eps);

        float covar = 0;
        for(int u = 0; u < h; u++) {
          for(int v = 0; v < w; v++) {
            covar += (p[i].template at<float>(u, v) - mean[i]) * (p[j].template at<float>(u, v) - mean[j]);
          }
        }

        covar /= N;

        s += (covar + eps) / (sqrt(var[i]) * sqrt(var[j]) + eps);
      }
    }

    return pow(l, alpha) * pow(c, beta) * pow(s, gamma);
  }

  static cv::Mat gssim_volume(const std::array<cv::Mat, 2>& p, int ndisp, int patch_size = 7,
                              float alpha = 0.9, float beta = 0.1, float gamma = 0.2, float eps = .001) {
    int h = p[0].rows, w = p[0].cols;
    auto sizes = std::array { ndisp, h, w };

    int pad = patch_size / 2;

    std::array<cv::Mat, 4> g;
    for(int k = 0; k < 2; k++) {
      for(int dir = 0; dir < 2; dir++) {
        int idx = k * 2 + dir;
        g[idx] = cv::Mat_<float>(h + 2 * pad, w + 2 * pad, 0.);
        cv::Sobel(p[k], g[idx](cv::Rect(pad, pad, w, h)), CV_32F, dir == 0, dir == 1);
      }
    }

    cv::Mat ret = cv::Mat::zeros(sizes.size(), sizes.data(), CV_32FC1);

    std::vector<float> mx(ndisp);

    #pragma omp parallel for
    for(int d = 0; d < ndisp; d++) {
      for(int u = 0; u < h; u++) {
        for(int v = 0; v < w; v++) {
          int v2 = v - d;
          if(v2 < 0) continue;

          std::array<cv::Mat, 4> p;

          for(int k = 0; k < 2; k++) {
            for(int dir = 0; dir < 2; dir++) {
              int idx = k * 2 + dir;
              int V = k ? v2 : v;
              p[idx] = g[idx](cv::Rect(V, u, patch_size, patch_size));
            }
          }

          mx[d] = max(mx[d],
                   ret.at<float>(d, u, v) = gssim(p, alpha, beta, gamma, eps));
        }
      }
    }

    ret = *std::max_element(mx.begin(), mx.end()) - ret;

    fill_out_of_view(ret, 0);
    return ret;
  }

  // borrowed from LocalExpansionStereo
  static cv::Mat volume_l2r(cv::Mat& volSrc, int margin = 0) {
    int D = volSrc.size[0];
    int H = volSrc.size[1];
    int W = volSrc.size[2];
    cv::Mat volDst = volSrc.clone();

    for (int d = 0; d < D; d++) {
      cv::Mat_<float> s0(H, W, volSrc.ptr<float>() + H*W*d);
      cv::Mat_<float> s1(H, W, volDst.ptr<float>() + H*W*d);
      s0(cv::Rect(d, 0, W - d, H)).copyTo(s1(cv::Rect(0, 0, W - d, H)));

      cv::Mat edge1 = s0(cv::Rect(W - 1 - margin, 0, 1, H)).clone();
      cv::Mat edge0 = s0(cv::Rect(d + margin, 0, 1, H)).clone();
      for (int x = W - 1 - d - margin; x < W; x++)
        edge1.copyTo(s1.col(x));
      for (int x = 0; x < margin; x++)
        edge0.copyTo(s1.col(x));
    }

    fill_out_of_view(volDst, 1);
    return volDst;
  }

  static double variogram_point(const std::array<cv::Mat, 2>& img, int h, cv::Mat mask) {
    double ret = 0;
    int N = 0;
    for(int i = 0; i < mask.rows; i++) {
      for(int j = 0; j < mask.cols; j++) {
        if(mask.at<float>(i, j) < .5 || j - h < 0) continue;
        auto a = img[0].at<uint8_t>(i, j);
        auto b = img[1].at<uint8_t>(i, j - h);

        ret += (a - b) * (a - b);
        N++;
      }
    }
    return ret / N / 2;
  }

  static std::vector<double> normalized_variogram(const std::array<cv::Mat, 2>& img, int lo, int hi, cv::Mat mask) {
    std::vector<double> ret; ret.reserve(hi - lo + 1);
    double mx = 0, mn = std::numeric_limits<double>::max();
    for(int i = lo; i <= hi; i++) {
      ret.push_back(variogram_point(img, i, mask));
      mx = std::max(mx, ret.back());
      mn = std::min(mn, ret.back());
    }

    for(auto& x: ret) x = (x - mn) / (mx - mn);

    return ret;
  }
}
