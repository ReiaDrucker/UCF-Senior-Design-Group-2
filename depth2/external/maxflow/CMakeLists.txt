add_library(maxflow OBJECT graph.cpp maxflow.cpp)
target_include_directories(maxflow PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
