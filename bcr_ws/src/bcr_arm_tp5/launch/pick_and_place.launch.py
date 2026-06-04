#!/usr/bin/python3
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    xacro_file = LaunchConfiguration("xacro_file")
    controllers_file = LaunchConfiguration("controllers_file")
    world = LaunchConfiguration("world")
    headless = LaunchConfiguration("headless").perform(context).lower() == "true"
    auto_start_pipeline = LaunchConfiguration("auto_start_pipeline").perform(context).lower() == "true"
    world_path = world.perform(context)
    gazebo_args = f"-r {'-s ' if headless else ''}{world_path}"

    robot_description_content = Command(
        [
            FindExecutable(name="xacro"),
            " ",
            xacro_file,
            " ",
            "use_gazebo:=true",
            " ",
            "use_camera:=true",
            " ",
            "ros2_controllers_path:=",
            controllers_file,
        ]
    )
    robot_description = {
        "robot_description": ParameterValue(robot_description_content, value_type=str)
    }

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"])
        ),
        launch_arguments={"gz_args": gazebo_args}.items(),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[robot_description, {"use_sim_time": True}],
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="tp5_camera_bridge",
        output="screen",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
            "/camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image",
            "/camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked",
            "/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
        ],
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        name="spawn_bcr_arm",
        output="screen",
        arguments=["-name", "bcr_arm", "-topic", "robot_description", "-x", "0.0", "-y", "0.0", "-z", "0.0"],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    joint_trajectory_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    actions = [
        gazebo,
        bridge,
        robot_state_publisher,
        spawn_robot,
        RegisterEventHandler(
            OnProcessExit(target_action=spawn_robot, on_exit=[joint_state_broadcaster_spawner])
        ),
        RegisterEventHandler(
            OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[joint_trajectory_controller_spawner],
            )
        ),
    ]

    if auto_start_pipeline:
        pick_and_place_node = Node(
            package="bcr_arm_tp5",
            executable="pick_and_place.py",
            name="pick_and_place",
            output="screen",
            parameters=[{"use_sim_time": True}],
        )
        actions.append(
            RegisterEventHandler(
                OnProcessExit(
                    target_action=joint_trajectory_controller_spawner,
                    on_exit=[pick_and_place_node],
                )
            )
        )

    return actions


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "xacro_file",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("bcr_arm_description"), "urdf", "robots", "bcr_arm.urdf.xacro"]
                ),
                description="Main BCR arm xacro file",
            ),
            DeclareLaunchArgument(
                "controllers_file",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("bcr_arm_gazebo"), "config", "ros2_controllers.yaml"]
                ),
                description="Controller YAML for ros2_control",
            ),
            DeclareLaunchArgument(
                "world",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("bcr_arm_tp5"), "worlds", "pick_scene.world"]
                ),
                description="TP5 pick scene world file",
            ),
            DeclareLaunchArgument(
                "headless",
                default_value="false",
                choices=["true", "false"],
                description="Run Gazebo server-only",
            ),
            DeclareLaunchArgument(
                "auto_start_pipeline",
                default_value="false",
                choices=["true", "false"],
                description="Start pick_and_place.py after controllers are active",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
