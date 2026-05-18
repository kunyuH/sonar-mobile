from ..lib.gmssl import sm4

class Encrypt:
    def __init__(self, key):
        self.key = key
        pass

    def sm4_encrypt(self, data_str):
        """
        sm4 加密
        """
        sm4Alg = sm4.CryptSM4()  # 实例化sm4
        sm4Alg.set_key(self.key.encode(), sm4.SM4_ENCRYPT)  # 设置密钥
        dateStr = str(data_str)
        enRes = sm4Alg.crypt_ecb(dateStr.encode())  # 开始加密,bytes类型，ecb模式
        ciphertext = enRes.hex()
        return ciphertext  # 返回十六进制值

    def sm4_decrypt(self, ciphertext):
        """
        sm4 解密
        """
        sm4Alg = sm4.CryptSM4()  # 实例化sm4
        sm4Alg.set_key(self.key.encode(), sm4.SM4_DECRYPT)  # 设置密钥
        deRes = sm4Alg.crypt_ecb(bytes.fromhex(ciphertext))  # 开始解密。十六进制类型,ecb模式
        data_str = deRes.decode()
        return data_str
