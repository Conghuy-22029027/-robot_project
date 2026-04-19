import socket

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String


class CmdReceiverNode(Node):
    def __init__(self):
        super().__init__('cmd_receiver_node')

        self.declare_parameter('listen_ip', '0.0.0.0')
        self.declare_parameter('listen_port', 5005)
        self.declare_parameter('enable_log', False)

        self.listen_ip = self.get_parameter('listen_ip').get_parameter_value().string_value
        self.listen_port = self.get_parameter('listen_port').get_parameter_value().integer_value
        self.enable_log = self.get_parameter('enable_log').get_parameter_value().bool_value

        self.cmd_pub = self.create_publisher(Twist, '/robot/cmd_vel', 10)
        self.addr_pub = self.create_publisher(String, '/robot/laptop_addr', 10)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.listen_ip, self.listen_port))
        self.sock.setblocking(False)

        self.timer = self.create_timer(0.01, self.poll_udp)

        self.get_logger().info(
            f'cmd_receiver_node started, listening on {self.listen_ip}:{self.listen_port}'
        )
        self.get_logger().info('Publishing: /robot/cmd_vel')
        self.get_logger().info('Publishing: /robot/laptop_addr')

    def poll_udp(self):
        try:
            data, addr = self.sock.recvfrom(1024)
        except BlockingIOError:
            return
        except Exception as e:
            self.get_logger().error(f'UDP recv error: {e}')
            return

        line = data.decode(errors='ignore').strip()
        if not line:
            return

        try:
            if line.startswith('CMD,'):
                parts = line.split(',')
                if len(parts) != 3:
                    raise ValueError('Expected CMD,v,w')
                v = float(parts[1])
                w = float(parts[2])
            else:
                parts = line.split(',')
                if len(parts) != 2:
                    raise ValueError('Expected v,w')
                v = float(parts[0])
                w = float(parts[1])

            cmd_msg = Twist()
            cmd_msg.linear.x = v
            cmd_msg.angular.z = w
            self.cmd_pub.publish(cmd_msg)

            addr_msg = String()
            addr_msg.data = f'{addr[0]}:{addr[1]}'
            self.addr_pub.publish(addr_msg)

            if self.enable_log:
                self.get_logger().info(
                    f'Recv UDP {addr[0]}:{addr[1]} -> v={v:.3f}, w={w:.3f}'
                )

        except Exception as e:
            self.get_logger().warn(f'Invalid command "{line}": {e}')

    def destroy_node(self):
        try:
            self.sock.close()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CmdReceiverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
