import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterFile, ParameterValue
from launch_ros.substitutions import FindPackageShare

def launch_setup(context):
    # Load parameters
    log_level = context.launch_configurations["log_level"]
    ns = context.launch_configurations["ns"]
    model = context.launch_configurations["model"]
    use_fake_hardware = str(context.launch_configurations["use_fake_hardware"]).lower()
    com_port = context.launch_configurations["com_port"]

    # Print parameters
    print("")
    print("Starting driver with parameters:")
    print(" log_level:           " + log_level)
    if ns == "":
        print(" ns:                  " + "/")
    else:
        print(" ns:                  " + "/" + ns)
    print(" model:               " + model)
    print(" use_fake_hardware:   " + use_fake_hardware)
    if use_fake_hardware == "false":
        print(" com_port:            " + com_port)
    print("")

    # Package shares
    description_pkg_share = FindPackageShare(package="robotiq_description").find("robotiq_description")
    bringup_pkg_share = FindPackageShare(package="robotiq_bringup").find("robotiq_bringup")

    # Robot description
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            model,
            " ",
            "use_fake_hardware:=",
            use_fake_hardware,
            " ",
            "com_port:=",
            com_port,
        ]
    )

    robot_description_param = {
        "robot_description": ParameterValue(robot_description_content, value_type=str)
    }

    # Config files
    update_rate_config_file = PathJoinSubstitution(
        [
            description_pkg_share,
            "config",
            "robotiq_update_rate.yaml",
        ]
    )

    ros2_controllers_file = PathJoinSubstitution(
        [bringup_pkg_share, "config", "robotiq_controllers.yaml"]
    )

    # Nodes
    nodes = []

    nodes.append(
        Node(
            package="controller_manager",
            executable="ros2_control_node",
            namespace=ns,
            parameters=[
                ParameterFile(ros2_controllers_file, allow_substs=True),
                robot_description_param,
                update_rate_config_file,
            ],
            arguments=["--ros-args", "--log-level", log_level],
            output="screen",
        )
    )

    nodes.append(
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            namespace=ns,
            parameters=[robot_description_param],
            arguments=["--ros-args", "--log-level", log_level],
        )
    )

    nodes.append(
        Node(
            package="controller_manager",
            executable="spawner",
            namespace=ns,
            arguments=[
                "joint_state_broadcaster",
                "--controller-manager",
                "controller_manager",
                "--ros-args",
                "--log-level",
                log_level,
            ],
        )
    )

    nodes.append(
        Node(
            package="controller_manager",
            executable="spawner",
            namespace=ns,
            arguments=[
                "robotiq_gripper_controller",
                "-c",
                "controller_manager",
                "--ros-args",
                "--log-level",
                log_level,
            ],
        )
    )

    nodes.append(
        Node(
            package="controller_manager",
            executable="spawner",
            namespace=ns,
            arguments=[
                "robotiq_activation_controller",
                "-c",
                "controller_manager",
                "--ros-args",
                "--log-level",
                log_level,
            ],
        )
    )

    return nodes

def generate_launch_description():
    description_pkg_share = FindPackageShare(package="robotiq_description").find("robotiq_description")
    default_model_path = os.path.join(
        description_pkg_share, "urdf", "robotiq_2f_85_gripper.urdf.xacro"
    )

    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "log_level",
            default_value="error",
            description="Log Level to use for all nodes",
            choices=["info", "debug", "error"],
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "ns",
            default_value="",
            description="Namespace for all nodes",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "model",
            default_value=default_model_path,
            description="Absolute path to gripper URDF file",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_fake_hardware",
            default_value="false",
            description="Start robot with fake hardware (mock components)",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "com_port",
            default_value="/dev/ttyUSB0",
            description="Port for communicating with Robotiq hardware",
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
