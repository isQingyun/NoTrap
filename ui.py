import subprocess
import sys
import threading
import tkinter as tk
from collections import deque
from tkinter import messagebox, ttk

import cv2
import serial

# import pyautogui
#
#
import win32gui

from braille_dict import array_to_pinyin
from gcode_generator import print_array

# from listen_wav import start_audio
from random_char import get_Rchar
from toolbox import device
from unicode_generator import array_to_unicode, unicode_to_array


class win1(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("无障碍模式")
        self.geometry("550x600")
        self.myDev = device()
        self.create_widgets()
        self.func = {
            "一键输出": self.on_button_click,
            "1.图片显示": self.show_click,
            "2.翻译结果": self.tran_click,
            "3.盲文打印": self.print_click,
            "打印输入": self.print_input_click,
            "返回首页": self.go_back,
        }
        self.lan_dict = {"chi_sim": "中文", "eng": "英文", "jpn": "日文", "fra": "法语"}
        self.serial_port = sys.argv[1] if len(sys.argv) > 1 else "COM8"
        self.start_serial_thread()  # 摇杆串口通信
        self.myDev.speak("您已进入无障碍模式")

    def create_widgets(self):
        self.frm = tk.Frame(self)
        self.frm.grid(padx=20, pady=10, columnspan=3)

        self.bt_total = tk.Button(
            self.frm, text="一键输出", command=self.on_button_click, state="disabled"
        )
        self.bt_total.grid(row=1, column=0, ipadx=3, ipady=5, padx=10, pady=10)
        self.bt_show = tk.Button(
            self.frm, text="1.图片显示", command=self.show_click, state="disabled"
        )
        self.bt_show.grid(row=1, column=1, ipadx=3, ipady=5, padx=10, pady=10)
        self.bt_tran = tk.Button(
            self.frm, text="2.翻译结果", command=self.tran_click, state="disabled"
        )
        self.bt_tran.grid(row=1, column=2, ipadx=3, ipady=5, padx=10, pady=10)
        self.bt_print = tk.Button(
            self.frm, text="3.盲文打印", command=self.print_click, state="disabled"
        )
        self.bt_print.grid(row=1, column=3, ipadx=3, ipady=5, padx=10, pady=10)
        self.language = tk.Label(
            self.frm, text="输入语言", wraplength=80, justify="left"
        )
        self.language.grid(row=0, column=0, ipadx=3, ipady=5, padx=10, pady=10)
        self.type = tk.StringVar()
        self.choice_ch = ttk.Radiobutton(
            self.frm,
            text="中文",
            variable=self.type,
            value="chi_sim",
            command=self.type_choice,
            state="active",
        )
        self.choice_ch.grid(
            row=0,
            column=1,
            ipadx=3,
            ipady=5,
            padx=10,
            pady=10,  # columnspan=3
        )
        self.choice_eg = ttk.Radiobutton(
            self.frm,
            text="英文",
            variable=self.type,
            value="eng",
            command=self.type_choice,
            state="active",
        )
        self.choice_eg.grid(row=0, column=2, ipadx=3, ipady=5, padx=10, pady=10)
        self.choice_jp = ttk.Radiobutton(
            self.frm,
            text="日文",
            variable=self.type,
            value="jpn",
            command=self.type_choice,
            state="active",
        )
        self.choice_jp.grid(row=0, column=3, ipadx=3, ipady=5, padx=10, pady=10)
        self.choice_fr = ttk.Radiobutton(
            self.frm,
            text="法文",
            variable=self.type,
            value="fra",
            command=self.type_choice,
            state="active",
        )
        self.choice_fr.grid(row=0, column=4, ipadx=3, ipady=5, padx=10, pady=10)
        self.label_input = tk.Label(
            self.frm, text="输入文本", wraplength=80, justify="left"
        )
        self.label_input.grid(row=3, column=0, ipadx=3, ipady=5, padx=10, pady=10)
        self.inputbox = tk.Entry(self.frm, width=20, state="disabled")
        self.inputbox.grid(
            row=3,
            column=1,
            ipadx=3,
            ipady=5,
            padx=10,
            pady=10,
            columnspan=3,
            sticky="w",
        )
        self.bt_input = tk.Button(
            self.frm, text="打印输入", state="disabled", command=self.print_input_click
        )
        self.bt_input.grid(row=3, column=3, ipadx=3, ipady=5, padx=10, pady=10)
        self.bt_back = tk.Button(self.frm, text="返回首页", command=self.go_back)
        self.bt_back.grid(row=4, column=0, ipadx=3, ipady=5, padx=10, pady=10)
        self.widgets = [
            self.choice_ch,
            self.choice_eg,
            self.choice_jp,
            self.choice_fr,
            self.bt_total,
            self.bt_show,
            self.bt_tran,
            self.bt_print,
            self.inputbox,
            self.bt_input,
            self.bt_back,
        ]
        self.bind_widgets()

    def bind_widgets(self):
        for widget in self.widgets:
            widget.bind("<Tab>", self.on_tab)
            widget.bind("<Shift-Tab>", self.on_shift_tab)
            widget.bind("<Shift-Return>", self.on_shift)
            widget.bind("<Return>", self.on_return)
        self.widgets[0].focus_set()

    def on_tab(self, event):
        event.widget.tk_focusNext().focus_set()
        return "break"

    def on_shift_tab(self, event):
        event.widget.tk_focusPrev().focus_set()
        return "break"

    def on_shift(self, event):
        widget = event.widget
        if isinstance(widget, tk.Entry):
            if self.type.get() == "chi_sim":
                content = "中文"
            elif self.type.get() == "eng":
                content = "英文"
            self.myDev.speak("当前是文本输入框,请输入你的" + content + "文本")
        else:
            self.myDev.speak("当前选项是" + widget["text"])
        return "break"

    def on_return(self, event):
        widget = event.widget
        if isinstance(widget, tk.Button):
            if widget["text"] == "返回首页":
                # 关闭可能存在的串口连接
                if hasattr(self, "ser") and self.ser is not None:
                    self.ser.close()

                self.destroy()
                # # 关闭可能存在的线程
                # if (
                #     hasattr(self, "serial_thread")
                #     and self.serial_thread is not None
                #     and self.serial_thread.is_alive()
                # ):
                #     self.serial_thread.join()
                Homepage(1)
            else:
                command = self.func[widget["text"]]
                # print(command)
                command()
        elif isinstance(widget, ttk.Radiobutton):
            self.type.set(widget.cget("value"))
            self.type_choice()
        return "break"

    def handle_serial_data(self, data):
        if data == "DN":
            self.event_generate("<Shift-Tab>")
        elif data == "UP":
            self.event_generate("<Tab>")
        elif data == "EN":
            self.event_generate("<Return>")
        else:
            self.event_generate("<Shift-Return>")

    def execute_script(self, script_path):
        try:
            result = subprocess.run(
                ["python", script_path], capture_output=True, text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"脚本执行失败: {e.output}")
            return None

    def print_input_click(self):
        if self.inputbox.get() == "":
            # messagebox.showerror("错误", "输入不能为空")
            self.myDev.speak("错误,输入不能为空")
        else:
            self.output = self.inputbox.get()
            if self.type.get() == "chi_sim":
                # messagebox.showinfo("识别结果", f"中文识别:\n{self.output}")
                self.myDev.speak("中文输入" + self.output)
                self.myDev.print_text(self.output, self.type.get())
            else:
                self.tran = self.myDev.translate(self.output, self.type.get())
                # messagebox.showinfo("识别结果", f"英文识别:\n{self.output}\n中文翻译:\n{self.tran}")
                self.myDev.speak(
                    f"{self.lan_dict[self.type.get()]}输入:"
                    + self.output
                    + ",中文翻译:"
                    + self.tran
                )
                self.myDev.print_text(self.tran, self.type.get())
            self.inputbox.delete(0, tk.END)
            self.myDev.speak("打印完成,电机正在归位")

    def type_choice(self):
        if (
            self.type.get() == "chi_sim"
            or self.type.get() == "eng"
            or self.type.get() == "jpn"
            or self.type.get() == "fra"
        ):
            self.myDev.speak(f"您选择的是{self.lan_dict[self.type.get()]}")
            print(f"您选择的是{self.lan_dict[self.type.get()]}")
            self.bt_show.config(state="normal")
            self.bt_total.config(state="normal")
            self.bt_tran.config(state="disabled")
            self.bt_print.config(state="disabled")
            self.inputbox.config(state="normal")
            self.bt_input.config(state="normal")
        # elif self.type.get() == "eng":
        #     self.myDev.speak("您选择的是英文")
        #     self.bt_show.config(state="normal")
        #     self.bt_total.config(state="normal")
        #     self.inputbox.config(state="normal")
        #     self.bt_input.config(state="normal")
        else:
            self.bt_show.config(state="disabled")

    def on_button_click(self):
        self.show_click()
        self.bt_tran.config(state="disabled")
        self.bt_print.config(state="disable")
        self.bt_show.config(state="normal")
        self.bt_total.focus_set()
        self.range_tran()
        if self.type.get() == "chi_sim":
            self.myDev.speak("中文识别" + self.output)
            self.myDev.print_text(self.output, self.type.get())
        elif self.type.get() == "eng":
            self.tran = self.myDev.translate(self.output)
            self.myDev.speak(
                f"{self.lan_dict[self.type.get()]}识别:"
                + self.output
                + ",中文翻译:"
                + self.tran
            )
            self.myDev.print_text(self.tran, self.type.get())
        self.myDev.speak("打印完成,电机正在归位")

    def show_click(self):
        imgout = cv2.imread(
            r"C:\Users\lockw\Desktop\NoTrap\img\image_15.png",
        )  # C:\Users\lockw\Desktop\NoTrap\img\image_15.png
        cv2.imshow("captured image", imgout)
        self.bt_tran.config(state="normal")
        self.bt_show.tk_focusNext().focus_set()
        self.bt_show.config(state="disable")
        cv2.waitKey(2000)
        self.myDev.speak("图片显示结果")
        cv2.waitKey(2000)
        cv2.destroyAllWindows()

    def tran_click(self):
        self.range_tran()
        if self.type.get() == "chi_sim":
            # messagebox.showinfo("识别结果", f"中文识别:\n{self.output}")
            self.myDev.speak("中文识别" + self.output)
        elif self.type.get() == "eng":
            self.tran = self.myDev.translate(self.output)
            # messagebox.showinfo(
            #     "识别结果", f"英文识别:\n{self.output}\n中文翻译:\n{self.tran}"
            # )
            self.myDev.speak("英文识别:" + self.output + ",中文翻译:" + self.tran)
        self.bt_print.config(state="normal")
        self.bt_tran.tk_focusNext().focus_set()
        self.bt_tran.config(state="disable")

    def print_click(self):
        if self.type.get() == "chi_sim":
            print(self.output)
            self.myDev.print_text(self.output, self.type.get())
        elif self.type.get() == "eng":
            print(self.tran)
            self.myDev.print_text(self.tran, self.type.get())
        # messagebox.showinfo("打印结果", "打印完成！")
        self.myDev.speak("打印完成,电机正在归位")
        self.bt_show.config(state="normal")
        self.bt_print.tk_focusNext().focus_set()
        self.bt_print.config(state="disable")

    def range_tran(self):
        text = []
        for i in range(12, 19):
            text += [
                self.myDev.read(
                    f"image_{i}-ps-ps.png",
                    "C:\\Users\\lockw\\Desktop\\NoTrap\\img\\",
                    self.type.get(),
                )
            ]
        self.output = max(text, key=len, default="")

    def start_serial_thread(self):
        try:
            self.ser = serial.Serial(port=self.serial_port, baudrate=9600)
            self.ser.timeout = 1
            print(f"Successfully opened port {self.serial_port}")
            self.serial_thread = threading.Thread(target=self.serial_communication)
            self.serial_thread.start()
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)

    def serial_communication(self):
        self.serial_data = b""
        while True:
            try:
                snap = self.ser.read(8)
                if len(snap) == 0:
                    continue
                self.serial_data += snap
                self.serial_word = self.parse_data()
                if self.serial_word is not None:
                    print(self.serial_word.decode("utf-8"))
                    self.handle_serial_data(self.serial_word.decode("utf-8"))
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break

    def parse_data(self):
        start_marker = b"RY"
        size = 2
        while len(self.serial_data) > 0 and self.serial_data[:2] != start_marker:
            self.serial_data = self.serial_data[1:]
        if len(self.serial_data) < (size + 2) or self.serial_data[:2] != start_marker:
            return None
        self.serial_data = self.serial_data[4:]
        getData = self.serial_data[:size]
        self.serial_data = self.serial_data[size + 2 :]
        return getData

    def go_back(self):
        # 关闭可能存在的串口连接
        if hasattr(self, "ser") and self.ser is not None:
            self.ser.close()
        # 关闭可能存在的线程
        if (
            hasattr(self, "serial_thread")
            and self.serial_thread is not None
            and self.serial_thread.is_alive()
        ):
            self.serial_thread.join()
        self.destroy()
        Homepage(1)


