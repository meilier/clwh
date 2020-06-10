#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:Tao Yimin
# Time  :2019/5/7 19:29
from Cryptodome.Random import get_random_bytes

from t_encryption.AESCipher import AESCipher
from t_encryption.RSACipher import RSACipher
from t_encryption.config import Config
from phe import paillier
import json
from t_encryption.he import HeEnc
import collections

import re

class ThreeEncClient:
    def __init__(self):
        super().__init__()
        # 随机生成aes的密钥
        self.aes_key = get_random_bytes(16)
        print('随机生成的aes密钥:\n%s' % self.aes_key)
        self.aes_cipher = AESCipher(self.aes_key)
        self.rsa_cipher = RSACipher()
        self.mhe = HeEnc()

    def three_layer_enc_bak(self, ori_dict):
        for k, v in ori_dict.items():
            if re.search('weight', k):
                for j in v:
                    ori_dict[k] = [self.mhe.public_key.encrypt(x) for x in j]
            else:
                ori_dict[k] = [self.mhe.public_key.encrypt(x) for x in v]
        text = self.mhe.getSerialisedDataDict(self.mhe.public_key, ori_dict)

        # 使用aes密钥对数据进行加密
        encrypt_text = self.aes_cipher.encrypt(text)
        print('经过aes加密后的数据:\n%s' % encrypt_text)

        # 使用客户端私钥对aes密钥签名
        signature = self.rsa_cipher.sign(Config.CLIENT_PRIVATE_KEY, self.aes_key)
        print('签名:\n%s' % signature)

        # 使用服务端公钥加密aes密钥
        encrypt_key = self.rsa_cipher.encrypt(Config.SERVER_PUBLIC_KEY, self.aes_key)
        print('加密后的aes密钥:\n%s' % encrypt_key)

        return encrypt_text, encrypt_key, signature
    
    def three_layer_deenc_bak(self,encrypt_text, encrypt_key, signature):
        # 服务端发送密文、签名和加密后的aes密钥
        print('\n************************分割线************************\n')
        # 接收到服务端发送过来的signature encrypt_key encrypt_text
        # 客户端代码
        # 使用客户端私钥对加密后的aes密钥解密
        naes_key = self.rsa_cipher.decrypt(Config.CLIENT_PRIVATE_KEY, encrypt_key)
        print('解密后的aes密钥:\n%s' % naes_key)
        # 使用服务端公钥验签
        result = self.rsa_cipher.verify(Config.SERVER_PUBLIC_KEY, naes_key, signature)
        print('验签结果:\n%s' % result)

        # 使用aes私钥解密密文
        aes_cipher = AESCipher(naes_key)
        decrypt_text = aes_cipher.decrypt(encrypt_text)
        print('经过aes解密后的数据:\n%s' % decrypt_text)

        # 解密好的数据再进行反向序列化，获得同态加密数据
        c_pub_k, c_enc_nums_rec = self.mhe.deserialDataDict(decrypt_text)

        # 同态解密获得数据
        for k, v in c_enc_nums_rec.items():
            c_enc_nums_rec[k] = [self.mhe.private_key.decrypt(x) for x in v]

        return c_enc_nums_rec

    def three_layer_enc(self, ori_dict):
        
        text = json.dumps(ori_dict)
        # 使用aes密钥对数据进行加密
        encrypt_text = self.aes_cipher.encrypt(text)
        # print('经过aes加密后的数据:\n%s' % encrypt_text)

        # 使用客户端私钥对aes密钥签名
        signature = self.rsa_cipher.sign(Config.CLIENT_PRIVATE_KEY, self.aes_key)
        print('签名:\n%s' % signature)

        # 使用服务端公钥加密aes密钥
        encrypt_key = self.rsa_cipher.encrypt(Config.SERVER_PUBLIC_KEY, self.aes_key)
        print('加密后的aes密钥:\n%s' % encrypt_key)

        return encrypt_text, encrypt_key, signature
    
    def three_layer_deenc(self,encrypt_text, encrypt_key, signature):
        # 服务端发送密文、签名和加密后的aes密钥
        print('\n************************分割线************************\n')
        # 接收到服务端发送过来的signature encrypt_key encrypt_text
        # 客户端代码
        # 使用客户端私钥对加密后的aes密钥解密
        naes_key = self.rsa_cipher.decrypt(Config.CLIENT_PRIVATE_KEY, encrypt_key)
        print('解密后的aes密钥:\n%s' % naes_key)
        # 使用服务端公钥验签
        result = self.rsa_cipher.verify(Config.SERVER_PUBLIC_KEY, naes_key, signature)
        print('验签结果:\n%s' % result)

        # 使用aes私钥解密密文
        aes_cipher = AESCipher(naes_key)
        decrypt_text = aes_cipher.decrypt(encrypt_text)
        # print('经过aes解密后的数据:\n%s' % decrypt_text)

        # 解密好的数据再进行反向序列化，获得同态加密数据
        c_enc_nums_rec = json.loads(decrypt_text, object_pairs_hook=collections.OrderedDict)

        return c_enc_nums_rec





