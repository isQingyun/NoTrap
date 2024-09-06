# 说明文档
## 概述
该设备的主要函数封装在device类下，下面依次介绍device中的功能函数。
## 函数&功能
1. single_search函数
采用github开源的`word_translation.csv`和`word.csv`文件，直接使用单个单词作为索引搜索数据库，并返回单词的中文释义及英式、美式发音
2. read函数
基于Google赞助的开源OCR引擎tesseract实现的根据图像识别大段本文功能
3. translate函数
自动调用开发者在腾讯云注册的api，可以在线上对英文文本进行翻译
4. speak函数
调用讯飞开放的api，利用讯飞开发的超拟人合成技术生成高度接近人声的音频文件，大大提高了文本转语音效果
5. text_to_pinyin函数
对输入的中文文本进行基于jieba的智能分词，分词之后使用pypinyin库转换成带调拼音，实现盲文打印的部分预处理工作