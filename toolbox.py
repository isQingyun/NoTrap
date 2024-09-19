import json
import os
import re

import cv2
import jieba
import pandas as pd
import pocketsphinx as ps
import pypinyin
import speech_recognition as sr
from PIL import Image
from playsound import playsound
from pydub import AudioSegment
from pytesseract import image_to_string
from tencentcloud.common import credential  # 这里需要安装腾讯翻译sdk
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import models, tmt_client

import speak
from braille_dict import *
from gcode_generator import print_array
from listen_wav import start_audio
from speak import str_to_mp3


class device:
    def __init__(self) -> None:
        self.lang_dict = {
            "chi_sim": "zh",
            "eng": "en",
            "fra": "fr",
            "deu": "de",
            "spa": "es",
            "jpn": "ja",
            "kor": "ko",
            "nld": "nl",
            "rus": "ru",
            "por": "pt",
            "ita": "it",
        }

    def read(self, image_name="test.jpg", image_path="", image_lang="chi_sim"):
        """read the image and return text

        :param image_name: the name of the image
        :type image_name: str
        :param image_path: the path of the image
        :type image_path: str
        :return: the text in the image
        :rtype: str
        :Example:
        >>> self.read("text.png", "Image/")
        hello world
        """
        input_text = image_to_string(
            Image.open(image_path + image_name), lang=image_lang
        )
        if image_lang == "chi_sim":
            input_text = re.sub("[\\sa-zA-Z0-9]", "", input_text.strip())
        else:
            input_text = re.sub("[^a-zA-Z\\x20]", "", input_text.strip())
        return input_text

    def translate(self, text, lang="eng"):
        """translate English text into Chinese

        :param text: the text to be translated
        :type text: str
        :return: the tranlation result
        :rtype: str
        :Example:
        >>> self.translate("hello world")
        你好世界
        """

        try:
            cred = credential.Credential(
                "YOURAPPID",
                "YOURAPPSECRET",
            )
            httpProfile = HttpProfile()
            httpProfile.endpoint = "tmt.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)

            req = models.TextTranslateRequest()
            req.SourceText = text  # 要翻译的语句
            # req.Source = "en"  # 源语言类型
            req.Source = self.lang_dict.get(lang, "en")  # 源语言类型
            req.Target = "zh"  # 目标语言类型
            req.ProjectId = 0

            resp = client.TextTranslate(req)
            data = json.loads(resp.to_json_string())
            return data["TargetText"]

        except TencentCloudSDKException as err:
            print(err)

    def speak(self, input_text):  # noqa: F811
        """receive text and generate human voice file in mp3 formation

        :param input_text: the text to be speak
        :type input_text: str
        :return: this function doesn't have return
        :rtype: None
        :Example:
        >>> self.speak("hello world")
        there will be no output here
        """
        str_to_mp3(
            appid="YOURAPPID",
            api_secret="YOURAPPSECRET",
            api_key="YOURAPIKEY",
            url="wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/medd90fec",
            # 待合成文本
            text=input_text,
            # 发音人参数
            vcn="x4_lingxiaoxuan_oral",
            save_file_name="./voice.mp3",
            # save_file_name="C:\\Users\\lockw\\Desktop\\NoTrap\\voice.mp3",
        )
        playsound("C:\\Users\\lockw\\Desktop\\NoTrap\\voice.mp3")

    def print_text(self, input_text="", text_lang="chi_sim"):
        """receive text and generate braille array

        :param input_text: the text to be printed
        :type input_text: str
        :param text_lang: the language of the text, default is Chinese
        :type text_lang: str
        :return: this function doesn't have return
        :rtype: None
        :Example:
        >>> self.print_text("hello world")
        there will be no output here
        """
        words = list(jieba.cut(input_text))
        print(words)
        braille_array = []  # 盲文点阵序列
        first_letter = []  # 声母序列
        final_letter = []  # 韵母序列
        for word in words:
            first_letter += pypinyin.pinyin(
                word, style=pypinyin.Style.INITIALS, heteronym=False
            )
            first_letter += [[" "]]
            final_letter += pypinyin.pinyin(
                word, style=pypinyin.Style.FINALS_TONE3, heteronym=False
            )
            final_letter += [[" "]]

        trans_map = {"g": "j", "k": "q", "h": "x"}

        for i in range(len(first_letter)):
            # 盲文变换规则
            if (
                first_letter[i][0] in ["z", "c", "s", "zh", "ch", "sh", "r"]
                and final_letter[i][0][:-1] == "i"
            ):
                final_letter[i][0] = final_letter[i][0][-1:]
            if first_letter[i][0] in ["g", "k", "h"] and final_letter[i][0][:-1] in [
                "i",
                "u",
                "v",
            ]:
                first_letter[i][0] = trans_map[first_letter[i][0]]

            first_array = first_letter_to_array.get(first_letter[i][0], None)  # noqa: F405
            if first_array is not None:
                braille_array += [first_array]
            final_array = final_letter_to_array.get(final_letter[i][0][:-1], None)  # noqa: F405
            if final_array is not None:
                braille_array += [final_array]
            tone_array = tone_to_array.get(final_letter[i][0][-1:], None)  # noqa: F405
            if tone_array is not None:
                braille_array += [tone_array]
        print(braille_array)
        print_array(braille_array)

    def get_text(self, input_text="", text_lang="chi_sim"):
        """receive text and generate braille array

        :param input_text: the text to be printed
        :type input_text: str
        :param text_lang: the language of the text, default is Chinese
        :type text_lang: str
        :return: this function doesn't have return
        :rtype: None
        :Example:
        >>> self.print_text("hello world")
        there will be no output here
        """
        words = list(jieba.cut(input_text))
        print(words)
        braille_array = []  # 盲文点阵序列
        first_letter = []  # 声母序列
        final_letter = []  # 韵母序列
        for word in words:
            first_letter += pypinyin.pinyin(
                word, style=pypinyin.Style.INITIALS, heteronym=False
            )
            first_letter += [[" "]]
            final_letter += pypinyin.pinyin(
                word, style=pypinyin.Style.FINALS_TONE3, heteronym=False
            )
            final_letter += [[" "]]

        trans_map = {"g": "j", "k": "q", "h": "x"}

        for i in range(len(first_letter)):
            # 盲文变换规则
            if (
                first_letter[i][0] in ["z", "c", "s", "zh", "ch", "sh", "r"]
                and final_letter[i][0][:-1] == "i"
            ):
                final_letter[i][0] = final_letter[i][0][-1:]
            if first_letter[i][0] in ["g", "k", "h"] and final_letter[i][0][:-1] in [
                "i",
                "u",
                "v",
            ]:
                first_letter[i][0] = trans_map[first_letter[i][0]]

            first_array = first_letter_to_array.get(first_letter[i][0], None)  # noqa: F405
            if first_array is not None:
                braille_array += [first_array]
            final_array = final_letter_to_array.get(final_letter[i][0][:-1], None)  # noqa: F405
            if final_array is not None:
                braille_array += [final_array]
            tone_array = tone_to_array.get(final_letter[i][0][-1:], None)  # noqa: F405
            if tone_array is not None:
                braille_array += [tone_array]
        print(braille_array)
        return braille_array

    def convert_mp3_to_wav(self, mp3_file, wav_file):
        """convert mp3 file to wav file

        :param mp3_file: the path of the mp3 file
        :type mp3_file: str
        :param wav_file: the path of the wav file
        :type wav_file: str
        :return: this function doesn't have return
        :rtype: None
        :Example:
        >>> self.convert_mp3_to_wav("C:\\Users\\lockw\\Desktop\\NoTrap\\hello.mp3", "C:\\Users\\lockw\\Desktop\\NoTrap\\hello.wav")
        there will be no output here
        """
        audio = AudioSegment.from_mp3(mp3_file)
        audio.export(wav_file, format="wav")

    # 识别WAV文件中的语音
    def recognize_audio(self, wav_file):
        """recognize the voice in the wav file

        :param wav_file: the path of the wav file
        :type wav_file: str
        :return: the recognized text
        :rtype: str
        :Example:
        >>> self.recognize_audio("C:\\Users\\lockw\\Desktop\\NoTrap\\hello.wav")
        你好
        """
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language="zh-CN")
                return text
            except sr.UnknownValueError:
                return "无法识别语音"
            except sr.RequestError as e:
                return f"请求出错； {e}"


