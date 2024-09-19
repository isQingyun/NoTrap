# -*- coding: UTF-8 -*-
import os

from PIL import Image, ImageEnhance


# 原始图像
def ImageAugument(img_path):
    # filepath = r'E:/PycharmProjects/image_cluster-master/data/smoke_call/train/1'  # 文件夹目录
    if not os.path.exists(img_path):
        print(f" path {img_path} does not exist.")
        return
    files = os.listdir(img_path)  # 得到文件夹下的所有文件名称
    # # 遍历文件夹
    prefix = img_path + "/"
    for file in files:
        # print(file)
        image = Image.open(prefix + file)
        enh_bri = ImageEnhance.Brightness(image)

        brightness = 2  # 1.5
        image_brightened = enh_bri.enhance(brightness)
        # image_brightened.save(prefix + file.strip(".png") + "-lightup" + ".png")

        enh_col = ImageEnhance.Color(image_brightened)
        color = 0.8
        image_colored = enh_col.enhance(color)
        # 对比度增强
        enh_con = ImageEnhance.Contrast(image_colored)
        contrast = 1.5
        image_contrasted = enh_con.enhance(contrast)
        # image_contrasted.save(prefix + file.strip(". png") + "-contrastup" + ".png")

        # 锐度增强
        enh_sha = ImageEnhance.Sharpness(image_contrasted)
        sharpness = 1.5  # 3.0
        image_sharped = enh_sha.enhance(sharpness)

        enh_bri = ImageEnhance.Brightness(image_sharped)
        image_sharped.save(img_path.strip(".png") + "-ps" + ".png")
        # img_path = img_path.strip(".png") + "-ps" + ".png"


if __name__ == "__main__":
    ImageAugument(r"C:\Users\lockw\Desktop\NoTrap\img")
# 调两遍可以达成翻译的效果
