import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32  # もしくは必要に応じてカスタムメッセージタイプを使用
import json, datetime, re, serial

class UDCO2Publisher(Node):
    def __init__(self, dev="/dev/ttyACM0"):
        super().__init__('udco2_publisher')
        self.publisher_ = self.create_publisher(Int32, 'co2ppm', 10)  # トピック名とタイプは必要に応じて調整してください
        self.dev = dev
        self.timer_period = 0.5  # 秒
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

    def timer_callback(self):
        regex = re.compile(r'CO2=(?P<co2>\d+),HUM=(?P<hum>\d+\.\d+),TMP=(?P<tmp>-?\d+\.\d+)')
        with serial.Serial(self.dev, 115200, timeout=6) as conn:
            conn.write("STA\r\n".encode())
            conn.readline()  # "OK STA" メッセージを読み込んでいるが、表示はしない
            line = conn.readline().decode().strip()
            m = regex.match(line)
            if m is not None:
                co2ppm = Int32()
                co2ppm.data = int(m.group("co2"))
                self.publisher_.publish(co2ppm)
                self.get_logger().info('Publishing: "%s"' % co2ppm.data)
            # conn.write("STP\r\n")  # このコマンドは通常、ループの外で一度だけ送信するべきです

def main(args=None):
    rclpy.init(args=args)
    udco2_publisher = UDCO2Publisher()
    rclpy.spin(udco2_publisher)
    udco2_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
