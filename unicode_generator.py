def array_to_unicode(text_array):
    """将二维数组转换为unicode字符串

    :param text_array: 二维数组
    :return: unicode字符串
    """
    unicode_string = ""
    for char_array in text_array:
        unicode_order = 10240  # 初始化unicode序列

        for i in range(3):
            for j in range(2):
                unicode_order += 2 ** (i + j * 3) * char_array[i][j]
        unicode_string += chr(unicode_order)
    return unicode_string


def unicode_to_array(unicode_string):
    """将unicode字符串转换为二维数组

    :param unicode_string: unicode字符串
    :return: 二维数组
    """
    text_array = []
    for unicode_char in unicode_string:
        unicode_order = ord(unicode_char) - 10240
        unicode_bin_order = bin(unicode_order)[2:].zfill(6)
        text_array.append(
            [
                [int(unicode_bin_order[5]), int(unicode_bin_order[2])],
                [int(unicode_bin_order[4]), int(unicode_bin_order[1])],
                [int(unicode_bin_order[3]), int(unicode_bin_order[0])],
            ]
        )

    return text_array


if __name__ == "__main__":
    test_array = [[[0, 0], [1, 1], [0, 0]]]
    test_unicode = array_to_unicode(test_array)
    print(test_unicode)
    print(unicode_to_array(test_unicode))
