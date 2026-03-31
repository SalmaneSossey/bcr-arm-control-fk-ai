cmake_minimum_required(VERSION 3.8)
project(bcr_arm_gazebo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch config worlds data models plots
  DESTINATION share/${PROJECT_NAME}
)

install(
  FILES README.md
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/test_arm_movement.py
    scripts/forward_kinematics.py
    scripts/predict_fk_mlp.py
    scripts/compare_fk_streams.py
    scripts/generate_fk_dataset.py
    scripts/train_fk_mlp.py
    scripts/evaluate_fk_mlp.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
