import socket

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class FeedbackSenderNode(Node):
    def __init__(self):
        super().__init__('feedback_sender_node')

        self.declare_parameter('enable_log', False)
        self.enable_log = self.get_parameter('enable_log').get_parameter_value().bool_value

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.laptop_ip = None
        self.laptop_port = None

        self.addr_sub = self.create_subscription(
            String,
            '/robot/laptop_addr',
            self.addr_callback,
            10
        )

        self.feedback_sub = self.create_subscription(
            String,
            '/robot/feedback_raw',
            self.feedback_callback,
            10
        )

        self.get_logger().info('feedback_sender_node started')
        self.get_logger().info('Subscribed : /robot/laptop_addr')
        self.get_logger().info('Subscribed : /robot/feedback_raw')

    def addr_callback(self, msg: String):
        text = msg.data.strip()
        if ':' not in text:
            self.get_logger().warn(f'Invalid laptop address: {text}')
            return

        ip, port_str = text.rsplit(':', 1)
        try:
            port = int(port_str)
        except ValueError:
            self.get_logger().warn(f'Invalid laptop port: {text}')
            return

        self.laptop_ip = ip
        self.laptop_port = port
        self.get_logger().info(f'Updated laptop addr -> {self.laptop_ip}:{self.laptop_port}')

    def feedback_callback(self, msg: String):
        if self.laptop_ip is None or self.laptop_port is None:
            return

        line = msg.data.strip()
        if not line:
            return

        try:
            self.sock.sendto(
                (line + '\n').encode('utf-8'),
                (self.laptop_ip, self.laptop_port)
            )
            if self.enable_log:
                self.get_logger().info(f'Sent to laptop: {line}')
        except Exception as e:
            self.get_logger().error(f'UDP send error: {e}')

    def destroy_node(self):
        try:
            self.sock.close()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = FeedbackSenderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
