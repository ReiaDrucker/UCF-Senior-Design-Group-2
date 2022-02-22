#include <pybind11/pybind11.h>

#include <iostream>
#include <matching.h>
#include <calib.h>
#include <depth.h>

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

PYBIND11_MODULE(_core, m) {
  m.doc() = R"pbdoc(
        Module for calculating depth from stereogram images.
    )pbdoc";

  ImagePair::init_pybind(m);
  CameraPose::init_pybind(m);
  PointCloud::init_pybind(m);

#ifdef VERSION_INFO
  m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
  m.attr("__version__") = "dev";
#endif
}
