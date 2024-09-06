import subprocess
import threading


# 定义一个函数来运行 save_img.py 脚本
def run_save_img():
    subprocess.run(["python", r"C:\Users\lockw\Desktop\NoTrap\save_img.py"])


# 定义一个函数来运行 ui.py 脚本
def run_ui():
    subprocess.run(["python", r"C:\Users\lockw\Desktop\NoTrap\ui.py"])


# 主函数，用于启动两个线程
def main():
    # 创建线程来运行 save_img.py
    thread_save_img = threading.Thread(target=run_save_img)
    # 创建线程来运行 ui.py
    thread_ui = threading.Thread(target=run_ui)

    # 启动线程
    thread_save_img.start()
    thread_ui.start()

    # 等待线程结束
    thread_save_img.join()
    thread_ui.join()


# 调用主函数
if __name__ == "__main__":
    main()
