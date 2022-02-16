#pragma once
#include <gtsam/geometry/Cal3_S2.h>
#include <iostream>

#include <opencv2/calib3d.hpp>
#include <opencv2/opencv.hpp>

#include <gtsam/geometry/Point2.h>
#include <gtsam/geometry/Cal3DS2.h>
#include <gtsam/inference/Symbol.h>
#include <gtsam/slam/PriorFactor.h>
#include <gtsam/slam/ProjectionFactor.h>
#include <gtsam/slam/GeneralSFMFactor.h>
#include <gtsam/nonlinear/NonlinearFactorGraph.h>
#include <gtsam/nonlinear/LevenbergMarquardtOptimizer.h>
#include <gtsam/nonlinear/DoglegOptimizer.h>
#include <gtsam/nonlinear/Values.h>
#include <opencv4/opencv2/core/types.hpp>

#include "matching.h"

struct CameraPose {
  double f;
  double skew;
  std::array<cv::Mat, 2> pts;
  std::array<cv::Mat, 2> R;
  std::array<cv::Mat, 2> t;
  cv::Mat p;

  std::array<cv::Scalar, 2> center;

  double e1, e2;

  void validateTypes() {
    if(p.type() != CV_64FC3
       || pts[0].type() != CV_32FC2
       || R[0].type() != CV_64FC1
       || t[0].type() != CV_64FC1)
      throw runtime_error("Unexpected matrix types");
  }

  CameraPose(ImagePair& stereo, double fov):
    e1(std::numeric_limits<double>::quiet_NaN()),
    e2(std::numeric_limits<double>::quiet_NaN()),
    skew(0)
  {
    f = math::focal_from_fov(stereo.img[0].size, fov);

    auto K = cv::Matx33d(f, 0, 0,
                         0, f, 0,
                         0, 0, 1);

    pts = stereo.get_matches_tuple();
    pts = util::for_each(pts, [&](auto&& p, auto i) {
      center[i] = cv::Scalar(stereo.img[i].cols / 2., stereo.img[i].rows / 2.);
      return cv::Mat(p - center[i]);
    });

    R[0] = cv::Mat::eye(3, 3, CV_64FC1);
    t[0] = cv::Mat::zeros(3, 1, CV_64FC1);

    cv::Mat mask;
    auto E = cv::findEssentialMat(pts[0], pts[1], K, cv::LMEDS, 0.999, 1.0, mask);
    cv::recoverPose(E, pts[0], pts[1], K, R[1], t[1], std::numeric_limits<double>::infinity(), mask, p);

    cv::convertPointsFromHomogeneous(p.reshape(4), p);

    for(int i = 0; i < p.rows; i++) {
      auto pt = p.at<cv::Vec3d>(i);
      if(pt[2] < 0) mask.at<uchar>(i) = 0;
    }

    p = util::filter_mat<cv::Vec3d>(p, mask);
    util::for_each(std::array<int,2>{}, [&](auto&&, auto i) {
      pts[i] = util::filter_mat<cv::Vec2f>(pts[i], mask);
      return 0;
    });

    validateTypes();
  }

  void refine() {
    using namespace gtsam;

    NonlinearFactorGraph graph;
    Values initial;

    Cal3_S2 K(f, f, 0, 0, 0);

    auto cal_noise = noiseModel::Diagonal::Sigmas((Vector(5) << 1, 1, 0.01, 1, 1).finished());
    graph.emplace_shared<PriorFactor<Cal3_S2>>(Symbol('K', 0), K, cal_noise);
    initial.insert(Symbol('K', 0), K);

    int n = pts[0].rows;
    auto measurement_noise = noiseModel::Isotropic::Sigma(2, 2.0);
    auto pose = util::for_each(pts, [&](auto&& pts, auto i) {
      auto pose = util::gtsam_pose_from_cv<double>(R[i].t(), -R[i].t() * t[i]);
      initial.insert(Symbol('x', i), pose);

      for(int j = 0; j < n; j++) {
        auto pt_cv = pts.template at<cv::Vec2f>(j);
        auto pt = gtsam::Point2(pt_cv[0], pt_cv[1]);
        graph.emplace_shared<GeneralSFMFactor2<Cal3_S2>>(pt, measurement_noise,
                                                         Symbol('x', i), Symbol('l', j), Symbol('K', 0));
      }

      return pose;
    });

    auto pose_noise = noiseModel::Diagonal::Sigmas((Vector(6) << Vector3::Constant(0.0),
                                                        Vector3::Constant(0.0)).finished());
    graph.emplace_shared<PriorFactor<Pose3> >(gtsam::Symbol('x', 0), pose[0], pose_noise);

    Point3 first_pt;
    for(int i = 0; i < n; i++) {
      auto cv_pt = p.at<cv::Vec3d>(i);
      Point3 pt(cv_pt[0], cv_pt[1], cv_pt[2]);
      initial.insert<Point3>(Symbol('l', i), pt);

      if(i == 0) first_pt = pt;
    }

    auto point_noise = noiseModel::Isotropic::Sigma(3, 0.1);
    graph.emplace_shared<PriorFactor<Point3>>(Symbol('l', 0), first_pt, point_noise);

    e1 = graph.error(initial);

    auto result = LevenbergMarquardtOptimizer(graph, initial).optimize();
    e2 = graph.error(result);

    K = result.at<Cal3_S2>(Symbol('K', 0));
    // f = sqrt(K.fx() * K.fy());
    // skew = K.skew();

    util::for_each(std::array<int,2>{}, [&](auto&&, int i) {
      auto [R2, t2] = util::cv_from_gtsam_pose(result.at<Pose3>(Symbol('x', i)));
      R[i] = R2.t(); t[i] = -R2.t() * t2;
      t[i] /= sqrt(t[i].dot(t[i]));
      return 0;
    });

    for(int i = 0; i < n; i++) {
      auto pt_gtsam = result.at<Point3>(Symbol('l', i));
      p.at<cv::Vec3d>(i) = cv::Vec3d(pt_gtsam[0], pt_gtsam[1], pt_gtsam[2]);
    }

    validateTypes();
  }

