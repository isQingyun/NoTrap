import wave

import pyaudio


def start_audio(time=3, save_file="test.wav"):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 16000
    RECORD_SECONDS = time  # 需要录制的时间
    WAVE_OUTPUT_FILENAME = save_file  # 保存的文件名

    p = pyaudio.PyAudio()  # 初始化
    print("RECOARD ON")

    stream = p.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )  # 创建录音文件
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)  # 开始录音

    print("RECOARD OFF")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")  # 保存
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()


if __name__ == "__main__":
    start_audio()
