from typing import List
from PIL import Image

CYAN = '\x1b[96m'
RESET = '\x1b[0m'

def fread(fn :str, mode :str = 'rb', encoding = None):
    with open(fn, mode, encoding = encoding) as f:
        return f.read()

def fwrite(fn :str, data :object, mode :str = 'wb', encoding = None):
    with open(fn, mode, encoding = encoding) as f:
        f.write(data)

class rgb:
    def __init__(self, path :str, save_path :str = None):
        self.path      = path      # 图像路径
        self.save_path = save_path # 经过resize调整后的图像的保存路径
        self.width   :int = 0 # 使用时会变的宽度
        self.height  :int = 0 # 使用时会变的高度

        self.rgb888 :list = None # 储存图像RGB888值，单个像素以24位二进制数表示
        self.rgb565 :list = None # 储存图像RGB888值，单个像素以16位二进制数表示

        self.img :Image.Image = None # 用于储存Image对象的变量
        self.pixel            = 0 # 由Pillow库读取到的图像详细源信息

    def image_open(self):
        if not self.path:
            print(f'[>>>>]: path is null.')
            return

        try:
            self.img = Image.open(self.path) # 读取图像
        except FileNotFoundError:
            exit(f'路径错误：{self.path}')

    def image_size(self):
        self.width, self.height = self.img.size # 获取宽高

    def image_resize(self, width: int, height :int):
        temp = self.img.resize((width, height))
        self.img.close()
        self.img = temp
        self.width = width
        self.height = height
        if self.save_path:
            self.img.save(self.save_path)

    def image_close(self):
        # 如果对象是Image.Image，那么就关闭
        if isinstance(self.img, Image.Image):
            self.img.close()

    # 获取图像的RGB888值，忽略A通道（如果有的话）
    def get_rgb888(self):
        self.pixel = self.img.load() # 获取像素对象

        size = self.width * self.height # 得到RGB88列表长度
        self.rgb888 = [0 for _ in range(size)] # 生成空列表

        for y in range(self.height):
            for x in range(self.width):
                if self.img.mode == 'RGB':
                    r, g, b = self.pixel[x, y]
                elif self.img.mode == 'RGBA':
                    r, g, b, _ = self.pixel[x, y]
                # 将RGB888信息存入self.rgb888列表
                self.rgb888[y * self.width + x] = (r<<16) | (g<<8) | b
                # print(f'get_rgb888 function: '
                #     f'width: {self.width}, height: {self.height}, '
                #     f'index: {y*self.width+x: >5d}, '
                #     f'r: {r:02x}, g: {g:02x}, b: {b:02x}')

    # 获取图像的RGB565值
    def get_rgb565(self):
        # 获取RGB888值并存入self.rgb888列表
        if not self.rgb888:
            self.get_rgb888()

        self.rgb565 = [0 for _ in range(len(self.rgb888))] # 生成空的rgb565列表

        for x in range(len(self.rgb888)):
            r = (self.rgb888[x] >> 19) << 11
            g = (((self.rgb888[x] >> 8) & 0xff) >> 2) << 5
            b = (self.rgb888[x] & 0xff) >> 3
            self.rgb565[x] = r | g | b

    # 将传入的列表转为单个元素为8位的数组（字符串）
    def convert_8bit_string(self, rgb_list :List[int]):
        return f'uint8_t image[{len(rgb_list)}] = ' + \
        '{' + \
            ', '.join(f'0x{value:02x}' for value in rgb_list) + \
        '};'

    # 将传入的列表转为单个元素为16位的数组（字符串）
    def convert_16bit_string(self, rgb_list :List[int]):
        lines = []
        for i in range(0, len(rgb_list), 16):
            line = ', '.join(f'0x{value:04x}' for value in rgb_list[i:i+16])
            lines.append(f'    {line}')
        return f'static const uint16_t image[{len(rgb_list)}] = ' + '{\n' + ',\n'.join(lines) + '\n};'

    # 将图像转为小于等于128x160像素并转为单元素为16位的C数组
    def convert_128x160_string(self, proportionallyResize :bool = False):
        self.image_open()
        self.image_size()
        
        # 等比例缩小到小于等于128x160的分辨率
        if proportionallyResize:
            MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = 128, 160
            scale = min(MAX_IMAGE_WIDTH / self.width, MAX_IMAGE_HEIGHT / self.height)
            new_width, new_height  = self.width * scale, self.height * scale
            # 如果分辨率大于106*133
            while (new_width * new_height) > 14098:
                new_width  *= 0.99999
                new_height *= 0.99999
            self.image_resize(int(new_width), int(new_height))
        else:
            # 不等比例缩小，但需要输入的图像分辨率是4比5的。
            if 0.01 < abs((self.width / self.height) - (4 / 5)):
                print(f'错误的图像分辨率比例：{self.width}x{self.height}')
                print(f'分辨率比例必须为4:5，误差值为0.01')
                return
            if (self.width != 106) and (self.height != 133):
                self.image_resize(106, 133)

        self.get_rgb565()
        self.image_close()
        return self.convert_16bit_string(self.rgb565)

image = 'p:/Lycoris_Recoil/FbU1_1NaIAITEM1.jpg'
obj = rgb(image)
uint16 = obj.convert_128x160_string(True)

c_uint16_string = ''.join(
    '#ifndef __PICTURE_H\n'
    '#define __PICTURE_H\n'
    '#include <stdint.h>\n'
    '\n' +
    f'#define IMAGE_WIDTH  {obj.width}\n'
    f'#define IMAGE_HEIGHT {obj.height}\n'
    '\n' + 
    uint16 + '\n'
    '\n'
    '#endif\n')
fwrite('E:/Projects/STM32/1.8_TFT_128x160_rgb565/Hardware/Picture.h',
    c_uint16_string, mode = 'w')
