add_library(maxflow INTERFACE graph.cpp maxflow.cpp)
target_include_directories(maxflow INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)
