cmake_minimum_required(VERSION 3.15...3.19)

project(depth_algo VERSION "0.0.1")

list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})
list(APPEND CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR})

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include(conan.cmake)

conan_cmake_configure(
  REQUIRES opencv/4.5.3
  REQUIRES eigen/3.4.0
  OPTIONS ffmpeg:with_openjpeg=False
  GENERATORS cmake_find_package)

conan_cmake_autodetect(settings)

message("hmm: ${settings}")

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
find_package(OpenCV REQUIRED)
find_package(Eigen3 REQUIRED)

pybind11_add_module(_core MODULE src/main.cpp)
target_link_libraries(_core PRIVATE opencv_core Eigen3::Eigen)
target_include_directories(_core PUBLIC ${CMAKE_SOURCE_DIR}/include)

target_compile_definitions(_core PRIVATE VERSION_INFO=${PROJECT_VERSION})

install(TARGETS _core DESTINATION .)
