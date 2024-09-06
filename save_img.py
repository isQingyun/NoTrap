import os
import sys
import time

import cv2
import numpy as np
import serial

# 定义保存图像的目录路径
save_directory = r"C:\Users\lockw\Desktop\NoTrap\img"
# 使用默认串口端口（例如 'COM3' 或 '/dev/ttyUSB0'）
serial_port = sys.argv[1] if len(sys.argv) > 1 else "COM5"


def parse_image(data):
    image_start_marker = b"RDY"  # 图像开始标记

    width = 320
    height = 240

    size = width * height

    while len(data) > 0 and data[:3] != image_start_marker:
        data = data[1:]

    if len(data) < (size + 3) or data[:3] != image_start_marker:
        return data, None

    data = data[3:]
    buffer = data[:size]
    data = data[size:]

    img = np.frombuffer(buffer, dtype=np.uint8)
    img = np.reshape(img, (height, width))

    return data, img


try:
    ser = serial.Serial(port=serial_port, baudrate=1000000)
    print(f"Successfully opened port {serial_port}")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)

# 初始化数据变量和图像计数器
data = b""
image_counter = 0

while True:
    try:
        data, img = parse_image(data)
        if img is not None:
            # 确保目录存在，如果不存在则创建
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
            # 生成文件名并保存图像
            filename = os.path.join(save_directory, f"image_{image_counter}.png")

            cv2.imwrite(filename, img)
            print(f"Saved {filename}")
            image_counter += 1
            # 添加短暂延迟
            # time.sleep(0.1)
        # ser.reset_input_buffer()  # 清空缓冲区
        snap = ser.read(5120)
        print(f"Read {len(snap)} bytes")
        if len(snap) == 0:
            print(0)
            continue

        data += snap

    except serial.SerialException as e:
        print(f"Serial error: {e}")
        break
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        break
