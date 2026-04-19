import serial

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String


class SerialBridgeNode(Node):
    def __init__(self):
        super().__init__('serial_bridge_node')

        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('enable_log', False)

        self.port = self.get_parameter('port').get_parameter_value().string_value
        self.baudrate = self.get_parameter('baudrate').get_parameter_value().integer_value
        self.enable_log = self.get_parameter('enable_log').get_parameter_value().bool_value

        self.ser = None
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.01)
            self.get_logger().info(f'Opened serial {self.port} at {self.baudrate}')
        except Exception as e:
            self.get_logger().error(f'Cannot open serial: {e}')
            self.ser = None

        self.cmd_sub = self.create_subscription(
            Twist,
            '/robot/cmd_vel',
            self.cmd_callback,
            10
        )

        self.feedback_pub = self.create_publisher(
            String,
            '/robot/feedback_raw',
            10
        )

        self.timer = self.create_timer(0.01, self.read_serial)

        self.get_logger().info('Subscribed : /robot/cmd_vel')
        self.get_logger().info('Publishing : /robot/feedback_raw')

    def cmd_callback(self, msg: Twist):
        if self.ser is None:
            return

        v = msg.linear.x
        w = msg.angular.z
        cmd_str = f'CMD,{v:.3f},{w:.3f}\n'

        try:
            self.ser.write(cmd_str.encode('utf-8'))
            if self.enable_log:
                self.get_logger().info(f'To Arduino: {cmd_str.strip()}')
        except Exception as e:
            self.get_logger().error(f'Serial write error: {e}')

    def read_serial(self):
        if self.ser is None:
            return

        try:
            while self.ser.in_waiting > 0:
                line = self.ser.readline().decode(errors='ignore').strip()
                if line:
                    msg = String()
                    msg.data = line
                    self.feedback_pub.publish(msg)
                    if self.enable_log:
                        self.get_logger().info(f'From Arduino: {line}')
        except Exception as e:
            self.get_logger().error(f'Serial read error: {e}')

    def destroy_node(self):
        if self.ser is not None:
            try:
                self.ser.close()
            except Exception:
                pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SerialBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
