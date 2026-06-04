cmake_minimum_required(VERSION 3.8)
project(bcr_arm_tp5)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  FILES README_TP5.md
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/perception.py
    scripts/segmentation.py
    scripts/classifier.py
    scripts/ik_solver.py
    scripts/trajectory.py
    scripts/pick_and_place.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
