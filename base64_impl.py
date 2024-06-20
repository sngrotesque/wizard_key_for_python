RFC4648_BASE64_ENCODE = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
RFC4648_BASE64_DECODE = bytes([
    00,00,00,00, 00,00,00,00, 00,00,00,00, 00,00,00,00,
    00,00,00,00, 00,00,00,00, 00,00,00,00, 00,00,00,00,
    00,00,00,00, 00,00,00,00, 00,00,00,62, 00,00,00,63,
    52,53,54,55, 56,57,58,59, 60,61,00,00, 00, 0,00,00,
    00, 0, 1, 2,  3, 4, 5, 6,  7, 8, 9,10, 11,12,13,14,
    15,16,17,18, 19,20,21,22, 23,24,25,00, 00,00,00,00,
    00,26,27,28, 29,30,31,32, 33,34,35,36, 37,38,39,40,
    41,42,43,44, 45,46,47,48, 49,50,51,00, 00,00,00,00,

    00,00,00,00, 00,00,00,00, 00,00,00,00, 00,00,00,00,
    00,00,00,00, 00,00,00,00, 00,00,00,00, 00,00,00,00,
    00,00,00,00, 00,00,00,00, 00,00,00,00, 00,00,00,00,
    00,00,00,00, 00,00,00,00, 00,00,00,00, 00,00,00,00,
    00,00,00,00, 00,00,00,00, 00,00,00,00, 00,00,00,00,
    00,00,00,00, 00,00,00,00, 00,00,00,00, 00,00,00,00,
    00,00,00,00, 00,00,00,00, 00,00,00,00, 00,00,00,00,
    00,00,00,00, 00,00,00,00, 00,00,00,00, 00,00,00,00
])

class Base64:
    def EN_MAP_1(self, b, i):
        return RFC4648_BASE64_ENCODE[b[i] >> 2]

    def EN_MAP_2(self, b, i):
        return RFC4648_BASE64_ENCODE[((b[i] & 0x3) << 4) | (b[i+1] >> 4)]

    def EN_MAP_3(self, b, i):
        return RFC4648_BASE64_ENCODE[((b[i+1] & 0xf) << 2) | (b[i+2] >> 6)]

    def EN_MAP_4(self, b, i):
        return RFC4648_BASE64_ENCODE[b[i+2] & 0x3f]

    def get_encode_length(self, length):
        return ((length // 3 + 1) * 4) if length % 3 else (length // 3 * 4)

    def encode(self, buffer :bytes):
        result_len = self.get_encode_length(len(buffer))
        result = bytearray(bytes(result_len))

        loop_max = result_len - 2
        for si, di in zip(range(0, loop_max, 3), range(0, loop_max, 4)):
            result[di]   = self.EN_MAP_1(buffer, si)
            result[di+1] = self.EN_MAP_2(buffer, si)
            result[di+2] = self.EN_MAP_3(buffer, si)
            result[di+3] = self.EN_MAP_4(buffer, si)

        if (len(buffer) % 3) == 1:
            result[di - 2] = b'='
        if (len(buffer) % 3) == 2:
            result[di - 1] = b'='

        return bytes(result)

    def DE_MAP_1(self, b, i):
        return (RFC4648_BASE64_DECODE[b[i]] << 2) | (RFC4648_BASE64_DECODE[b[i+1]] >> 4)

    def DE_MAP_2(self, b, i):
        return ((RFC4648_BASE64_DECODE[b[i+1]] & 0x0F) << 4) | (RFC4648_BASE64_DECODE[b[i+2]] >> 2)

    def DE_MAP_3(self, b, i):
        return ((RFC4648_BASE64_DECODE[b[i+2]] & 0x03) << 6) | RFC4648_BASE64_DECODE[b[i+3]]

    def get_decode_length(self, buffer :bytes):
        tmp_len = len(buffer) // 4 * 3
        if buffer[-1] == ord(b'='):
            tmp_len -= 1
        if buffer[-2] == ord(b'='):
            tmp_len -= 1
        return tmp_len

    def decode(self, buffer :bytes):
        if isinstance(buffer, str):
            buffer = buffer.encode()

        if (len(buffer) % 4):
            raise TypeError('长度必须是4的倍数。')

        buffer = buffer.rstrip(b'=')

        result_len = self.get_decode_length(buffer)
        result = bytearray(bytes(result_len))

        loop_max = result_len - 2
        for si, di in zip(range(0, loop_max, 4), range(0, loop_max, 3)):
            result[di]   = self.DE_MAP_1(buffer, si)
            try:
                result[di+1] = self.DE_MAP_2(buffer, si)
            except:
                print(self.DE_MAP_2(buffer, si))
                exit()
            result[di+2] = self.DE_MAP_3(buffer, si)

        return bytes(result)

if __name__ == '__main__':
    data = ('GET / HTTP/1.1\r\n'
            'Host: passport.bilibili.com\r\n'
            'Accept: */*\r\n'
            'Connection: keep-alive\r\n'
            'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0\r\n'
            '\r\n').encode()

    b64 = Base64()
    res = b64.encode(data)
    
    print(b64.decode(res))
