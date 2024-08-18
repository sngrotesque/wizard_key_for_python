from PIL import Image, ImageDraw, ImageFont
from .crypto import get_digest
import numpy as np
import struct
import zlib

PNG_HEAD = b'\x89PNG\r\n\x1A\n'
PNG_IEND = b'\0\0\0\0IEND\xaeB`\x82'

def hex_to_number(hexStream :bytes):
    return struct.unpack('>I', hexStream)[0]

def number_to_hex(number :int):
    return struct.pack('>I', number)

class ImageToCharacterImage:
    def __init__(self, src_path :str, dst_path :str,
                resize_factor :float = 0.7,
                sample_step   :int   = 3,
                scale         :int   = 2,
                font_size     :int   = 8,
                font_family   :str   = 'consola.ttf',
                font_encoding :str   = 'UTF-8',
                background    :int   = 0xffffff):
        self.src_path      = src_path
        self.dst_path      = dst_path
        self.resize_factor = resize_factor
        self.sample_step   = sample_step
        self.scale         = scale

        self.font          = ImageFont.truetype(font_family, font_size, encoding=font_encoding)
        self.width         = 0
        self.height        = 0
        self.background    = self.__get_rgb_tuple(background)

        self.pix           = None

        with Image.open(self.src_path) as img:
            # print(f'Original image width: {img.size[0]}, height: {img.size[1]}.')
            new_size = (int(img.size[0] * self.resize_factor), int(img.size[1] * self.resize_factor))
            with img.resize(new_size, Image.Resampling.LANCZOS) as new_img:
                with new_img.convert('RGB') as new_new_img:
                    self.pix       = new_new_img.load()
                    self.width     = new_new_img.size[0]
                    self.height    = new_new_img.size[1]

        self.canvas        = np.ndarray((self.height * self.scale, self.width * self.scale, 3), np.uint8)
        self.canvas[:,:,:] = self.background

        # print(f'New image width: {self.width}, height: {self.height}')

    def __get_rgb_tuple(self, value :int):
        return (value >> 16, (value & 0xff00) >> 8, value & 0xff)

    def __get_brightness_of_color(self, r :int, g :int, b :int, level :int):
        if level == 32: # Level: 32
            index = int((r*0.299 + g*0.587 + b*0.114) / 8)
            return r'WMHSQGFEDB@8&#$%?+\/^][|!*=~-:. '[index-1 if index == 32 else index]
        elif level == 16: # Level: 16
            index = int((r*0.299 + g*0.587 + b*0.114) / 16)
            return r'WM@GB%8&#*+=-:. '[index-1 if index == 16 else index]
        elif level == 8: # Level: 8
            index = int((r*0.299 + g*0.587 + b*0.114) / 32)
            return r'#*+=-:. '[index-1 if index == 8 else index]

    def __draw_primary_colours(self, draw_obj :ImageDraw.Draw, string :str):
        length = len(string)
        index = 0
        for y in range(self.height):
            for x in range(self.width):
                if (not (x % self.sample_step)) and (not (y % self.sample_step)):
                    draw_obj.text((x * self.scale, y *self.scale), text = string[index % length], fill = self.pix[x, y], font = self.font)
                    index += 1

    def __draw_black_white(self, draw_obj :ImageDraw.Draw, fore_color :int, level :int):
        # file = open('C:/Users/sn/Desktop/收纳/result.txt', 'w', encoding='UTF-8')
        fore_color = self.__get_rgb_tuple(fore_color)
        for y in range(self.height):
            for x in range(self.width):
                if (not (x % self.sample_step)) and (not (y % self.sample_step)):
                    r, g, b = self.pix[x, y]
                    char = self.__get_brightness_of_color(r, g, b, level)
                    draw_obj.text((x * self.scale, y *self.scale), text = char,
                        fill = fore_color, font = self.font)
        #             file.write(char)
        #     file.write('\n')
        # file.close()

    def draw(self,  draw_string :str = 'helloworld',
                    fore_color :int = 0x0000000,
                    blackAndWhite :bool = False,
                    brightnessLevel :int = 32,
                    show :bool = False):
        if (brightnessLevel != 32) and (brightnessLevel != 16) and (brightnessLevel != 8):
            raise RuntimeError(f'The black and white levels of the image can only be 32, 16, and 8. You provided {brightnessLevel}.')

        with Image.fromarray(self.canvas) as img:
            draw = ImageDraw.Draw(img)
            if not blackAndWhite:
                self.__draw_primary_colours(draw, draw_string)
            else:
                self.__draw_black_white(draw, fore_color, brightnessLevel)

            img.save(self.dst_path)
            if show:
                img.show()