class ThreeEncServer:
    def __init__(self):
        super().__init__()
        # 随机生成aes的密钥
        self.aes_key = get_random_bytes(16)
        print('随机生成的aes密钥:\n%s' % self.aes_key)
        self.aes_cipher = AESCipher(self.aes_key)
        self.rsa_cipher = RSACipher()
        self.mhe = HeEnc()
        self.client_pub_k = 0

    def three_layer_enc_bak(self, mid_dict):
        # 服务器端序列化
        s_text = self.mhe.getSerialisedDataDict(self.client_pub_k, mid_dict)
        # 下面从服务器端将数据传送给客户端


        # 使用aes密钥对数据进行加密
        encrypt_text = self.aes_cipher.encrypt(s_text)
        # print('经过aes加密后的数据:\n%s' % encrypt_text)

        # 使用服务端私钥对aes密钥签名
        signature = self.rsa_cipher.sign(Config.SERVER_PRIVATE_KEY, aes_key)
        print('签名:\n%s' % signature)

        # 使用客户端公钥加密aes密钥
        encrypt_key = self.rsa_cipher.encrypt(Config.CLIENT_PUBLIC_KEY, aes_key)
        print('加密后的aes密钥:\n%s' % encrypt_key)

        return encrypt_text, encrypt_key, signature


    def three_layer_deenc_bak(self,encrypt_text, encrypt_key, signature):
        # 客户端发送密文、签名和加密后的aes密钥
        print('\n************************分割线************************\n')
        # 接收到客户端发送过来的signature encrypt_key encrypt_text

        # 服务端代码
        # 使用服务端私钥对加密后的aes密钥解密
        naes_key = self.rsa_cipher.decrypt(Config.SERVER_PRIVATE_KEY, encrypt_key)
        print('解密后的aes密钥:\n%s' % naes_key)

        # 使用客户端公钥验签
        result = self.rsa_cipher.verify(Config.CLIENT_PUBLIC_KEY, naes_key, signature)
        print('验签结果:\n%s' % result)

        # 使用aes私钥解密密文
        aes_cipher = AESCipher(naes_key)
        decrypt_text = aes_cipher.decrypt(encrypt_text)
        # print('经过aes解密后的数据:\n%s' % decrypt_text)

        # 解密好的数据再进行反向序列化，获得同态加密数据
        self.client_pub_k, s_enc_nums_rec = self.mhe.deserialData(decrypt_text)

        return s_enc_nums_rec

    def three_layer_enc(self, mid_dict):
        # 服务器端序列化
        s_text = json.dumps(mid_dict)
        # 下面从服务器端将数据传送给客户端


        # 使用aes密钥对数据进行加密
        encrypt_text = self.aes_cipher.encrypt(s_text)
        #print('经过aes加密后的数据:\n%s' % encrypt_text)

        # 使用服务端私钥对aes密钥签名
        signature = self.rsa_cipher.sign(Config.SERVER_PRIVATE_KEY, self.aes_key)
        print('签名:\n%s' % signature)

        # 使用客户端公钥加密aes密钥
        encrypt_key = self.rsa_cipher.encrypt(Config.CLIENT_PUBLIC_KEY, self.aes_key)
        print('加密后的aes密钥:\n%s' % encrypt_key)

        return encrypt_text, encrypt_key, signature


    def three_layer_deenc(self,encrypt_text, encrypt_key, signature):
        # 客户端发送密文、签名和加密后的aes密钥
        print('\n************************分割线************************\n')
        # 接收到客户端发送过来的signature encrypt_key encrypt_text

        # 服务端代码
        # 使用服务端私钥对加密后的aes密钥解密
        naes_key = self.rsa_cipher.decrypt(Config.SERVER_PRIVATE_KEY, encrypt_key)
        print('解密后的aes密钥:\n%s' % naes_key)

        # 使用客户端公钥验签
        result = self.rsa_cipher.verify(Config.CLIENT_PUBLIC_KEY, naes_key, signature)
        print('验签结果:\n%s' % result)

        # 使用aes私钥解密密文
        aes_cipher = AESCipher(naes_key)
        decrypt_text = aes_cipher.decrypt(encrypt_text)
        #print('经过aes解密后的数据:\n%s' % decrypt_text)

        # 解密好的数据再进行反向序列化，获得同态加密数据
        s_enc_nums_rec = json.loads(decrypt_text, object_pairs_hook=collections.OrderedDict)

        return s_enc_nums_rec









# 对加密数据进行操作
# return_list = [(old_list[i] + s_enc_nums_rec[i]) for i in range(10)]






