import cv2
import time
import os

def dir_remake(saveDir):
    while saveDir[-1] == '\\' or saveDir[-1] == '/':
        saveDir = saveDir.strip('\\')
        saveDir = saveDir.strip('/')
    return saveDir

def video_to_frames(in_file :str, dirName :str):
    ''' Source: https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames '''
    dirName = dir_remake(dirName)
    if not os.path.isfile(dirName) and not os.path.exists(dirName):
        os.mkdir(dirName)
    
    time_start = time.time() # 记录时间
    cap = cv2.VideoCapture(in_file) # 开始捕获提要
    video_length = cap.get(cv2.CAP_PROP_FRAME_COUNT) # 查找帧数
    print(f">>>> 视频总帧数: {video_length}")
    print(f">>>> 转换视频中...\n")
    count = 0
    while cap.isOpened(): # 开始转换视频
        ret, frame = cap.read() # 提取帧
        if not ret: continue
        fileName = f'{dirName}/{count+1:0>5}.jpg'
        print(f'\r>>>> 输出到文件路径: {fileName}', end='')
        cv2.imwrite(fileName, frame) # 将结果写回输出位置。
        count += 1
        if (count > (video_length-1)): # 如果没有剩余的帧
            time_end = time.time() # 再次记录时间
            cap.release() # 释放内存
            print(f'\n', end='')
            print(f">>>> 提取视频帧完成.")
            print(f">>>> 转换耗时: {time_end-time_start:.2f} 秒.")
            break

if __name__=="__main__":
    in_file = '20220913215449.mp4'
    dirName = '20220913215449/'
    video_to_frames(in_file, dirName)