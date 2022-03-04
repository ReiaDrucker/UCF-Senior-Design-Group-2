#include <depth.h>
#include <matching.h>

#include <common/util.h>
#include <common/math.h>

#include <opencv2/calib3d.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/ximgproc.hpp>

#include <LocalExpStereo/FastGCStereo.h>
#include <LocalExpStereo/CostVolumeEnergy.h>

void PointCloud::validateTypes() {
  if(disparity.type() != CV_32FC1)
    throw std::runtime_error("Unexpected matrix types");
}

PointCloud& PointCloud::load_stereo(ImagePair& stereo) {
  if (config.MATCHER == MatcherType::SGBM) {
    auto matcher = cv::StereoSGBM::create(config.min_disp,
                                          config.num_disp(16),
                                          config.block_size,
                                          0, // P1
                                          0, // P2
                                          0, // disp12maxDiff
                                          0, // preFilterCap
                                          5, // uniquenessRatio
                                          5, // speckleSize
                                          5  // speckleRange
                                          );

    matcher->compute(stereo.img[0], stereo.img[1], disparity);

    auto right_matcher = cv::ximgproc::createRightMatcher(matcher);

    cv::Mat right_disparity;
    right_matcher->compute(stereo.img[0], stereo.img[1], right_disparity);

    auto wls_filter = cv::ximgproc::createDisparityWLSFilter(matcher);
    wls_filter->setLambda(8000);
    wls_filter->setSigmaColor(config.sigma_color);

    wls_filter->filter(disparity, stereo.img[0], disparity, right_disparity);
    conf = wls_filter->getConfidenceMap();

    disparity.convertTo(disparity, CV_32FC1);
    disparity = disparity / 16; // correct for opencv's multiplier
  }

  else if(config.MATCHER == MatcherType::LOCAL_EXP) {
    Parameters params(1.0f, 20, "GF", .001f);

    std::array<cv::Mat, 2> img;
    img[0] = stereo.img[0];
    img[1] = cv::Mat::zeros(stereo.img[1].size(), stereo.img[1].type());

    if(config.min_disp < 0) {
      stereo.img[1](cv::Rect(-config.min_disp, 0, img[1].cols + config.min_disp, img[1].rows))
        .copyTo(img[1](cv::Rect(0, 0, img[1].cols + config.min_disp, img[1].rows)));
    } else {
      stereo.img[1](cv::Rect(0, 0, img[1].cols - config.min_disp, img[1].rows))
        .copyTo(img[1](cv::Rect(config.min_disp, 0, img[1].cols - config.min_disp, img[1].rows)));
    }

    std::array<cv::Mat, 2> img_color = util::for_each(img, [](auto&& img, auto) {
      cv::Mat ret;
      cv::cvtColor(img, ret, cv::COLOR_GRAY2RGB);
      return ret;
    });

    FastGCStereo matcher(img_color[0], img_color[1], params, config.num_disp(), 0, 5 /* vdisp */);

    {
      if(config.use_gssim_cost) {
        vol[0] = math::gssim_volume(img,
                                    config.num_disp() + 1,
                                    config.gssim_patch_size,
                                    config.gssim_consts[0],
                                    config.gssim_consts[1],
                                    config.gssim_consts[2]);
        vol[1] = math::volume_l2r(vol[0]);

        auto energy = std::make_unique<CostVolumeEnergy>(img_color[0], img_color[1],
                                                         vol[0], vol[1],
                                                         params, config.num_disp(), 0, 5);

        matcher.setStereoEnergyCPU(std::move(energy));
      }

      auto prop1 = ExpansionProposer(1);
      auto prop2 = RandomProposer(7, config.num_disp());
      auto prop3 = ExpansionProposer(2);
      auto prop4 = RansacProposer(1);

      matcher.addLayer(5, { &prop1, &prop4, &prop2 });
      matcher.addLayer(15, { &prop3, &prop4 });
      matcher.addLayer(25, { &prop3, &prop4 });

      cv::Mat label, raw_label;
      matcher.run(config.max_iters, { 0 }, config.pm_iters, label, raw_label);

      disparity = matcher.getEnergyInstance().computeDisparities(label);
      disparity = disparity.mul(stereo.mask);
    }
  }

  validateTypes();
  return *this;
}

py::array_t<float> PointCloud::get_disparity() {
  return util::mat_to_array<float>(disparity);
}

py::array_t<float> PointCloud::get_gssim_volume(int idx) {
  return util::mat_to_array<float>(vol[idx]);
}

void PointCloud::init_pybind(py::module_& m) {
  py::enum_<PointCloud::MatcherType>(m, "PointCloudMatcherType")
    .value("SGBM", MatcherType::SGBM)
    .value("LOCAL_EXP", MatcherType::LOCAL_EXP)
    ;

  py::class_<PointCloud::Builder>(m, "PointCloudBuilder")
    .def(py::init<>())
    .def("set_matcher", &PointCloud::Builder::set_matcher)
    .def("set_min_disp", &PointCloud::Builder::set_min_disp)
    .def("set_max_disp", &PointCloud::Builder::set_max_disp)
    .def("set_block_size", &PointCloud::Builder::set_block_size)
    .def("set_sigma_color", &PointCloud::Builder::set_sigma_color)
    .def("set_max_iters", &PointCloud::Builder::set_max_iters)
    .def("set_pm_iters", &PointCloud::Builder::set_pm_iters)
    .def("set_use_gssim_cost", &PointCloud::Builder::set_use_gssim_cost)
    .def("set_gssim_consts", &PointCloud::Builder::set_gssim_consts)
    .def("set_gssim_patch_size", &PointCloud::Builder::set_gssim_patch_size)
    .def("build", &PointCloud::Builder::build)
    ;
  py::class_<PointCloud>(m, "PointCloud")
    .def("load_stereo", &PointCloud::load_stereo)
    .def("get_disparity", &PointCloud::get_disparity)
    .def("get_gssim_volume", &PointCloud::get_gssim_volume)
    ;
}
