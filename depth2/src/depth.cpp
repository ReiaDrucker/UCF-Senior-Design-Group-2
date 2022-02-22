#include <depth.h>
#include <matching.h>

#include <common/util.h>
#include <common/math.h>

#include <opencv2/calib3d.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/ximgproc.hpp>

#include <LocalExpStereo/FastGCStereo.h>

void PointCloud::validateTypes() {
  if(disparity.type() != CV_32FC1)
    throw std::runtime_error("Unexpected matrix types");
}

PointCloud::PointCloud(ImagePair& stereo, int min_disp, int num_disp, int block_size, double sigma_color) {
  if constexpr(MATCHER == MatcherType::SGBM) {
    auto matcher = cv::StereoSGBM::create(min_disp,
                                          num_disp,
                                          block_size,
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
    wls_filter->setSigmaColor(sigma_color);

    wls_filter->filter(disparity, stereo.img[0], disparity, right_disparity);
    conf = wls_filter->getConfidenceMap();

    disparity.convertTo(disparity, CV_32FC1);
    disparity = disparity / 16; // correct for opencv's multiplier
  }

  else if constexpr(MATCHER == MatcherType::LOCAL_EXP) {
    Parameters params(1.0f, 20, "GF", .001f);

    auto max_disp = min_disp + num_disp;

    std::array<cv::Mat, 2> img_color = util::for_each(stereo.img, [](auto&& img, auto) {
      cv::Mat ret;
      cv::cvtColor(img, ret, cv::COLOR_GRAY2RGB);
      return ret;
    });

    FastGCStereo matcher(img_color[0], img_color[1], params, max_disp, min_disp, 5 /* vdisp */);

    {
      auto prop1 = ExpansionProposer(1);
      auto prop2 = RandomProposer(7, max_disp);
      auto prop3 = ExpansionProposer(2);
      auto prop4 = RansacProposer(1);

      matcher.addLayer(5, { &prop1, &prop4, &prop2 });
      matcher.addLayer(15, { &prop3, &prop4 });
      matcher.addLayer(25, { &prop3, &prop4 });

      auto max_iters = 10;
      auto pm_iters = 5;

      cv::Mat label, raw_label;
      matcher.run(max_iters, { 0 }, pm_iters, label, raw_label);

      disparity = matcher.getEnergyInstance().computeDisparities(label);
      disparity = disparity.mul(stereo.mask);
    }
  }

  validateTypes();
}

py::array_t<float> PointCloud::get_disparity() {
  return util::mat_to_array<float>(disparity);
}

void PointCloud::init_pybind(py::module_& m) {
  py::class_<PointCloud>(m, "PointCloud")
    .def(py::init<ImagePair&, int, int, int, double>())
    .def("get_disparity", &PointCloud::get_disparity)
    ;
}