class PNG_Analysis:
    def analysis(self, path :str):
        analysis_result = {
            "MD5": None,
            "SHA-1": None,
            "SHA-256": None,
            # "SHA-512": None,
            "Chunks": []
        }

        with open(path, 'rb') as f:
            file_content = f.read()

            if file_content[:8] != PNG_HEAD:
                raise TypeError(f'\'{path}\' is not a PNG image.')

            analysis_result['MD5']     = get_digest(file_content, 'md5')
            analysis_result['SHA-1']   = get_digest(file_content, 'sha1')
            analysis_result['SHA-256'] = get_digest(file_content)

            f.seek(len(PNG_HEAD)) # 将指针跳转到文件开头并跳过文件标识数据头

            while True:
                pos   = f.tell()
                
                size  = hex_to_number(f.read(4))
                name  = f.read(4).decode()
                data  = f.read(size)
                crc32 = hex_to_number(f.read(4))

                analysis_result['Chunks'].append(
                    {
                        "pos":   pos,
                        "size":  size,
                        "name":  name,
                        "data":  data,
                        "crc32": crc32
                    }
                )

                if name == 'IEND':
                    break

        return analysis_result

    def analysis_process(self, path :str, png_structure :dict[str, any]):
        with open(path, 'wb') as f:
            new_structure = png_structure['Chunks']

            while True:
                print([chunk['name'] for chunk in new_structure])

                chunk_name = input('请输入要删除的块名称：')
                if chunk_name in ('exit', 'quit', 'done'):
                    break

                if chunk_name in ('IHDR', 'IDAT', 'IEND'):
                    raise ValueError('You should not delete this chunk.')

                new_structure = [item for item in new_structure if item['name'] != chunk_name]

            f.write(PNG_HEAD)

            for item in new_structure:
                chunks = b''.join((
                    number_to_hex(item['size']),
                    item['name'].encode(),
                    item['data'],
                    number_to_hex(item['crc32'])
                ))

                f.write(chunks)

class PNG_Write:
    def __init__(self):
        self.width = None
        self.height = None
        
        self.IHDR = None
        self.IDAT = []
        self.IEND = PNG_IEND
    
    def build_IHDR(self,
                width       :int,
                height      :int,
                bit_depth   :int = 8,
                color_type  :int = 2,
                compression :int = 0,
                filter      :int = 0,
                scan_mode   :int = 0
                ) -> None:
        self.width = width
        self.height = height
        
        IHDR_chunk = struct.pack(
            '>I4sIIBBBBB',
            13,          # length
            b'IHDR',     # name
            width,       # image width
            height,      # image height
            bit_depth,   # image bit depth
            color_type,  # image color type
            compression, # compression method
            filter,      # filter method
            scan_mode    # scan mode
        )
        IHDR_crc32 = number_to_hex(zlib.crc32(IHDR_chunk[4:]))
        self.IHDR = b''.join((IHDR_chunk, IHDR_crc32))

    def build_IDAT(self, content :bytes) -> None:
        def split(data :bytes, splitNumber :int):
            # 将传入的数据按照splitNumber指定的长度进行分组，并在每个分组前添加一个00
            data = [data[x:x+splitNumber] for x in range(0, len(data), splitNumber)]
            return b'\x00' + b'\x00'.join(data)

        compressed = zlib.compress(split(content, self.width * 3))
        IDAT_chunk = struct.pack(f'>I4s{len(compressed)}s',
            len(compressed), # length
            b'IDAT',         # name
            compressed,      # data
            )
        IDAT_crc32 = number_to_hex(zlib.crc32(IDAT_chunk[4:]))
        
        IDAT = b''.join((IDAT_chunk, IDAT_crc32))
        
        self.IDAT.append(IDAT)

    def build_PNG_image(self):
        png_data = [PNG_HEAD, self.IHDR]
        
        for item in self.IDAT:
            png_data.append(item)
        
        png_data.append(self.IEND)
        
        return b''.join(png_data)