class win2(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("学习模式")
        self.geometry("550x600")
        self.myDev = device()
        self.lan_dict = {"中文": "chi_sim", "英文": "eng"}
        self.lan_dict = {
            "中文": "chi_sim",
            # "中文繁体": "chi_tra",
            "英文": "eng",
            "法语": "fra",
            "德语": "deu",
            "西班牙语": "spa",
            "日语": "jpn",
            "韩语": "kor",
            "荷兰语": "nld",
            "俄语": "rus",
            "葡萄牙语": "por",
            "意大利语": "ita",
        }
        self.array_serial_port = "COM11"  # 盲文输入
        # self.hand_serial_port = "COM4"  # 手势识别
        self.queue = deque(maxlen=20)  # 设置队列长度，可以根据实际情况调整
        self.create_widgets()

    def create_widgets(self):
        self.frm = tk.Frame(self)
        self.frm.grid(padx=20, pady=10, columnspan=3)
        self.language = tk.Label(
            self.frm, text="输入语言", wraplength=80, justify="left"
        )
        self.language.grid(row=0, column=0, ipadx=3, ipady=5, padx=10, pady=10)
        self.type = tk.StringVar()
        self.choice_lan = ttk.Combobox(
            self.frm, textvariable=self.type, state="readonly", width=20
        )  # entry
        self.choice_lan["values"] = tuple(self.lan_dict)
        self.choice_lan.current(0)
        self.choice_lan.grid(row=0, column=1, ipadx=3, ipady=5, padx=10, pady=10)
        self.label_input = tk.Label(
            self.frm, text="输入文本", wraplength=80, justify="left"
        )
        self.label_input.grid(row=1, column=0, ipadx=3, ipady=5, padx=10, pady=10)
        self.inputbox = tk.Entry(
            self.frm,
            width=20,
        )
        self.inputbox.grid(
            row=1,
            column=1,
            ipadx=3,
            ipady=5,
            padx=10,
            pady=10,
            columnspan=3,
            sticky="w",
        )
        self.bt_showarray = tk.Button(
            self.frm, text="盲文显示", command=self.bt_showarray_click
        )
        self.bt_showarray.grid(row=1, column=2, ipadx=3, ipady=5, padx=10, pady=10)
        self.bt_translate = tk.Button(
            self.frm, text="翻译显示", command=self.bt_translate_click
        )
        self.bt_translate.grid(row=1, column=3, ipadx=3, ipady=5, padx=10, pady=10)
        self.bt_random = tk.Button(
            self.frm,
            text="盲文单词\n随机学习",
            command=self.randomPrint,
        )
        self.bt_random.grid(row=2, column=0, ipadx=3, ipady=5, padx=10, pady=10)
        self.entrybox = tk.Entry(self.frm, width=20, state="disabled")
        self.entrybox.grid(
            row=2,
            column=1,
            ipadx=3,
            ipady=5,
            padx=10,
            pady=10,
            sticky="w",
        )
        # self.bt_voiceInput = tk.Button(
        #     self.frm, text="语言输入", command=self.voiceInput, state="disabled"
        # )
        # self.bt_voiceInput.grid(row=2, column=2, ipadx=3, ipady=5, padx=10, pady=10)
        self.bt_verify = tk.Button(
            self.frm, text="开始验证", command=self.entryVerify, state="disabled"
        )
        self.bt_verify.grid(row=2, column=2, ipadx=3, ipady=5, padx=10, pady=10)
        self.label_show = tk.Label(
            self.frm,
            text="结果预览",
            wraplength=80,
            justify="left",
        )
        self.label_show.grid(row=3, column=0, ipadx=3, ipady=5, padx=10, pady=10)
        self.showbox = tk.Entry(
            self.frm, width=10, font=("Times", 20, "bold"), state="readonly"
        )  # font=(16, "bold")
        self.showbox.grid(
            row=3,
            column=1,
            ipadx=3,
            ipady=0,
            padx=10,
            pady=10,
            columnspan=3,
            sticky="w",
        )
        self.bt_printarray = tk.Button(
            self.frm, text="结果打印", command=self.bt_printarray_click
        )
        self.bt_printarray.grid(row=3, column=2, ipadx=3, ipady=5, padx=10, pady=10)
        self.bt_clearshow = tk.Button(
            self.frm,
            text="清空输入",
            command=lambda: self.bt_cleararray_click(self.showbox),
        )
        self.bt_clearshow.grid(row=3, column=3, ipadx=3, ipady=5, padx=10, pady=10)
        # self.label_hand = tk.Label(self.frm, text="手语识别")
        # self.label_hand.grid(row=4, column=0, ipadx=3, ipady=5, padx=10, pady=10)
        # self.showhand = tk.Entry(self.frm, width=20, state="readonly")
        # self.showhand.grid(
        #     row=4,
        #     column=1,
        #     ipadx=3,
        #     ipady=5,
        #     padx=10,
        #     pady=10,
        #     sticky="w",
        # )
        # self.bt_starthand = tk.Button(
        #     self.frm, text="开始识别", command=self.bt_starthand_click
        # )
        # self.bt_starthand.grid(row=4, column=2, ipadx=3, ipady=5, padx=10, pady=10)

        # self.bt_endhand = tk.Button(
        #     self.frm, text="关闭识别", command=self.bt_endhand_click
        # )
        # self.bt_endhand.grid(row=4, column=3, ipadx=3, ipady=5, padx=10, pady=10)
        self.label_array = tk.Label(self.frm, text="盲文输入")
        self.label_array.grid(row=4, column=0, ipadx=3, ipady=5, padx=10, pady=10)
        self.showarray = tk.Entry(
            self.frm, width=10, font=("Times", 20, "bold"), state="readonly"
        )
        self.showarray.grid(
            row=4,
            column=1,
            ipadx=3,
            ipady=5,
            padx=10,
            pady=10,
            sticky="w",
        )
        self.bt_startarray = tk.Button(
            self.frm, text="开始输入", command=self.bt_startarray_click
        )
        self.bt_startarray.grid(row=4, column=2, ipadx=3, ipady=5, padx=10, pady=10)

        self.bt_endarray = tk.Button(
            self.frm,
            text="清空输入",
            command=lambda: self.bt_cleararray_click(self.showarray),
        )
        self.bt_endarray.grid(row=4, column=3, ipadx=3, ipady=5, padx=10, pady=10)
        self.bt_translatearray = tk.Button(
            self.frm,
            text="翻译输入",
            command=self.bt_translatearray_click,
        )
        self.bt_translatearray.grid(row=4, column=4, ipadx=3, ipady=5, padx=10, pady=10)
        self.bt_back = tk.Button(self.frm, text="返回首页", command=self.go_back)
        self.bt_back.grid(row=5, column=0, ipadx=3, ipady=5, padx=10, pady=10)

    def bt_printarray_click(self):
        if self.showbox.get() == "":
            messagebox.showerror("错误", "输入不能为空")
        else:
            print_array(unicode_to_array(self.showbox.get()))
            messagebox.showinfo("提示", "打印完成,电机正在归位")

    def bt_showarray_click(self):
        # input =
        # self.inputbox.delete(0, tk.END)
        tran = self.myDev.translate(self.inputbox.get(), self.lan_dict[self.type.get()])
        self.showbox.config(state="normal")
        self.showbox.delete(0, tk.END)
        self.showbox.insert(
            0,
            array_to_unicode(self.myDev.get_text(tran, self.lan_dict[self.type.get()])),
        )
        self.showbox.config(state="disabled")

    def bt_translate_click(self):
        if self.inputbox.get() == "":
            messagebox.showerror("错误", "输入不能为空")
        else:
            self.output = self.inputbox.get()
            if self.type.get() == "中文":
                if not messagebox.askokcancel(
                    "确认信息",
                    "中文输入：" + self.output,
                ):
                    # self.myDev.print_text(self.output, self.lan_dict[self.type.get()])
                    self.inputbox.delete(0, tk.END)
            else:
                self.tran = self.myDev.translate(
                    self.output, self.lan_dict[self.type.get()]
                )
                if not messagebox.askokcancel(
                    "确认信息",
                    f"\n{self.type.get()}输入:"
                    + self.output
                    + "\n中文翻译:"
                    + self.tran,
                ):
                    # self.myDev.print_text(self.tran, self.lan_dict[self.type.get()])
                    self.inputbox.delete(0, tk.END)

    def randomPrint(self):
        self.Rchar = get_Rchar()
        self.showbox.config(state="normal")
        self.showbox.delete(0, tk.END)
        self.showbox.insert(
            0,
            array_to_unicode(self.myDev.get_text(self.Rchar, "chi_sim")),
        )
        self.showbox.config(state="disabled")
        # self.myDev.print_text(self.Rchar, "chi_sim")
        # messagebox.showinfo("提示", "打印完成,电机正在归位")
        self.entrybox.config(state="normal")
        # self.bt_voiceInput.config(state="normal")
        self.bt_verify.config(state="normal")

    # def voiceInput(self):
    #     self.myDev.speak("开始录音")
    #     start_audio()
    #     self.entrybox.delete(0, tk.END)
    #     self.entrybox.insert(0, self.myDev.recognize_audio("test.wav"))

    def entryVerify(self):
        if self.entrybox.get() == "":
            messagebox.showerror("错误", "输入不能为空")

        else:
            if self.myDev.get_text(self.entrybox.get()) == self.myDev.get_text(
                self.Rchar
            ):
                messagebox.showinfo(
                    "提示",
                    "恭喜你识别正确,答案是"
                    + self.Rchar
                    + f"({array_to_pinyin(self.myDev.get_text(self.Rchar))})",
                )
            else:
                messagebox.showinfo(
                    "提示",
                    "识别错误,正确答案是"
                    + self.Rchar
                    + f"({array_to_pinyin(self.myDev.get_text(self.Rchar))})",
                )
            self.entrybox.delete(0, tk.END)
            self.showbox.config(state="normal")
            self.showbox.delete(0, tk.END)
            self.showbox.config(state="disabled")
            self.Rchar = ""
            self.entrybox.config(state="disabled")
            # self.bt_voiceInput.config(state="disabled")
            self.bt_verify.config(state="disabled")

    def bt_cleararray_click(self, widget):
        widget.config(state="normal")
        widget.delete(0, tk.END)
        widget.config(state="disabled")
        widget.delete(0, tk.END)

    def bt_translatearray_click(self):
        array = self.showarray.get()
        print(array)
        print(unicode_to_array(array))
        print(array_to_pinyin(unicode_to_array(array)))
        messagebox.showinfo(
            "翻译结果",
            f"{array}的盲文国标拼音是{array_to_pinyin(unicode_to_array(array))}",
        )

    # if self.array_ser is not None:
    #     self.array_ser.close()
    # if self.array_serial_thread is not None:
    #     self.array_serial_thread.join()

    def bt_startarray_click(self):
        try:
            self.array_ser = serial.Serial(port=self.array_serial_port, baudrate=9600)
            self.array_ser.timeout = 1
            print(f"Successfully opened port {self.array_serial_port}")
            self.array_serial_thread = threading.Thread(
                target=self.array_serial_communication
            )
            self.array_serial_thread.start()
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)

    def array_serial_communication(self):
        self.serial_data = b""
        while True:
            try:
                snap = self.array_ser.read(12)
                print(snap)
                if len(snap) == 0:
                    continue
                self.serial_data += snap
                self.serial_array = self.parse_array()
                if self.serial_array is not None:
                    print(self.serial_array)
                    # self.showarray
                    self.showarray.config(state="normal")
                    # self.showarray.delete(0, tk.END)
                    self.showarray.insert(
                        tk.END,
                        array_to_unicode(self.serial_array),
                    )
                    self.showarray.config(state="disabled")
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break

    def parse_array(self):
        start_marker = b"RY"
        size = 6
        while len(self.serial_data) > 0 and self.serial_data[:2] != start_marker:
            self.serial_data = self.serial_data[1:]
        if len(self.serial_data) < (size + 2) or self.serial_data[:2] != start_marker:
            return None
        self.serial_data = self.serial_data[4:]
        getData = self.serial_data[:size].decode("utf-8")
        self.serial_data = self.serial_data[size + 2 :]
        return [
            [[int(getData[i]), int(getData[i + 1])] for i in range(0, len(getData), 2)]
        ]

    # def bt_endhand_click(self):
    #     if self.hand_ser is not None:
    #         self.hand_ser.close()
    #     if self.hand_serial_thread is not None:
    #         self.hand_serial_thread.join()

    # def bt_starthand_click(self):
    #     try:
    #         self.hand_ser = serial.Serial(port=self.hand_serial_port, baudrate=9600)
    #         self.hand_ser.timeout = 1
    #         print(f"Successfully opened port {self.array_serial_port}")
    #         self.hand_serial_thread = threading.Thread(
    #             target=self.hand_serial_communication
    #         )
    #         self.hand_serial_thread.start()
    #     except serial.SerialException as e:
    #         print(f"Error opening serial port: {e}")
    #         sys.exit(1)
    #     except Exception as e:
    #         print(f"An unexpected error occurred: {e}")
    #         sys.exit(1)

    # def hand_serial_communication(self):
    #     self.serial_data = b""
    #     while True:
    #         try:
    #             snap = self.hand_ser.readline()
    #             print(snap)
    #             if len(snap) == 0:
    #                 self.handle_serial_data("")
    #                 continue
    #             self.serial_data += snap
    #             self.serial_word = self.parse_hand()
    #             if self.serial_word is not None:
    #                 decoded_word = self.serial_word.decode("utf-8")
    #                 print(decoded_word)
    #                 self.handle_serial_data(decoded_word)
    #                 # self.handle_serial_data(self.serial_word.decode("utf-8"))
    #         except serial.SerialException as e:
    #             print(f"Serial error: {e}")
    #             break
    #         except Exception as e:
    #             print(f"An unexpected error occurred: {e}")
    #             break

    # def parse_hand(self):
    #     start_marker = b"RY"
    #     end_marker = b"ED"
    #     # size = 1
    #     while len(self.serial_data) > 0 and self.serial_data[:2] != start_marker:
    #         self.serial_data = self.serial_data[1:]
    #     if (
    #         len(self.serial_data) < 5 or self.serial_data[:2] != start_marker
    #     ):  # 至少大于5RY+ED
    #         return None
    #     self.serial_data = self.serial_data[2:]
    #     for i in range(min(3, len(self.serial_data) - 1)):
    #         if self.serial_data[i : i + 2] == end_marker:
    #             break
    #     if self.serial_data[i : i + 2] != end_marker:
    #         return None
    #     getData = self.serial_data[:i]
    #     self.serial_data = self.serial_data[i + 2 :]
    #     return getData

    # def handle_serial_data(self, data):
    # if data == "":
    #     # print("kongkongk")
    #     if len(self.queue) > 0:
    #         mode_code = max(set(self.queue), key=self.queue.count)
    #         print(f"当前识别物体代号可能为：{mode_code}")
    #         self.showhand.config(state="normal")
    #         self.showhand.delete(0, tk.END)
    #         self.showhand.insert(0, f"当前识别物体代号可能为：{mode_code}")
    #         self.showhand.config(state="disabled")
    #         self.queue.clear()
    # else:
    # self.queue.append(data)
    # if len(self.queue) == self.queue.maxlen:
    #     # 可以使用统计众数的方法确定代号
    #     mode_code = max(set(self.queue), key=self.queue.count)
    #     print(f"当前识别物体代号可能为：{mode_code}")
    #     self.showhand.config(state="normal")
    #     self.showhand.delete(0, tk.END)
    #     self.showhand.insert(0, f"当前识别物体代号可能为：{mode_code}")
    #     self.showhand.config(state="disabled")
    #     self.queue.clear()
    #     self.queue.clear()

    def go_back(self):
        # 销毁当前窗口，创建首页
        if hasattr(self, "array_ser") and self.array_ser is not None:
            self.array_ser.close()
        # if hasattr(self, "hand_ser") and self.hand_ser is not None:
        #     self.hand_ser.close()
        if (
            hasattr(self, "array_serial_thread")
            and self.array_serial_thread is not None
            and self.array_serial_thread.is_alive()
        ):
            self.array_serial_thread.join()
        # if (
        #     hasattr(self, "hand_serial_thread")
        #     and self.hand_serial_thread is not None
        #     and self.hand_serial_thread.is_alive()
        # ):
        # self.hand_serial_thread.join()
        self.destroy()
        Homepage(1)