  std::array<cv::Mat, 2> rectify(const std::array<cv::Mat, 2>& img) {
    std::array<cv::Matx33d, 2> K;

    K[0] = cv::Matx33d(f, skew, center[0][0],
                       0, f, center[0][1],
                       0, 0, 1);

    K[1] = cv::Matx33d(f, skew, center[1][0],
                       0, f, center[1][1],
                       0, 0, 1);

    // S=np.mat([[0,-T[2],T[1]],[T[2],0,-T[0]],[-T[1],T[0],0]])
    // E=S*np.mat(R)

    cv::Vec3d T = t[1];
    cv::Matx33d Tx(0, -T[2], T[1],
                   T[2], 0, -T[0],
                   -T[1], T[0], 0);
    auto E = Tx * R[1];
    cv::Matx33d F = cv::Mat(K[1].inv().t() * E * K[0].inv());

    // F = F * (1 / F(2, 2));
    std::cout << F << std::endl;

    auto size = cv::Size(img[0].size[1], img[0].size[0]);
    std::array<cv::Mat, 2> H;
    cv::stereoRectifyUncalibrated(pts[0], pts[1], F, size, H[0], H[1]);

    std::tie(H, size) = math::get_optimal_homography(H, {img[0].size, img[1].size});

    return util::for_each(H, [&](auto&& H, auto i) {
      pts[i] = math::warp_points(pts[i] + center[i], H) - center[i];
      cv::Mat ret;
      cv::warpPerspective(img[i], ret, H, size);
      return ret;
    });

    validateTypes();
  }

  auto get_matches() {
    static constexpr int elem_sz = sizeof(float);

    int n = pts[0].rows;
    std::vector<cv::Vec2f> flat(n * 2);
    for(int i = 0; i < n; i++) {
      flat[i * 2 + 0] = pts[0].at<cv::Vec2f>(i) + cv::Vec2f(center[0][0], center[0][1]);
      flat[i * 2 + 1] = pts[1].at<cv::Vec2f>(i) + cv::Vec2f(center[1][0], center[1][1]);
    }

    return py::array_t<float>({n, 2, 2},
                              {2 * 2 * elem_sz, 2 * elem_sz, elem_sz},
                              (float*)flat.data());
  }

  friend std::ostream& operator<<(std::ostream& os, const CameraPose& pose) {
    os << "p.size: " << pose.p.size << '\n';
    os << "f: " << pose.f << '\n';
    os << "skew: " << pose.skew << '\n';
    os << "R: " << pose.R[1] << '\n';
    os << "t: " << pose.t[1] << '\n';

    {
      auto yaw = atan2(pose.R[1].at<double>(1, 0), pose.R[1].at<double>(0, 0));
      auto pitch = atan2(-pose.R[1].at<double>(2, 0), hypot(pose.R[1].at<double>(2, 1), pose.R[1].at<double>(2, 2)));
      auto roll = atan2(pose.R[1].at<double>(2, 1), pose.R[1].at<double>(2, 2));

      auto to_deg = [](auto x) { return x * 180 / acos(-1); };
      os << "yaw (deg): " << to_deg(yaw)  << '\n';
      os << "pitch (deg): " << to_deg(pitch) << '\n';
      os << "roll (deg): " << to_deg(roll) << '\n';
    }

    if(!isnan(pose.e1))
      os << "error before/after: " << pose.e1 << " " << pose.e2 << "\n";

    return os;
  }
};
