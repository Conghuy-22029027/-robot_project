# robot_project

Dự án phát triển hệ điều khiển từ xa song phương cho robot di động vi sai, theo hướng bilateral teleoperation.

## Mục tiêu
Xây dựng hệ thống điều khiển gồm:
- Laptop
- Raspberry Pi 3
- Arduino
- Robot di động vi sai
- LiDAR
- Haptic device (giai đoạn sau)

Hệ thống hướng tới:
- điều khiển robot từ xa
- nhận feedback từ robot
- bổ sung LiDAR để phát hiện vật cản
- sau này tích hợp force feedback và fictitious force / impedance

## Kiến trúc hiện tại
```text
Laptop -> Raspberry Pi 3 -> Arduino -> robot
Robot -> Arduino -> Raspberry Pi 3 -> laptop
