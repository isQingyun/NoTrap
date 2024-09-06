核心思想

软件部分的核心思想是**信息链的提取和处理**。

系统通过摄像模块将图像保存到本地，通过pytesseract模块将小型摄像头拍摄的图像转换成中/英文文字信息，统一转换成中文，使用jieba智能分词系统切割文本信息，根据盲文转换规则翻译成3*2的盲文点阵。

获得点阵之后，系统对点阵进行解析，自动翻译成gcode指令，通过串口烧录进CNC板，CNC中预加载的GRBL会进一步解读gcode指令，操作步进电机在纸面上将盲文打印出来。

# 软件模块

余杨诚

## 使用教学

### 环境准备

一、安装pytesseract-OCR

1. Download tesseract exe from https://github.com/UB-Mannheim/tesseract/wiki.
2. Install this exe in `C:\Program Files (x86)\Tesseract-OCR`
3. Open virtual machine command prompt in windows or anaconda prompt.
4. Run `pip install pytesseract`

二、pip安装别的依赖库

```cmd
pip install opencv-python jieba pandas pypinyin Pillow tencentcloud-sdk-python
```

三、（*）注册腾讯翻译api，将`main.py`的下列代码内容替换成自己的api_secret和api_key：

```python
cred = credential.Credential(
                "api_secret",
                "api_key",
            )
```

四、（*）注册讯飞语音api，将`main.py`的下列代码内容替换成自己的appid,api_secret和api_key:

```python
str_to_mp3(
    appid="appid",
    api_secret="api_secret",
    api_key="api_key",
    url="wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/medd90fec",
    # 待合成文本
    text=input_text,
    # 发音人参数
    vcn="x4_lingxiaoxuan_oral",
    save_file_name="./voice.mp3",
)
```

五、确认上述过程完成无误，开始编写自己的代码吧！

## 开发过程

#### 汉盲翻译

网络上公开的资料较为匮乏：

- 百度上检索结果绝大部分都是学报、论文。
  
- 在google上检索，有由中文盲文数字平台开发的汉盲翻译网站，但是不提供没有提供api接口。
  

鉴于资料匮乏，团队选择自行开发汉盲翻译功能。由于汉语“方块字”的属性，相比于英语等拼音文字，汉盲转换更加复杂。

> 现有的汉盲转换方法均采用多步转换方法：
> 
> 1. 先对汉字文本进行盲文**分词**连写
> 2. 再对汉字进行**标调**
> 3. 最后结合分词和标调信息**合成盲文文本**。

我们延续了这一思路，在有限的开发时间内，规定全部标调的标准，根据博客园上提供的汉语盲文对照表 https://www.cnblogs.com/gwind/p/8009861.html 开发了自己的汉盲转换功能。

#### 语音合成

我们尝试了多种基于文本的语音合成功能：

- 本地机械语音合成
  
- 百度语音api
  
- 讯飞语音开放大平台
  

由于前两者产生的电子音明显具有**机械感**和**疲惫感**，长时间使用会让人感到不适；而讯飞的超拟人合成技术合成的语音，则可以实现接近人声的效果。最终，我们选择使用讯飞开放大平台实现语音合成。

### 图像识别与中英翻译

在互联网上检索资料后，我们选择了目前准确率最高的翻译引擎：tesseract-OCR负责实现图像识别板块。

我们在开发翻译功能时尝试了两种技术路线，分别是本地词库查询和调用腾讯api。由于本地词库查询不支持长文本（句子）识别，我们最终选择了后者。

#### 开发阻碍

软件部分遇到的主要困难有如下几点：

1. 由于汉语“方块字”的属性，相比于英语等拼音文字，汉盲转换需要进行复杂的分词转换、基于现行盲文标准的声母替换等预处理。网络上汉盲转换资料相当匮乏，因此本系统的汉盲转换部分基本由团队根据现有资料独立开发。另外，现行盲文标准关于标调和不标调有着复杂的规定，由于软件开发时间紧张，本系统采用全部标调的做法。
  
2. 考虑到我们作品面向的是视障人群，需要尽可能降低成本，我们的摄像模块是自己搭建的，拍摄出来的照片像素和清晰度有限。因此，我们自主学习了opencv的图像处理的一些算法，用来锐化图片，增加图像识别的准确性。
  

---

# 写字机模块

田铠瑄

## 使用教学

### 准备

##### Arduino环境：

- Arduino IDE
  
- grbl（GitHub搜索即可）
  
- coreXY.hex（待刷固件）
  
- 刷固件工具（用于向Arduino刷固件）
  

##### 控制电脑环境：

- python及其解释器（vscode）
  
- pyserial库（pip install pyserial）
  
- gcode_generator.py（脚本文件）
  
- CH340G_USB驱动.rar
  

##### 硬件：

- 打字机系统（硬件部分采购列表和3D打印件图纸，见附件）
  
- cnc控制板
  
- Arduino uno及烧录线
  
- 电机驱动 * 4
  
- 充电宝及电线、诱骗器
  

### 详细教程

#### 环境配置

##### Arduino环境：

1. 下载 **grbl** 库， 将其中 **Grbl** 文件夹（与doc文件同级，内容只有示例文件和其他配置文件）压缩为 **.zip** 文件。
  
2. 启动Arduino IDE，导入库，选择压缩好的 **Grbl.zip** 文件。
  
3. 打开grbl库下的示例文件 **GrblUpload**，并且将其烧录到Arduino控制板中。
  
4. 打开**刷固件工具**，将 **coreXY.hex** 文件上传到Arduino和cnc控制板中。
  

##### 控制电脑环境：

1. 下载pyserial库，可以通过在终端中输入**pip install pyserial**。
  
2. 打开 **CH340G_USB驱动.rar** 中的 **DRVSETUP64.exe** 文件，安装驱动。
  
3. 打开**设备管理器**，点击**查看**，选择**查看隐藏设备**，在主界面中找到**端口（COM和LPT）**，在次项目中确定自己用于连接控制板的**端口名称**。
  

#### 具体使用

将 **gcode_generator.py** 文件中，将`ser = serial.Serial("COM3", 15200)`中的`COM3`改成自己连接控制板的端口名称。并且完成与前续代码的链接。

将Arduino控制板与控制电脑连接，通过充电宝为cnc控制板通电（**注意正负极**），之后分别按下Arduino和cncn控制板上的重启按键。

启动程序即可。

## 开发过程

#### 机械结构

盲文打字机本质上类似于3D打印机，常见结构有coreXY和Hbot两种结构，主要区别为：

- coreXY结构更稳定
  
- coreXY控制精度更高
  
- coreXY制作更复杂
  

鉴于盲文对打印精度要求较高，在本项目中选择coreXY结构。

> 打字机具体结构依据GitHub开源项目自制（大鱼打字机V2.2）。

#### 控制程序

上位机的选择经过三次迭代：

- 首次，直接使用较成熟的3D打字机上位机软件（炽写3.0）。
  
  - [ ] 不能够打印盲文。
    
  - [ ] 打字极不稳定。
    
  - [ ] 界面操作繁琐，为本盲人友好的设计初衷。
    
- 第二次，使用python生成特定的盲文打印G-code代码，并且通过Universal Gcode Sender执行。
  
  - [x] 能够打印盲文
    
  - [x] 打字稳定
    
  - [ ] 仍然需要一定的界面操作，不便于盲人使用
    
- 第三次，使用python生成G-code代码，且直接通过其serial库将代码传输给控制板来执行打印。
  
  - [x] 能够打印盲文
    
  - [x] 打字稳定
    
  - [x] 没有任何界面操作，跟随前序代码执行。
