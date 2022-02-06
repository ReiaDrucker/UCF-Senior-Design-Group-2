#include <tuple>
#include <array>

namespace util {
  namespace detail {
    template <typename T, typename F, size_t... I>
    auto _for_each(T t, F f, std::index_sequence<I...>) {
      return std::array { (std::forward<F>(f))(std::forward<T>(std::get<I>(t)))... };
    }
  }

  template <typename T, typename F>
  auto for_each(T t, F f) {
    constexpr int N = std::tuple_size_v<std::decay_t<T>>;
    return detail::_for_each(t, f, std::make_index_sequence<N>{});
  }
};
