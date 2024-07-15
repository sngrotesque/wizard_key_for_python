# -*- coding: utf-8 -*-
from matplotlib.mlab import window_none
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import wave
import sys

def img2wav(img_path, wav_path, fft_size=1024):
    """把图片写到音频频域
    :param img_path: 输入图片路径
    :param wav_path: 输出音频路径
    :param fft_size: 图片每列代表的音频长度，也是频域长度的两倍"""
    img = Image.open(img_path).convert('L') # 读取图片，转为灰度图
    img = img.resize((img.width * fft_size // 2 // img.height,
        fft_size // 2), Image.BICUBIC) # 缩放到高度 = fft_size / 2 （令负频率全为0）

    img = np.array(img, 'float') # 转为numpy数组
    img = img * (100 / 255) - 100 # 变换到-100~0分贝
    # 单位从分贝转成1，此时取值为0~1
    # amp_dB = 20 * ln(amp) / ln(10)
    # amp = exp(amp_dB / 20 * ln(10))
    img = np.exp(img * (np.log(10) / 20))
    img = img[::-1].T # 翻转（索引小的频率小）然后转置（要迭代列）

    max_sum = max(col.sum() for col in img) # 防溢出，每列总振幅不能超过1
    if max_sum > 1:
        img /= max_sum

    with wave.open(wav_path, 'wb') as f:
        # (nchannels, sampwidth, framerate, nframes, comptype, compname)
        f.setparams((1, 2, 44100, len(img) * fft_size, 'NONE', ''))
        for col in img:
            data = np.fft.ifft(col * fft_size, fft_size).real * 32767 # 傅里叶反变换
            # 最后一次防溢出，限制范围在-32768~32767
            for index in np.where(data < -32768):
                data[index] = -32768
            for index in np.where(data > 32767):
                data[index] = 32767

            data = data.astype('short')
            f.writeframesraw(data)

def draw_spectrum(wav_path, fft_size=1024):
    """画音频频谱图
    :param wav_path: 输入音频路径
    :param fft_size: 傅里叶变换用的长度"""
    with wave.open(wav_path, 'rb') as f:
        n_samples = f.getnframes()
        data = f.readframes(n_samples)
        n_channels = f.getnchannels()
        sample_rate = f.getframerate()
    data = np.frombuffer(data, dtype='int16') # 转为numpy数组
    data.shape = (n_samples, n_channels) # 取第一个声道
    data = data.T[0]
    # 画频谱，无加窗和重叠
    plt.specgram(data / 32767, fft_size, sample_rate, window=window_none,
        noverlap=0, scale='dB')
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        exit(f'python {sys.argv[0]} [Image Path] [Audio Path]')
    imgPath = sys.argv[1]
    audioPath = sys.argv[2]
    
    img2wav(imgPath, audioPath)
    # draw_spectrum(audioPath)
