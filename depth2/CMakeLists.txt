cmake_minimum_required(VERSION 3.15...3.19)

project(depth_algo VERSION "0.0.1")

list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})
list(APPEND CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR})

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include(conan.cmake)

conan_cmake_configure(
  REQUIRES opencv/4.1.2
  REQUIRES gtsam/4.0.3
  REQUIRES eigen/3.4.0
  OPTIONS ffmpeg:with_openjpeg=False
  OPTIONS opencv:contrib=True
  OPTIONS opencv:parallel=tbb
  GENERATORS cmake_find_package)

conan_cmake_autodetect(settings)

# this seems jank
set(CONAN_COMMAND "conan")

conan_cmake_install(PATH_OR_REFERENCE .
                    BUILD missing
                    REMOTE conancenter
                    SETTINGS ${settings})

if(SKBUILD)
  # Scikit-Build does not add your site-packages to the search path
  # automatically, so we need to add it _or_ the pybind11 specific directory
  # here.
  execute_process(
    COMMAND "${PYTHON_EXECUTABLE}" -c
            "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE _tmp_dir
    OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ECHO STDOUT)
  list(APPEND CMAKE_PREFIX_PATH "${_tmp_dir}")
endif()

# Now we can find pybind11
find_package(pybind11 CONFIG REQUIRED)
find_package(OpenCV REQUIRED COMPONENTS features2d calib3d xfeatures2d ximgproc)
find_package(GTSAM REQUIRED)

add_subdirectory(external/maxflow)
add_subdirectory(external/LocalExpStereo)

pybind11_add_module(_core MODULE src/main.cpp src/matching.cpp src/calib.cpp src/depth.cpp)
target_link_libraries(_core PRIVATE opencv_core opencv_ximgproc opencv_features2d opencv_xfeatures2d opencv_calib3d GTSAM::gtsam LocalExpStereo maxflow tbb)
target_include_directories(_core PUBLIC ${CMAKE_SOURCE_DIR}/include)

target_compile_definitions(_core PRIVATE VERSION_INFO=${PROJECT_VERSION})

install(TARGETS _core DESTINATION .)

# Force the RPATH installation so the user does not have to fiddle
# with the library path `(DY)?LD_LIBRARY_PATH` 1_.
#
# .. _1: https://gitlab.kitware.com/cmake/community/-/wikis/doc/cmake/RPATH-handling#always-full-rpath
set(lib_path "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}")
list(FIND CMAKE_PLATFORM_IMPLICIT_LINK_DIRECTORIES "${lib_path}" is_system)
if ("${is_system}" STREQUAL "-1")
    # The following is necessary for installation in a virtual
    # environment `python -m pip venv env`
    set_target_properties(_core PROPERTIES
        INSTALL_RPATH_USE_LINK_PATH TRUE
        INSTALL_RPATH "${lib_path}")
endif()
