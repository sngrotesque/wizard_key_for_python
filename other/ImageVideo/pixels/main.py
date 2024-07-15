from typing import List
from PIL import Image

EOF = -1

def getPixel(code :str, path :str):
    '''code: 颜色类型（RGB, RGBA）, path: 图像路径
    '''
    img = Image.open(path)
    width, height = img.size
    pixels = img.load()

    rgb_a = [0 for _ in range(width * height)]

    if 'rgb' == code.lower():
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                rgb_a[y * width + x] = (r << 16) | (g << 8) | b
    elif 'rgba' == code.lower():
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                rgb_a[y * width + x] = (r << 24) | (g << 16) | (b << 8) | a
    else:
        print(f'错误的code值：{code}')
        exit(-1)

    img.close()
    return rgb_a

def rgb888_rgb565(rgb888 :List[int]):
    rgb565 = [0 for _ in range(len(rgb888))]
    
    for x in range(len(rgb888)):
        r = (rgb888[x] & 0xff0000) >> 19
        g = (rgb888[x] & 0x00ff00) >> 10
        b = (rgb888[x] & 0x0000ff) >> 3
        rgb565[x] = (r << 11) | (g << 5) | b
    
    return rgb565

def rgb565_to_byte(path :str):
    rgb888 = getPixel('rgb', path)
    rgb565 = rgb888_rgb565(rgb888)
    rgb_byte = [0 for _ in range(len(rgb565) << 1)]
    
    for x in range(len(rgb565)):
        rgb_byte[(x << 1)]     = rgb565[x] >> 8
        rgb_byte[(x << 1) + 1] = rgb565[x] & 0xff

    rgb_byte_string = f'unsigned char image[{len(rgb_byte)}] = \x7b\n'
    for x in range(len(rgb_byte)):
        rgb_byte_string += f'0x{rgb_byte[x]:02x},'
        if (x + 1) != len(rgb_byte):
            if (x + 1) % 16 == 0: rgb_byte_string += '\n'
            else: rgb_byte_string += ' '
    rgb_byte_string += '\n};'

    return rgb_byte_string

def rgb888_to_rgb565_128x160(path :str, rgb565_byte_string_path :str):
    # 请注意这个会覆盖原始图像，所以请使用副本图像
    img = Image.open(path)
    width, height = img.size
    # 如果比例不是4:5 (128:160)
    if 0.01 < abs((width / height) - (4 / 5)):
        print(width, height)
        return EOF

    if (width != 64) and (height != 80):
        img.resize((64, 80)).save(path)
    img.close()

    rgb565_string = rgb565_to_byte(path)
    with open(rgb565_byte_string_path, 'w') as f:
        f.write(rgb565_string)
    
    return rgb565_string

print(rgb888_to_rgb565_128x160('./128x160_rgb_tft_test_1.jpg', './128x160_rgb_tft_test_1.txt'))