class win3(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("手语模式")
        self.geometry("550x600")
        self.myDev = device()
        self.hand_serial_port = "COM5"  # 手势识别
        self.hand_dict = {
            "1": "好",
            "2": "大家",
            "3": "我",
            "4": "谢谢",
            "5": "你",
            "6": "投票",
            "7": "要",
            "8": "朋友",
            "9": "是",
        }
        self.queue = deque(maxlen=20)  # 设置队列长度，可以根据实际情况调整
        self.create_widgets()

    def create_widgets(self):
        self.frm = tk.Frame(self)
        self.frm.grid(padx=20, pady=10, columnspan=3)
        self.label_hand = tk.Label(self.frm, text="手语识别")
        self.label_hand.grid(row=0, column=0, ipadx=3, ipady=5, padx=10, pady=10)
        self.showhand = tk.Entry(self.frm, width=20, state="readonly")
        self.showhand.grid(
            row=0,
            column=1,
            ipadx=3,
            ipady=5,
            padx=10,
            pady=10,
            sticky="w",
        )
        self.bt_starthand = tk.Button(
            self.frm, text="开始识别", command=self.bt_starthand_click
        )
        self.bt_starthand.grid(row=0, column=2, ipadx=3, ipady=5, padx=10, pady=10)

        self.bt_endhand = tk.Button(
            self.frm, text="关闭识别", command=self.bt_endhand_click
        )
        self.bt_endhand.grid(row=0, column=3, ipadx=3, ipady=5, padx=10, pady=10)
        self.bt_back = tk.Button(self.frm, text="返回首页", command=self.go_back)
        self.bt_back.grid(row=1, column=0, ipadx=3, ipady=5, padx=10, pady=10)

    def bt_endhand_click(self):
        if self.hand_ser is not None:
            self.hand_ser.close()
        if self.hand_serial_thread is not None:
            self.hand_serial_thread.join()

    def bt_starthand_click(self):
        try:
            self.hand_ser = serial.Serial(port=self.hand_serial_port, baudrate=9600)
            self.hand_ser.timeout = 1
            print(f"Successfully opened port {self.hand_serial_port}")
            self.hand_serial_thread = threading.Thread(
                target=self.hand_serial_communication
            )
            self.hand_serial_thread.start()
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)

    def hand_serial_communication(self):
        self.serial_data = b""
        while True:
            try:
                snap = self.hand_ser.readline()
                print(snap)
                if len(snap) == 0:
                    self.handle_serial_data("")
                    continue
                self.serial_data += snap
                self.serial_word = self.parse_hand()
                if self.serial_word is not None:
                    decoded_word = self.serial_word.decode("utf-8")
                    print(decoded_word)
                    self.handle_serial_data(decoded_word)
                    # self.handle_serial_data(self.serial_word.decode("utf-8"))
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break

    def parse_hand(self):
        start_marker = b"RY"
        end_marker = b"ED"
        # size = 1
        while len(self.serial_data) > 0 and self.serial_data[:2] != start_marker:
            self.serial_data = self.serial_data[1:]
        if (
            len(self.serial_data) < 5 or self.serial_data[:2] != start_marker
        ):  # 至少大于5RY+ED
            return None
        self.serial_data = self.serial_data[2:]
        for i in range(min(3, len(self.serial_data) - 1)):
            if self.serial_data[i : i + 2] == end_marker:
                break
        if self.serial_data[i : i + 2] != end_marker:
            return None
        getData = self.serial_data[:i]
        self.serial_data = self.serial_data[i + 2 :]
        return getData

    def handle_serial_data(self, data):
        if data == "":
            # print("kongkongk")
            if len(self.queue) > 0:
                mode_code = max(set(self.queue), key=self.queue.count)
                print(f"当前识别物体代号可能为：{mode_code}")
                self.showhand.config(state="normal")
                self.showhand.delete(0, tk.END)
                self.showhand.insert(0, self.hand_dict[mode_code])
                self.showhand.config(state="disabled")
                self.myDev.speak(self.hand_dict[mode_code])
                self.queue.clear()
        else:
            self.queue.append(data)
            if len(self.queue) == self.queue.maxlen:
                # 可以使用统计众数的方法确定代号
                mode_code = max(set(self.queue), key=self.queue.count)
                print(f"当前识别物体代号可能为：{mode_code}")
                self.showhand.config(state="normal")
                self.showhand.delete(0, tk.END)
                self.showhand.insert(0, self.hand_dict[mode_code])
                self.showhand.config(state="disabled")
                self.myDev.speak(self.hand_dict[mode_code])
                self.queue.clear()

    def go_back(self):
        # 销毁当前窗口，创建首页
        if hasattr(self, "hand_ser") and self.hand_ser is not None:
            self.hand_ser.close()
        if (
            hasattr(self, "hand_serial_thread")
            and self.hand_serial_thread is not None
            and self.hand_serial_thread.is_alive()
        ):
            self.hand_serial_thread.join()
        self.destroy()
        Homepage(1)


