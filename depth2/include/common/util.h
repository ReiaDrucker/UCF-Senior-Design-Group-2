#include <tuple>
#include <array>

#include <opencv2/opencv.hpp>
#include <pybind11/numpy.h>

namespace py = pybind11;

namespace util {
  namespace detail {
    template <typename T, typename F, size_t... I>
    auto _for_each(T t, F f, std::index_sequence<I...>) {
      return std::array { (std::forward<F>(f))(std::get<I>(t))... };
    }
  }

  template <typename T, typename F>
  auto for_each(T t, F f) {
    constexpr int N = std::tuple_size_v<std::decay_t<T>>;
    return detail::_for_each(std::forward<T>(t), std::forward<F>(f), std::make_index_sequence<N>{});
  }

  template <typename T>
  static py::array_t<T> mat_to_array(cv::Mat mat) {
    constexpr int elem_size = sizeof(T);
    return {
      {mat.rows, mat.cols},
      {mat.cols * elem_size, elem_size},
      (T*)mat.ptr()
    };
  }
};
