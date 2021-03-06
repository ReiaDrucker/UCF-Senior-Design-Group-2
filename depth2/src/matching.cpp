#include <matching.h>
#include <calib.h>

#include <common/util.h>
#include <common/math.h>

#include <opencv2/features2d.hpp>

ImagePair& ImagePair::load_images(ImagePair::array_t left, ImagePair::array_t right) {
  img[0] = cv::Mat(left.shape(0), left.shape(1), CV_8UC1, (uint8_t*)left.data()).clone();
  img[1] = cv::Mat(right.shape(0), right.shape(1), CV_8UC1, (uint8_t*)right.data()).clone();

  img[0] = math::rescale(img[0], config.TARGET_SCALE);
  img[1] = math::rescale(img[1], config.TARGET_SCALE);

  mask = cv::Mat::ones(img[1].rows, img[1].cols, CV_32FC1);
  return *this;
}

ImagePair& ImagePair::fill_matches() {
  struct kp_and_matches {
    std::vector<cv::KeyPoint> kp;
    cv::Mat des;
  };

  auto detector = Detector::create(config.N_FEATURES);
  auto features = util::for_each(img, [&](auto&& img, auto) {
    kp_and_matches ret;

    detector->detect(img, ret.kp);
    detector->compute(img, ret.kp, ret.des);

    return ret;
  });

  std::vector<std::vector<cv::DMatch>> matches_;
  auto matcher = cv::BFMatcher(detector->defaultNorm());
  matcher.knnMatch(features[0].des, features[1].des, matches_, 2);

  matches.reserve(matches_.size());
  for(auto p: matches_) {
    if(p[0].distance < config.RATIO * p[1].distance) {
      auto& u = features[0].kp[p[0].queryIdx].pt;
      auto& v = features[1].kp[p[0].trainIdx].pt;
      matches.push_back({ u, v });
    }
  }

  return *this;
}

ImagePair& ImagePair::rectify(CameraPose& pose) {
  img = pose.rectify(img, mask);
  return *this;
}

auto ImagePair::get_image(int idx) {
  return util::mat_to_array<uint8_t>(img[idx]);
}

auto ImagePair::get_matches() {
  static constexpr int elem_sz = sizeof(float);
  return py::array_t<float>({(int)matches.size(), 2, 2},
                            {2 * 2 * elem_sz, 2 * elem_sz, elem_sz},
                            (float*)matches.data());
}

cv::Mat ImagePair::get_matches_mat(int idx) {
  using vec = cv::Vec2f;
  return cv::Mat(matches.size(), 1, CV_32FC2, (vec*)matches.data() + idx, 2 * sizeof(vec));
}

std::array<cv::Mat, 2> ImagePair::get_matches_tuple() {
  return std::array<cv::Mat, 2> {
    get_matches_mat(0),
    get_matches_mat(1)
  };
}

void ImagePair::init_pybind(py::module_& m) {

  py::class_<ImagePair::Builder>(m, "ImagePairBuilder")
    .def(py::init<>())
    .def("set_target_scale", &ImagePair::Builder::set_target_scale)
    .def("set_feature_count", &ImagePair::Builder::set_target_scale)
    .def("set_test_ratio", &ImagePair::Builder::set_test_ratio)
    .def("build", &ImagePair::Builder::build)
    ;

  py::class_<ImagePair>(m, "ImagePair")
    .def("__deepcopy__", [](const ImagePair& o, py::dict) { return ImagePair(o); })
    .def("load_images", &ImagePair::load_images)
    .def("fill_matches", &ImagePair::fill_matches, py::call_guard<py::gil_scoped_release>())
    .def("rectify", [](ImagePair& pair, CameraPose& pose) { return pair.rectify(pose); })
    .def("get_matches", &ImagePair::get_matches)
    .def("get_image", &ImagePair::get_image)
    ;
}
