import time

import serial


def print_array(matrixs):
    # matrixs = [[[1, 1], [1, 1], [1, 1]], [[1, 1], [1, 1], [1, 1]]]
    # 参数
    x_offset = 0
    y_offset = 0
    dot_size = 4
    pen_up = 5
    pen_down = -1
    travel_speed = 3000
    draw_speed = 3000
    character_space = 15
    max_characters = 9
    line_space = 25

    # 串口写入函数
    def write(sstr):
        strByte = bytes(sstr, "utf-8")
        ser.write(strByte)

    # 启动串口
    ser = serial.Serial("COM6", 115200)  # 将COM3修改为自己的串口
    time.sleep(0.5)

    # 初始化
    ser.write(b"G21\r\n")
    time.sleep(0.5)
    ser.write(b"G90\r\n")
    time.sleep(0.5)
    ser.write(b"G17\r\n")
    time.sleep(0.5)
    ser.write(b"M3 S1000\r\n")
    time.sleep(0.5)
    ser.write(b"G94\r\n")
    time.sleep(0.5)
    write(f"G92 X0 Y0 Z{pen_up}\r\n")
    time.sleep(0.5)
    # G21 ; 设置单位为毫米 G90使用绝对定位 G17设置为XY平面 M3 S1000主轴开启 G94每分钟给进 G92 X0 Y0 Z{pen_up}设置起始位置

    # 遍历矩阵并生成 G-code
    for z, matrix in enumerate(matrixs):
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                # CoreXY结构中，X = x + y, Y = x - y
                corexy_x = (-x) * dot_size + x_offset + (y * dot_size + y_offset)
                corexy_y = (-x) * dot_size + x_offset - (y * dot_size + y_offset)

                if val == 1:
                    write(f"G00 X{corexy_x} Y{corexy_y} F{travel_speed}\r\n")
                    time.sleep(0.9)
                    write(f"G00 Z{pen_down} F{draw_speed}\r\n")
                    time.sleep(0.9)
                    write(f"G00 Z{pen_up} F{travel_speed}\r\n")
                    time.sleep(1.8)

        if not (z + 1) % max_characters:
            y_offset += line_space
            x_offset += character_space * (max_characters - 1)
        else:
            x_offset -= character_space
        time.sleep(1.8)

    # 结束, 返回起始位置
    ser.write(b"G00 X0 Y0 Z10 F3000 \r\n")
    ser.close()
