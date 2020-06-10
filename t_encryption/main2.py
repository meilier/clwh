#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:Tao Yimin
# Time  :2019/5/7 19:29
from Cryptodome.Random import get_random_bytes

from AESCipher import AESCipher
from RSACipher import RSACipher
from config import Config
from phe import paillier
import json
import he
from he import HeEnc

mHe = HeEnc()

pub_k = mHe.public_key
pri_k = mHe.private_key


old_list = [-0.07596425712108612, -0.23666907846927643, -0.0026714717969298363, 0.007066658232361078, -0.07952287793159485, 0.07049212604761124, 0.0499127134680748, 0.02685585618019104, 0.28861308097839355, 0.08262384682893753]

new_list = [-0.08014976978302002, -0.24069957435131073, -0.012351605109870434, 0.01167038083076477, -0.0750594511628151, 0.06132391467690468, 0.053481679409742355, 0.02685585618019104, 0.3005945384502411, 0.08262384682893753]

secret_number_list = [(new_list[i] - old_list[i]) for i in range(10)]

encrypted_number_list = [pub_k.encrypt(x) for x in secret_number_list]

# 客户端序列化

text = mHe.getSerialisedData(encrypted_number_list)
# 随机生成aes的密钥
aes_key = get_random_bytes(16)
print('随机生成的aes密钥:\n%s' % aes_key)

aes_cipher = AESCipher(aes_key)
rsa_cipher = RSACipher()

# 使用aes密钥对数据进行加密
encrypt_text = aes_cipher.encrypt(text)
#print('经过aes加密后的数据:\n%s' % encrypt_text)

# 使用客户端私钥对aes密钥签名
signature = rsa_cipher.sign(Config.CLIENT_PRIVATE_KEY, aes_key)
print('签名:\n%s' % signature)

# 使用服务端公钥加密aes密钥
encrypt_key = rsa_cipher.encrypt(Config.SERVER_PUBLIC_KEY, aes_key)
print('加密后的aes密钥:\n%s' % encrypt_key)

# 客户端发送密文、签名和加密后的aes密钥

# 接收到客户端发送过来的signature encrypt_key encrypt_text

# 服务端代码
# 使用服务端私钥对加密后的aes密钥解密
aes_key = rsa_cipher.decrypt(Config.SERVER_PRIVATE_KEY, encrypt_key)
print('解密后的aes密钥:\n%s' % aes_key)

# 使用客户端公钥验签
result = rsa_cipher.verify(Config.CLIENT_PUBLIC_KEY, aes_key, signature)
print('验签结果:\n%s' % result)

# 使用aes私钥解密密文
aes_cipher = AESCipher(aes_key)
decrypt_text = aes_cipher.decrypt(encrypt_text)
#print('经过aes解密后的数据:\n%s' % decrypt_text)

# 解密好的数据再进行反向序列化，获得同态加密数据
s_pub_k, s_enc_nums_rec = mHe.deserialData(decrypt_text)



# 对加密数据进行操作
return_list = [(old_list[i] + s_enc_nums_rec[i]) for i in range(10)]
print('\n中心服务器对加密数据进行运算\n')

print('\n************************分割线************************\n')

# 服务器端序列化
s_text = mHe.getSerialisedData(return_list)

# 下面从服务器端将数据传送给客户端

# 随机生成aes的密钥
aes_key = get_random_bytes(16)
print('随机生成的aes密钥:\n%s' % aes_key)

aes_cipher = AESCipher(aes_key)
rsa_cipher = RSACipher()

# 使用aes密钥对数据进行加密
encrypt_text = aes_cipher.encrypt(s_text)
#print('经过aes加密后的数据:\n%s' % encrypt_text)

# 使用服务端私钥对aes密钥签名
signature = rsa_cipher.sign(Config.SERVER_PRIVATE_KEY, aes_key)
print('签名:\n%s' % signature)

# 使用客户端公钥加密aes密钥
encrypt_key = rsa_cipher.encrypt(Config.CLIENT_PUBLIC_KEY, aes_key)
print('加密后的aes密钥:\n%s' % encrypt_key)

# 服务端发送密文、签名和加密后的aes密钥

# 接收到服务端发送过来的signature encrypt_key encrypt_text


# 客户端代码
# 使用客户端私钥对加密后的aes密钥解密
aes_key = rsa_cipher.decrypt(Config.CLIENT_PRIVATE_KEY, encrypt_key)
print('解密后的aes密钥:\n%s' % aes_key)

# 使用服务端公钥验签
result = rsa_cipher.verify(Config.SERVER_PUBLIC_KEY, aes_key, signature)
print('验签结果:\n%s' % result)

# 使用aes私钥解密密文
aes_cipher = AESCipher(aes_key)
decrypt_text = aes_cipher.decrypt(encrypt_text)
#print('经过aes解密后的数据:\n%s' % decrypt_text)

# 解密好的数据再进行反向序列化，获得同态加密数据
c_pub_k, c_enc_nums_rec = mHe.deserialData(decrypt_text)

# 同态解密获得数据
res = [mHe.private_key.decrypt(x) for x in c_enc_nums_rec]

print("接下来进行训练参与方获得数据:", res)