# 创建首页
class Homepage:
    def __init__(self, flag=0):
        self.homepage = tk.Tk()
        self.homepage.title("心桥服务平台")
        self.homepage.geometry("450x200")
        self.flag = flag
        self.myDev = device()
        self.serial_port = "COM8"
        self.ser = None
        self.serial_thread = None
        self.create_widgets()
        self.start_serial_thread()
        self.homepage.mainloop()

    def create_widgets(self):
        frm = tk.Frame(self.homepage)
        frm.grid(padx=20, pady=10, columnspan=3)
        label_title = tk.Label(frm, text="心桥服务平台", font=("华文行楷", 20))
        label_title.grid(row=0, column=1, ipadx=6, ipady=10, padx=10, pady=10)
        self.accessible_button = tk.Button(
            frm, text="无障碍模式", command=self.show_accessible_interface
        )
        self.accessible_button.grid(row=1, column=0, ipadx=3, ipady=5, padx=10, pady=10)
        self.hand_button = tk.Button(
            frm, text="手语模式", command=self.show_hand_interface
        )
        self.hand_button.grid(row=1, column=1, ipadx=3, ipady=5, padx=10, pady=10)
        self.study_button = tk.Button(
            frm, text="学习模式", command=self.show_study_interface
        )
        self.study_button.grid(row=1, column=2, ipadx=3, ipady=5, padx=10, pady=10)

        self.accessible_button.bind("<Tab>", self.on_tab)
        self.hand_button.bind("<Tab>", self.on_tab)
        self.study_button.bind("<Tab>", self.on_tab)
        self.accessible_button.bind("<Shift-Return>", self.on_shift)
        self.hand_button.bind("<Shift-Return>", self.on_shift)
        self.study_button.bind("<Shift-Return>", self.on_shift)
        self.accessible_button.bind("<Return>", self.on_return)
        self.hand_button.bind("<Return>", self.on_return)
        self.study_button.bind("<Return>", self.on_return)
        if self.flag == 1:
            try:
                hwnd = self.homepage.winfo_id()
                win32gui.SetForegroundWindow(hwnd)
                self.homepage.focus_force()
            except Exception as e:
                print(f"win focus error: {e}")
                messagebox.showwarning(
                    "焦点设置问题", "焦点设置失败，请手动将焦点切换到程序窗口。"
                )
        self.accessible_button.focus_set()

    def on_tab(self, event):
        widget = event.widget
        if widget == self.accessible_button:
            self.hand_button.focus_set()
        elif widget == self.hand_button:
            self.study_button.focus_set()
        elif widget == self.study_button:
            self.accessible_button.focus_set()
        return "break"

    def on_shift(self, event):
        widget = event.widget
        self.myDev.speak("当前选项是进入" + widget["text"])
        return "break"

    def on_return(self, event):
        widget = event.widget
        if widget == self.accessible_button:
            self.show_accessible_interface()
        elif widget == self.hand_button:
            self.show_hand_interface()
        elif widget == self.study_button:
            self.show_study_interface()
        return "break"

    def handle_serial_data(self, data):
        if data == "DN":
            self.homepage.event_generate("<Shift-Tab>")
        elif data == "UP":
            self.homepage.event_generate("<Tab>")
        elif data == "EN":
            self.homepage.event_generate("<Return>")
        else:
            self.homepage.event_generate("<Shift-Return>")

    def start_serial_thread(self):
        try:
            self.ser = serial.Serial(self.serial_port, baudrate=9600)
            self.ser.timeout = 1
            print(f"Successfully opened port {self.serial_port}")
            self.serial_thread = threading.Thread(target=self.serial_communication)
            self.serial_thread.start()
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)

    def serial_communication(self):
        self.serial_data = b""
        while True:
            try:
                snap = self.ser.read(8)
                if len(snap) == 0:
                    continue
                self.serial_data += snap
                self.serial_word = self.parse_data()
                if self.serial_word is not None:
                    print(self.serial_word.decode("utf-8"))
                    self.handle_serial_data(self.serial_word.decode("utf-8"))
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break

    def parse_data(self):
        start_marker = b"RY"
        size = 2
        while len(self.serial_data) > 0 and self.serial_data[:2] != start_marker:
            self.serial_data = self.serial_data[1:]
        if len(self.serial_data) < (size + 2) or self.serial_data[:2] != start_marker:
            return None
        self.serial_data = self.serial_data[4:]
        getData = self.serial_data[:size]
        self.serial_data = self.serial_data[size + 2 :]
        return getData

    def show_accessible_interface(self):
        if self.ser is not None:
            self.ser.close()
        # if self.serial_thread is not None and self.serial_thread.is_alive():
        #     self.serial_thread.join()
        self.homepage.destroy()
        window1 = win1()
        try:
            hwnd = window1.winfo_id()
            win32gui.SetForegroundWindow(hwnd)
            window1.focus_force()
            window1.choice_ch.focus_set()
        except Exception as e:
            print(f"win focus error: {e}")
            messagebox.showwarning(
                "焦点设置问题", "焦点设置失败，请手动将焦点切换到程序窗口。"
            )
        window1.mainloop()

    def show_hand_interface(self):
        if self.ser is not None:
            self.ser.close()
        # if self.serial_thread is not None and self.serial_thread.is_alive():
        #     self.serial_thread.join()
        self.homepage.destroy()
        window3 = win3()
        try:
            hwnd = window3.winfo_id()
            win32gui.SetForegroundWindow(hwnd)
            window3.focus_force()
        except Exception as e:
            print(f"win focus error: {e}")
            messagebox.showwarning(
                "焦点设置问题", "焦点设置失败，请手动将焦点切换到程序窗口。"
            )
        window3.mainloop()

    def show_study_interface(self):
        if self.ser is not None:
            self.ser.close()
        # if self.serial_thread is not None and self.serial_thread.is_alive():
        #     self.serial_thread.join()
        self.homepage.destroy()
        window2 = win2()
        try:
            hwnd = window2.winfo_id()
            win32gui.SetForegroundWindow(hwnd)
        except Exception as e:
            print(f"win focus error: {e}")
            messagebox.showwarning(
                "焦点设置问题", "焦点设置失败，请手动将焦点切换到程序窗口。"
            )
        window2.mainloop()


if __name__ == "__main__":
    Homepage()
