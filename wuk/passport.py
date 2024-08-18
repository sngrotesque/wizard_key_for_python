'''
针对的文件结构（Json）

样例：
{
    "Google": {
        "account":  ["exmple 1", "exmple 2"],
        "password": ["exmple 1", "exmple 2"]
    },
    "Github": {
        "account":  ["exmple 1", "exmple 2"],
        "password": ["exmple 1", "exmple 2"]
    }
}
'''
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
import hashlib
import base64
import json

b64encode = base64.b64encode
b64decode = base64.b64decode

class AuthenticationError(Exception):
    def __init__(self, message :str):
        super().__init__(message)

class PasswordCipher:
    def __init__(self, token :bytes, dict_file_in :str, dict_file_out :str, verify_block :bytes = b'\x00\x01\x02\x03'):
        self.token = token
        self.dict_file_in = dict_file_in
        self.dict_file_out = dict_file_out
        self.verify_block = verify_block

    def build_aes_ctx(self):
        key_with_iv = PBKDF2(self.token, hashlib.sha256(self.token).digest(), 32 + 16, 15920)
        return AES.new(key_with_iv[:32], iv = key_with_iv[-16:], mode = AES.MODE_CFB, segment_size = 8)
    
    def get_dict_key(self):
        with open(self.dict_file_in, 'r', encoding='UTF-8') as f:
            json_data :dict = json.loads(f.read())
        return [*json_data.keys()]
    
    def encrypt(self, plaintext :bytes):
        aes_ctx = self.build_aes_ctx()
        ciphertext = aes_ctx.encrypt(plaintext)
        return ciphertext
    
    def decrypt(self, ciphertext :bytes):
        aes_ctx = self.build_aes_ctx()
        plaintext = aes_ctx.decrypt(ciphertext)
        return plaintext
    
    def encryption_write(self, platform_name :list[str]):
        def encryption(json_data :dict, platform_name :str, item_name :str):
            for item in range(len(json_data[platform_name][item_name])):
                plaintext = json_data[platform_name][item_name][item].encode()
                ciphertext = self.encrypt(plaintext + self.verify_block)
                json_data[platform_name][item_name][item] = b64encode(ciphertext).decode()
            return json_data

        with open(self.dict_file_in, 'r', encoding = 'UTF-8') as f:
            json_data = json.loads(f.read())

        for platform in platform_name:
            json_data = encryption(json_data, platform, 'account')
            json_data = encryption(json_data, platform, 'password')

        with open(self.dict_file_out, 'w', encoding = 'UTF-8') as f:
            f.write(json.dumps(json_data, ensure_ascii=False, indent=4))

    def decryption_write(self, platform_name :list[str]):
        def decryption(json_data :dict, platform_name :str, item_name :str):
            for item in range(len(json_data[platform_name][item_name])):
                base64_ciphertext = json_data[platform_name][item_name][item]
                ciphertext = b64decode(base64_ciphertext)
                plaintext_with_verify = self.decrypt(ciphertext)
                verify_size = len(self.verify_block)
                plaintext, verify = plaintext_with_verify[:-verify_size], plaintext_with_verify[-verify_size:]
                if verify != self.verify_block:
                    print(f'test plaintext: {plaintext}')
                    raise AuthenticationError('密码不正确或密文被修改，验证失败。')
                json_data[platform_name][item_name][item] = plaintext.decode()
            return json_data

        with open(self.dict_file_in, 'r', encoding = 'UTF-8') as f:
            json_data = json.loads(f.read())

        for platform in platform_name:
            json_data = decryption(json_data, platform, 'account')
            json_data = decryption(json_data, platform, 'password')

        with open(self.dict_file_out, 'w', encoding = 'UTF-8') as f:
            f.write(json.dumps(json_data, ensure_ascii=False, indent=4))

if __name__ == '__main__':
    user_token    = input('请输入密码：').encode()
    verify_block  = input('请输入验证块：').encode()
    dict_file_in  = input('请输入密码文件路径：')
    dict_file_out = input('请输入加/解密后密码文件路径：')
    ctx           = PasswordCipher(user_token, dict_file_in, dict_file_out, verify_block)

    ctx.encryption_write(ctx.get_dict_key())
    # ctx.decryption_write(ctx.get_dict_key())
