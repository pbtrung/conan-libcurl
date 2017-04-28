PROJECT(Example C)
cmake_minimum_required(VERSION 3.0)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(example example.c)