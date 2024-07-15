from Crypto.Cipher import AES, DES, DES3, ChaCha20

from wtools.utils import fread, fwrite
from typing import Callable
import hashlib
import base64
import wtools
import random
import socket
import struct
import time
import sys
import re
import os

def fcipher_xcrypt():
    if len(sys.argv) < 5:
        exit(f'usage: python {sys.argv[0]} [Password] [input_path] [output_path] [e]ncrypt/[d]ncrypt')
    
    password = sys.argv[1]
    input_path = sys.argv[2]
    output_path = sys.argv[3]
    xcrypt_mode = sys.argv[4].lower()
    
    if input_path == output_path:
        print(f'input_path == output_path, are you sure?')
        choice = input('[y/N]').lower()
        if (choice == '') or (choice == 'n') or (choice == 'no'):
            exit('exit.')
        elif (choice == 'y') or (choice == 'yes'):
            print('continue.')
        else:
            exit('error input.')
    
    ctx = wtools.fcipher(password.encode())
    
    if xcrypt_mode == 'e':
        ctx.encrypt(input_path, output_path)
    elif xcrypt_mode == 'd':
        ctx.decrypt(input_path, output_path)
    else:
        exit(f'unknown xcrypt_mode.')

def create_true_random_number(min :int, max :int):
    array_size = random.choice([1, 2, 4, 8])
    random_bytearray = os.urandom(array_size)

    random_number = -1
    format_symbol = {1:'B',2:'H',4:'I',8:'Q'}[array_size]

    random_number = struct.unpack(f'>{format_symbol}', random_bytearray)[0]

    return random_number % (max - min + 1) + min

def pixiv_use(get_follow_list :bool = False):
    follow_list_save_path = './other/pixiv_follower.txt'
    pitcher_list_save_path = 'F:/Pitchers/Pixiv'
    https_proxies = 'http://localhost:8081'
    
    pix = wtools.pixiv(38279179, 'E:/pixiv_cookie.txt', save_path = pitcher_list_save_path,
                    proxies = https_proxies, maxNumberThreads=16)
    
    if get_follow_list:
        print('开始获取关注列表的所有作者ID...')
        artist_list = pix.get_all_followed_artists_uids()
        print(f'获取完毕，保存至{follow_list_save_path}')
        wtools.utils.fwrite(follow_list_save_path,
                            data = '\n'.join(artist_list).encode())
    else:
        artist_list = wtools.utils.fread(follow_list_save_path).decode().split()
    
    for artist_id in artist_list:
        pix.multi_threaded_download(artist_id, f'{pitcher_list_save_path}/{artist_id}')
        break

def encryption_speed_test(algorithmName: str = 'aes', key_len :int = 32, iv_len :int = 16):
    def encryption_timer(ctx, plaintext :bytes):
        start_timer = time.time()
        encrypted   = ctx.encrypt(plaintext)
        stop_timer  = time.time()
        
        # 此内容是为了encrypted不被优化掉
        print(f'{encrypted[0]:02x}\b\b',end='')
        
        return stop_timer-start_timer
    ctx = None
    key = os.urandom(key_len)
    iv  = os.urandom(iv_len)

    match algorithmName.lower():
        case 'aes':
            ctx = AES.new(key, mode = AES.MODE_CBC, iv = iv)
        case 'des':
            ctx = DES.new(key, mode = DES.MODE_CBC, iv = iv)
        case '3des' | 'des3' | 'tdes':
            ctx = DES3.new(key, mode = DES3.MODE_CBC, iv = iv)
        case 'chacha20' | 'cc20':
            ctx = ChaCha20.new(key = key, nonce = iv)
        case _:
            raise TypeError(f'暂不支持{algorithmName}呢~')

    print(f'current algorithm name: {algorithmName}')

    randomData_16MB   = bytes(16  * 1024**2)
    randomData_512MB  = bytes(512 * 1024**2)
    randomData_1024MB = bytes(      1024**3)

    timer_16MB = encryption_timer(ctx, randomData_16MB)
    print(f'16MB   time used: {timer_16MB:.4f}')

    timer_512MB = encryption_timer(ctx, randomData_512MB)
    print(f'512MB  time used: {timer_512MB:.4f}')

    timer_1024MB = encryption_timer(ctx, randomData_1024MB)
    print(f'1024MB time used: {timer_1024MB:.4f}')

def total_download_time_required(TotalDownload :float, DownloadSpeed :float,
                                 TotalDwonloadUnit: str = 'GB', DownloadSpeedUnit :str = 'MB'):
    def _match_func(unit :str, download :float):
        match unit:
            # byte per second
            case 'GB': download *= 1024
            case 'TB': download *= 1024**2
            case 'MB': pass
            case 'KB': download /= 1024
            # bit per second
            case 'Tb': download = download / 8 * 1024**2
            case 'Gb': download = download / 8 * 1024
            case 'Mb': download /= 8
            case 'Kb': download = download / 8 / 1024
            case _:
                raise TypeError('你使用的单位是PB或者B？？？啊？不是哥们？')
        return download

    TotalDownload = _match_func(TotalDwonloadUnit, TotalDownload)
    DownloadSpeed = _match_func(DownloadSpeedUnit, DownloadSpeed)

    RequiredSeconds = TotalDownload   / DownloadSpeed
    RequiredMinutes = RequiredSeconds / 60
    RequiredHours   = RequiredMinutes / 60

    return f'{RequiredHours = :.2f}, {RequiredMinutes = :.2f}, {RequiredSeconds = :.2f}.'

def camel_to_snake(name):
    return re.sub(r'([a-z])([A-Z])', r'\1_\2', name).lower()

if __name__ == '__main__':
    encryption_speed_test(algorithmName='cc20', key_len=32, iv_len=12)
