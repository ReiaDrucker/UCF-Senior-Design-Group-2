#include <pybind11/pybind11.h>

#include <iostream>
#include <matching.h>
#include <calib.h>

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
  m.doc() = R"pbdoc(
        Module for calculating depth from stereogram images.
    )pbdoc";

  py::class_<ImagePair>(m, "ImagePair")
    .def(py::init<py::array_t<uint8_t>, py::array_t<uint8_t>>())
    .def("fill_matches", &ImagePair::fill_matches)
    .def("get_matches", &ImagePair::get_matches)
    .def("get_image", &ImagePair::get_image)
    .def("rectify", [](ImagePair& pair, CameraPose& pose) { return pair.rectify(pose); })
    ;

  py::class_<CameraPose>(m, "CameraPose")
    .def(py::init<ImagePair&, double>())
    .def("refine", &CameraPose::refine)
    .def("get_matches", &CameraPose::get_matches)
    .def("__repr__", [](const CameraPose& pose) {
      std::stringstream ss;
      ss << pose;
      return ss.str();
    })
    ;

#ifdef VERSION_INFO
  m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
  m.attr("__version__") = "dev";
#endif
}
