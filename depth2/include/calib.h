#pragma once
#include <gtsam/linear/NoiseModel.h>
#include <iostream>

#include <opencv2/opencv.hpp>

#include <gtsam/geometry/Point2.h>
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
  std::array<cv::Mat, 2> pts;
  std::array<cv::Mat, 2> R;
  std::array<cv::Mat, 2> t;
  cv::Mat p;

  double e1, e2;

  CameraPose(ImagePair& stereo, double fov) {
    f = math::focal_from_fov(stereo.img[0].size, fov);
    std::cout << f << std::endl;

    auto K = cv::Matx33d(f, 0, 0,
                         0, f, 0,
                         0, 0, f);

    pts = stereo.get_matches_tuple();
    pts = util::for_each(pts, [&](auto&& p, auto i) {
      return cv::Mat(p - cv::Scalar(stereo.img[i].cols / 2., stereo.img[i].rows / 2.));
    });

    R[0] = cv::Mat::eye(3, 3, CV_64FC1);
    t[0] = cv::Mat::zeros(3, 1, CV_64FC1);

    std::cout << pts[0].size << std::endl;

    cv::Mat mask;
    auto E = cv::findEssentialMat(pts[0], pts[1], K, cv::LMEDS, 0.999, 1.0, mask);
    cv::recoverPose(E, pts[0], pts[1], K, R[1], t[1], std::numeric_limits<double>::infinity(), mask, p);

    cv::convertPointsFromHomogeneous(p.reshape(4), p);
    assert(p.type() == CV_64FC3);

    for(int i = 0; i < p.rows; i++) {
      auto pt = p.at<cv::Vec3d>(i);
      if(pt[2] < 0) mask.at<uchar>(i) = 0;
    }

    p = util::filter_mat<cv::Vec3d>(p, mask);
    auto P = util::for_each(std::array<int,2>{}, [&](auto&&, auto i) {
      pts[i] = util::filter_mat<cv::Vec2f>(pts[i], mask);
      return math::construct_proj_mat(R[i], t[i], K);
    });

    // let's get the angle from top down between our cameras
    {
      auto a = cv::Vec3d(0, 0, 1);
      cv::Vec3d b = cv::Mat(R[1] * a);

      auto A = cv::Vec2d(a[1], a[2]);
      auto B = cv::Vec2d(b[1], b[2]);

      std::cout << "angle (deg): " << acos(A.dot(B)) * 180 / acos(-1) << std::endl;
    }

    std::cout << p.size << std::endl;
    std::cout << "f: " << f << std::endl;
    std::cout << "R: " << R[1] << std::endl;
    std::cout << "t: " << t[1] << std::endl;

    int acc = 0;
    for(int i = 0; i < p.rows; i++) {
      auto pt = p.at<cv::Vec3d>(i);
      acc += pt[2] < 0;
    }

    std::cout << "behind cam: " << acc << std::endl;
  }

  void refine() {
    using namespace gtsam;

    NonlinearFactorGraph graph;
    Values initial;

    Cal3_S2 K(f, f, 0, 0, 0);

    auto cal_noise = noiseModel::Diagonal::Sigmas((Vector(5) << 100, 100, 0.01 /*skew*/, 100, 100).finished());
    graph.emplace_shared<PriorFactor<Cal3_S2>>(Symbol('K', 0), K, cal_noise);

    initial.insert(Symbol('K', 0), K);

    int n = pts[0].rows;
    auto measurement_noise = noiseModel::Isotropic::Sigma(2, 2.0);
    auto pose = util::for_each(pts, [&](auto&& pts, auto i) {
      auto pose = util::gtsam_pose_from_cv<double>(R[i], t[i]);
      initial.insert(Symbol('x', i), pose);

      for(int j = 0; j < n; j++) {
        auto pt_cv = pts.template at<cv::Vec2d>(j);
        auto pt = gtsam::Point2(pt_cv[0], pt_cv[1]);
        graph.emplace_shared<GeneralSFMFactor2<Cal3_S2>>(pt, measurement_noise,
                                                         Symbol('x', i), Symbol('l', j), Symbol('K', 0));
      }

      return pose;
    });

    auto pose_noise = noiseModel::Diagonal::Sigmas((Vector(6) << Vector3::Constant(0.1),
                                                        Vector3::Constant(0.1)).finished());
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
    f = sqrt(K.fx() * K.fy());

    util::for_each(std::array<int,2>{}, [&](auto&&, int i) {
      auto [R2, t2] = util::cv_from_gtsam_pose(result.at<Pose3>(Symbol('x', i)));
      R[i] = R2; t[i] = t2;
      return 0;
    });

    for(int i = 0; i < n; i++) {
      auto pt_gtsam = result.at<Point3>(Symbol('l', i));
      p.at<cv::Vec3d>(i) = cv::Vec3d(pt_gtsam[0], pt_gtsam[1], pt_gtsam[2]);
    }

    std::cout << e1 << " " << e2 << std::endl;

    std::cout << "f: " << f << std::endl;
    std::cout << "R: " << R[1] << std::endl;
    std::cout << "t: " << t[1] << std::endl;
    std::cout << "sample: " << p.at<cv::Vec3d>(69) << std::endl;
  }
};
