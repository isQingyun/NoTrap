# coding: utf-8
import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import os
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode, urlparse
from wsgiref.handlers import format_date_time

import websocket


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, gpt_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(
            self.APISecret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding="utf-8")

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode(
            encoding="utf-8"
        )

        # 将请求的鉴权参数组合为字典
        v = {"authorization": authorization, "date": date, "host": self.host}
        # 拼接鉴权参数，生成url
        url = self.gpt_url + "?" + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws, ws1, ws2):
    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))


# 收到websocket消息的处理
def on_message(ws, message):
    message = json.loads(message)
    code = message["header"]["code"]
    if code != 0:
        print("### 请求出错： ", message)
    else:
        payload = message.get("payload")
        status = message["header"]["status"]
        if status == 2:
            print("### 合成完毕")
            ws.close()
        if payload and payload != "null":
            audio = payload.get("audio")
            if audio:
                audio = audio["audio"]
                with open(ws.save_file_name, "ab") as f:
                    f.write(base64.b64decode(audio))


def run(ws, *args):
    body = {
        "header": {"app_id": ws.appid, "status": 0},
        "parameter": {
            "oral": {"spark_assist": 1, "oral_level": "low"},
            "tts": {
                "vcn": ws.vcn,
                "speed": 50,
                "volume": 50,
                "pitch": 50,
                "bgs": 0,
                "reg": 0,
                "rdn": 0,
                "rhy": 0,
                "scn": 5,
                "version": 0,
                "L5SilLen": 0,
                "ParagraphSilLen": 0,
                "audio": {
                    "encoding": "lame",
                    "sample_rate": 16000,
                    "channels": 1,
                    "bit_depth": 16,
                    "frame_size": 0,
                },
                "pybuf": {"encoding": "utf8", "compress": "raw", "format": "plain"},
            },
        },
        "payload": {
            "text": {
                "encoding": "utf8",
                "compress": "raw",
                "format": "json",
                "status": 0,
                "seq": 0,
                "text": str(base64.b64encode(ws.text.encode("utf-8")), "UTF8"),
            }
        },
    }

    ws.send(json.dumps(body))


def str_to_mp3(appid, api_secret, api_key, url, text, vcn, save_file_name):
    wsParam = Ws_Param(appid, api_key, api_secret, url)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(
        wsUrl,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )
    websocket.enableTrace(False)
    ws.appid = appid
    ws.text = text
    ws.vcn = vcn
    ws.save_file_name = save_file_name
    if os.path.exists(ws.save_file_name):
        os.remove(ws.save_file_name)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


if __name__ == "__main__":
    str_to_mp3(
        appid="70b791ee",
        api_secret="M2M1ZTdhN2RlNTI5NTk2Y2RhOTNjNTMw",
        api_key="9ca4a8e057795e6a4d2a1a670915228e",
        url="wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/medd90fec",
        # 待合成文本
        text="我怎么能够把你来比作夏天？你不独比他可爱也比他温婉，狂风把五月宠爱的嫩蕊作践，夏天出赁的期限又未免太短。天上的眼睛有时照的太酷烈，他那炳耀的金颜又常遭掩蔽，被机缘或无常的天道所催折，没有芳艳不终于凋残或销毁，但你的长夏永远不会凋落。",
        # 发音人参数
        vcn="x4_lingxiaoxuan_oral",
        save_file_name="./test.mp3",
    )
