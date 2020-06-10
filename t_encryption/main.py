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
from he import private_key

# 客户端代码
# l = [1,2,3]
# text = "".join([str(x) for x in l])
# 反序列化操作取出被同态加密数据
received_dict = json.loads(he.getSerialisedData())
pk = received_dict['public_key']
public_key_rec = paillier.PaillierPublicKey(n = int(pk['n']))
enc_nums_rec = [
    paillier.EncryptedNumber(public_key_rec, int(x[0]), int(x[1]))
    for x in received_dict['values']
]


ps_list = [-0.07596425712108612, -0.23666907846927643, -0.0026714717969298363, 0.007066658232361078, -0.07952287793159485, 0.07049212604761124, 0.0499127134680748, 0.02685585618019104, 0.28861308097839355, 0.08262384682893753]

return_list = [(ps_list[i] + enc_nums_rec[i]) for i in range(10)]

# 运算完毕进行序列化操作
enc_with_one_pub_key2 = {}
enc_with_one_pub_key2['public_key'] = {'n': public_key_rec.n}
enc_with_one_pub_key2['values'] = [
    (str(x.ciphertext()), x.exponent) for x in return_list
]
serialised = json.dumps(enc_with_one_pub_key2)
text = serialised

# 随机生成aes的密钥
aes_key = get_random_bytes(16)
print('随机生成的aes密钥:\n%s' % aes_key)

aes_cipher = AESCipher(aes_key)
rsa_cipher = RSACipher()

# 使用aes密钥对数据进行加密
encrypt_text = aes_cipher.encrypt(text)
print('经过aes加密后的数据:\n%s' % encrypt_text)

# 使用客户端私钥对aes密钥签名
signature = rsa_cipher.sign(Config.CLIENT_PRIVATE_KEY, aes_key)
print('签名:\n%s' % signature)

# 使用服务端公钥加密aes密钥
encrypt_key = rsa_cipher.encrypt(Config.SERVER_PUBLIC_KEY, aes_key)
print('加密后的aes密钥:\n%s' % encrypt_key)

# 客户端发送密文、签名和加密后的aes密钥
print('\n************************分割线************************\n')
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
print('经过aes解密后的数据:\n%s' % decrypt_text)

# 解密好的数据再进行反向序列化，获得同态加密数据
received_dict = json.loads(decrypt_text)
pk2 = received_dict['public_key']
public_key_rec2 = paillier.PaillierPublicKey(n=int(pk['n']))
enc_nums_rec2 = [
   paillier.EncryptedNumber(public_key_rec, int(x[0]), int(x[1]))
    for x in received_dict['values']
]

# 同态解密获得数据
res = [private_key.decrypt(x) for x in enc_nums_rec2]

print(res)
