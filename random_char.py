import random
import unicodedata


def get_Rchar():
    # 读取文件中的常用汉字
    with open("demo.txt", "r", encoding="utf-8") as f:
        common_chars = f.read()
        # 去除空格
        common_chars = common_chars.replace(" ", "")
        common_chars = common_chars.strip()

        # 创建字符映射表
        translator = {
            ord(c): None
            for c in common_chars
            if unicodedata.category(c).startswith("P")
        }

        # 使用字符映射表去除标点符号
        s = common_chars.translate(translator)

    return random.choice(s)


if __name__ == "__main__":
    print(get_Rchar())
