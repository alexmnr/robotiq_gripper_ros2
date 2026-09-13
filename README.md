# robotiq_gripper_ros2

This repository contains the ROS 2 driver, controller and description packages for working with a Robotiq Gripper.

# Usage

Launch the controller manager, robot state publisher, and controller spawners for the Robotiq gripper:

```bash
ros2 launch robotiq_bringup bringup.launch.py
```

## Launch Arguments

| Argument | Default | Description |
| --- | --- | --- |
| `ns` | `""` | Namespace applied to all nodes. |
| `model` | `<pkg_share>/urdf/robotiq_2f_85_gripper.urdf.xacro` | Absolute path to the gripper URDF/Xacro file. |
| `use_fake_hardware` | `false` | Uses mock hardware components instead of real hardware when set to `true`. |
| `com_port` | `/dev/ttyUSB0` | Serial port path for hardware communication. |

## Examples

**Launch with Mock Hardware and Namespace:**

```bash
ros2 launch robotiq_description bringup.launch.py ns:=gripper use_fake_hardware:=true
```

## Controlling the gripper
You can send commands to the gripper using the ros2 action interface:
```sh
ros2 action send_goal /robotiq_gripper_controller/gripper_cmd control_msgs/action/ParallelGripperCommand "{command: {name: ['robotiq_85_left_knuckle_joint'], position: [0.0]}}"
```
