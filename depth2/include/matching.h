#include <array>
#include <opencv2/core/base.hpp>
#include <opencv2/core/types.hpp>
#include <vector>

#include <opencv2/opencv.hpp>
#include <Eigen/Eigen>

#include <common/util.h>

constexpr int nfeatures = 1e5;
constexpr double ratio = .75;

struct ImageSet {
  std::array<cv::Mat, 2> img;
  std::vector<std::array<cv::Point2f, 2>> matches;

  ImageSet() {
    
  }

  ImageSet& fill_matches() {
    struct kp_and_matches {
      std::vector<cv::KeyPoint> kp;
      cv::Mat des;
    };

    auto features = util::for_each(img, [](auto&& img) {
      auto orb = cv::ORB::create(nfeatures);

      kp_and_matches ret;

      orb->detect(img, ret.kp);
      orb->compute(img, ret.kp, ret.des);

      return ret;
    });

    std::vector<std::vector<cv::DMatch>> matches_;
    auto matcher = cv::BFMatcher(cv::NORM_HAMMING);
    matcher.knnMatch(features[0].des, features[1].des, matches_, 2);

    matches.reserve(matches_.size());
    for(auto p: matches_) {
      if(p[0].distance < ratio * p[1].distance) {
        auto& u = features[0].kp[p[0].queryIdx].pt;
        auto& v = features[1].kp[p[0].trainIdx].pt;
        matches.push_back({ u, v });
      }
    }

    return *this;
  }

  void adjust_scale() {

  }
};