if __name__ == "__main__":
    myDev = device()
    myDev.print_text("硬件设计大赛")
    # 读取单个图片并提取文字
    # text = myDev.read(
    #     "image_6.png",
    #     "C:\\Users\\lockw\\Desktop\\NoTrap\\img\\",
    #     "chi_sim",
    # )
    # print(text)

    # # 读取多个图片并提取文字
    # text = []
    # for i in range(12, 19):
    #     text += [
    #         myDev.read(
    #             f"image_{i}-ps-ps.png",
    #             "C:\\Users\\lockw\\Desktop\\NoTrap\\img\\",
    #             "eng",
    #         )
    #     ]
    # print(text)
    # output = max(text, key=len, default="")
    # print(output)

    # 语音识别
    # text = myDev.recognize_audio("C:\\Users\\lockw\\Desktop\\NoTrap\\hello.wav")
    # print(f"文本识别： {text}")

    # 调用api在线翻译英文文本
    # print(myDev.translate(text))
    # 根据输入的文本，在同一文件夹下生成人声朗读的mp3文件
    # myDev.speak("I can't speak ")
    #     "燕子去了，有再来的时候；杨柳枯了，有再青的时候；桃花谢了，有再开的时候。但是，聪明的，你告诉我，我们的日子为什么一去不复返呢？"
    # )
    # 基于智能分词系统，将中文文本分词后转换成特殊风格的拼音，并插入空格，便于之后的盲文打印
    # test_text = "我们知道,我们终会知道。"
    # # print(myDev.text_to_pinyin(test_text))
    # myDev.print_text(test_text)

    # # 测试语音转文字功能
    # mp3_file = "C:\\Users\\lockw\\Desktop\\NoTrap\\hello.mp3"
    # wav_file = "C:\\Users\\lockw\\Desktop\\NoTrap\\hello.wav"
    # myDev.convert_mp3_to_wav(mp3_file, wav_file)
    # result = myDev.recognize_audio(wav_file)
    # print("识别结果：", result)
