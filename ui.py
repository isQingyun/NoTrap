# from subprocess import Popen, PIPE, STDOUT
import subprocess

# import time
import tkinter as tk
from tkinter import messagebox, ttk

import cv2

from toolbox import device


class win(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("盲人服务平台")
        self.geometry("550x600")
        self.myDev = device()
        self.create_widgets()
        self.func = {
            "一键输出": self.on_button_click,
            "1.图片显示": self.show_click,
            "2.翻译结果": self.tran_click,
            "3.盲文打印": self.print_click,
            "打印输入": self.print_input_click,
        }

    def create_widgets(self):
        self.frm = tk.Frame(self)
        self.frm.grid(padx=20, pady=10, columnspan=3)
        # bt_capture = tk.Button(frame, text="拍摄图片", command=on_button_click)
        # bt_capture.grid(row=0, column=0, ipadx=3, ipady=5, padx=10, pady=10)

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
            pady=10,
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
            self.frm, text="打印输入", command=self.print_input_click, state="disabled"
        )
        self.bt_input.grid(row=3, column=3, ipadx=3, ipady=5, padx=10, pady=10)
        self.widgets = [
            self.choice_ch,
            self.choice_eg,
            self.bt_total,
            self.bt_show,
            self.bt_tran,
            self.bt_print,
            self.inputbox,
            self.bt_input,
        ]
        self.bind_widgets()

    def bind_widgets(self):
        for widget in self.widgets:
            # widget.bind("<space>", self.on_space)
            widget.bind("<Shift-Return>", self.on_shift)
            widget.bind("<Return>", self.on_return)
        self.widgets[0].focus_set()

    def on_space(self, event):
        event.widget.tk_focusNext().focus_set()
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
        # 当按下 Enter 键时，检查当前聚焦的组件
        widget = event.widget
        if isinstance(widget, tk.Button):
            # 对于按钮，直接调用其 command 方法
            command = self.func[widget["text"]]
            command()
        elif isinstance(widget, ttk.Radiobutton):
            # 对于单选按钮，设置其为选中状态
            # self.win.set(widget.cget("value"))
            # self.win.event_generate("<<RadioSelect>>")
            self.type.set(widget.cget("value"))
            self.type_choice()
        return "break"

    # 定义执行脚本的函数

    # def execute_script(self, script_path):
    #     # 使用Popen来执行脚本并捕获输出
    #     with Popen(
    #         ["python", script_path], stdout=PIPE, stderr=PIPE, text=True
    #     ) as process:
    #         # 实时读取输出
    #         while True:
    #             output = process.stdout.readline()
    #             error = process.stderr.readline()
    #             if output == "" and error == "" and process.poll() is not None:
    #                 break
    #             if output:
    #                 print(output.strip())
    #             if error:
    #                 print(error.strip())
    #         # 打印退出代码（如果需要）
    #         rc = process.poll()
    #         return rc
    def execute_script(self, script_path):
        try:
            # 使用subprocess.run来执行脚本并捕获输出
            result = subprocess.run(
                ["python", script_path], capture_output=True, text=True
            )
            # 返回脚本的输出
            return result.stdout
        except subprocess.CalledProcessError as e:
            # 如果脚本执行失败，捕获错误并打印
            print(f"脚本执行失败: {e.output}")
            return None  # 或者根据需要返回一个错误消息

    def print_input_click(self):
        if self.inputbox.get() == "":
            messagebox.showerror("错误", "输入不能为空")
            self.myDev.speak("错误,输入不能为空")
        else:
            self.output = self.inputbox.get()
            if self.type.get() == "chi_sim":
                messagebox.showinfo("识别结果", f"中文识别:{self.output}")
                self.myDev.speak("中文识别" + self.output)
                self.myDev.print_text(self.output)
            elif self.type.get() == "eng":
                self.tran = self.myDev.translate(self.output)
                messagebox.showinfo(
                    "识别结果", f"英文识别:{self.output}\n中文翻译:{self.tran}"
                )
                self.myDev.speak("英文识别:" + self.output + ",中文翻译:" + self.tran)
                self.myDev.print_text(self.tran)
            self.inputbox.delete(0, tk.END)
            self.myDev.speak("打印完成")

    def type_choice(self):
        if self.type.get() == "chi_sim":
            self.myDev.speak("您选择的是中文")
            print("您选择的是中文")
            self.bt_show.config(state="normal")
            self.bt_total.config(state="normal")
            self.inputbox.config(state="normal")
            self.bt_input.config(state="normal")
        elif self.type.get() == "eng":
            self.myDev.speak("您选择的是英文")
            print("您选择的是英文")
            self.bt_show.config(state="normal")
            self.bt_total.config(state="normal")
            self.inputbox.config(state="normal")
            self.bt_input.config(state="normal")
        else:
            self.bt_show.config(state="disabled")

    def on_button_click(self):
        # imgout = cv2.imread(r"C:\Users\hu\Desktop\hard\NoTrap\test.png")  # 图片位置
        # cv2.imshow("captured image", imgout)
        self.show_click()
        self.bt_tran.config(state="disabled")
        self.bt_print.config(state="disable")
        self.bt_show.config(state="normal")
        self.bt_total.focus_set()
        text = []
        for i in range(12, 20):
            text += [
                self.myDev.read(
                    f"image_{i}.png",
                    "C:\\Users\\lockw\\Desktop\\NoTrap\\img\\",
                    self.type.get(),
                )
            ]
        self.output = max(text, key=len, default="")
        if self.type.get() == "chi_sim":
            print(self.output)
            self.myDev.speak("中文识别," + self.output)
            self.myDev.print_text(self.output)
        elif self.type.get() == "eng":
            self.tran = self.myDev.translate(self.output)
            print(self.tran)
            self.myDev.speak("英文识别:" + self.output + ",中文翻译:" + self.tran)
            self.myDev.print_text(self.tran)
        self.myDev.speak("打印完成")

        # self.bt_tran.config(state="disabled")
        # self.bt_print.config(state="disable")
        # self.bt_show.config(state="normal")

    def show_click(self):
        # self.execute_script("")
        imgout = cv2.imread(
            r"C:\Users\lockw\Desktop\NoTrap\img\image_12.png",
        )  # 图片位置
        cv2.imshow("captured image", imgout)
        self.bt_tran.config(state="normal")
        self.bt_show.tk_focusNext().focus_set()
        self.bt_show.config(state="disable")
        cv2.waitKey(2000)
        self.myDev.speak("图片显示结果")
        cv2.waitKey(2000)
        cv2.destroyAllWindows()

    def tran_click(self):
        # self.myDev=device()
        text = []
        for i in range(12, 17):
            text += [
                self.myDev.read(
                    f"image_{i}.png",
                    "C:\\Users\\lockw\\Desktop\\NoTrap\\img\\",
                    self.type.get(),
                )
            ]
            # C:\Users\hu\Desktop\hard\NoTrap\img2
            # text = myDev.read(r"C:\Users\lockw\Desktop\NoTrap\img2\image_7.png")

        # print(f"文本识别： {text}")
        self.output = max(text, key=len, default="")
        if self.type.get() == "chi_sim":
            messagebox.showinfo("识别结果", f"中文识别:{self.output}")
            self.myDev.speak("中文识别" + self.output)
        elif self.type.get() == "eng":
            self.tran = self.myDev.translate(self.output)
            messagebox.showinfo(
                "识别结果", f"英文识别:{self.output}\n中文翻译:{self.tran}"
            )
            self.myDev.speak("英文识别:" + self.output + ",中文翻译:" + self.tran)
        self.bt_print.config(state="normal")
        self.bt_tran.tk_focusNext().focus_set()
        self.bt_tran.config(state="disable")
        #  # 识别函数位置
        # if output is None:
        #     messagebox.showerror("错误", "脚本无返回值")

    def print_click(self):
        ##成功运行啥的
        if self.type.get() == "chi_sim":
            print(self.output)
            self.myDev.print_text(self.output)
        elif self.type.get() == "eng":
            print(self.tran)
            self.myDev.print_text(self.tran)
        messagebox.showinfo("打印结果", "打印完成！")
        self.myDev.speak("打印完成")
        self.bt_show.config(state="normal")
        self.bt_print.tk_focusNext().focus_set()
        self.bt_print.config(state="disable")


if __name__ == "__main__":
    window = win()
    window.mainloop()
