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

import wtools.utils

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
    follow_list_save_path = 'pixiv_follower.txt'
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

def speed_test():
    buffer = os.urandom(256 * 1024**2)

    print(f'original buffer length: {len(buffer)}.')

    start = time.time()
    result = base64.b64encode(buffer)
    stop = time.time()

    print(f'encoding time: {stop-start:.4f}')

    start = time.time()
    result = base64.b64decode(result)
    stop = time.time()

    print(f'decoding time: {stop-start:.4f}')

def total_download_time_required(TotalDownload :float, DownloadSpeed :float, TotalDwonloadUnit: str = 'GB', DownloadSpeedUnit :str = 'MB'):
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
    print(camel_to_snake('TotalDownloadTimeRequired'))
