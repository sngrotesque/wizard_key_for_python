from typing import Callable
import hashlib
import base64
import wtools
import random
import socket
import struct
import time
import sys
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

def create_trueRandom_number(min :int, max :int):
    array_size = random.choice([1, 2, 4, 8])
    random_bytearray = os.urandom(array_size)

    random_number = -1
    if array_size == 1:
        random_number = struct.unpack('>B', random_bytearray)[0]
    elif array_size == 2:
        random_number = struct.unpack('>H', random_bytearray)[0]
    elif array_size == 4:
        random_number = struct.unpack('>I', random_bytearray)[0]
    elif array_size == 8:
        random_number = struct.unpack('>Q', random_bytearray)[0]

    return random_number % (max - min + 1) + min

def pixiv_use(get_follow_list :bool = False):
    follow_list_save_path = 'pixiv_follower.txt'
    pitcher_list_save_path = 'F:/Pitchers/Pixiv'
    https_proxies = 'http://localhost:8081'
    
    pix = wtools.pixiv(38279179, 'E:/pixiv_cookie.txt', save_path = pitcher_list_save_path,
                    proxies = https_proxies, maxNumberThreads=16)
    
    if get_follow_list:
        print('开始获取关注列表的所有作者ID...')
        artist_list = pix.getTotalArtistList()
        print(f'获取完毕，保存至{follow_list_save_path}')
        wtools.utils.fwrite(follow_list_save_path,
                            data = '\n'.join(artist_list).encode())
    else:
        artist_list = wtools.utils.fread(follow_list_save_path).decode().split()
    
    for artist_id in artist_list:
        pix.multiThreadedDownload(artist_id, f'{pitcher_list_save_path}/{artist_id}')
        break

if __name__ == '__main__':
    pixiv_use()
