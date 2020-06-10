from phe import paillier
import json
import collections


class HeEnc():
    """
    同态加密函数类
    """

    def __init__(self):
        self.public_key, self.private_key = paillier.generate_paillier_keypair()




    # 序列化函数，将public_key以及加密数据序列化
    def getSerialisedData(self, encrypted_number_list):
            enc_with_one_pub_key = {}
            enc_with_one_pub_key['public_key'] = {'n': self.public_key.n}
            enc_with_one_pub_key['values'] = [
                (str(x.ciphertext()), x.exponent) for x in encrypted_number_list
            ]
            serialised = json.dumps(enc_with_one_pub_key)
            return serialised
    # 反序列化函数，获取public_key，以及加密数据
    def deserialData(self, serialised):
        received_dict = json.loads(serialised)
        pk = received_dict['public_key']
        public_key_rec = paillier.PaillierPublicKey(n=int(pk['n']))
        enc_nums_rec = [
            paillier.EncryptedNumber(public_key_rec, int(x[0]), int(x[1]))
            for x in received_dict['values']
        ]
        return public_key_rec, enc_nums_rec

    # 序列化函数，将public_key以及加密数据序列化
    def getSerialisedDataDict(self, pub_k, encrypted_number_dict):
            enc_with_one_pub_key = collections.OrderedDict()
            enc_with_one_pub_key['public_key'] = {'n': pub_k.n}
            for k, v in encrypted_number_dict:
                enc_with_one_pub_key[k] = [
                    (str(x.ciphertext()), x.exponent) for x in v
                ]
            serialised = json.dumps(enc_with_one_pub_key)
            return serialised
    # 反序列化函数，获取public_key，以及加密数据
    def deserialDataDict(self, serialised):
        received_dict = json.loads(serialised, object_pairs_hook=collections.OrderedDict)
        pk = received_dict['public_key']
        del received_dict['public_key']
        public_key_rec = paillier.PaillierPublicKey(n=int(pk['n']))
        for k, v in received_dict.items():
            received_dict[k] = [
                paillier.EncryptedNumber(public_key_rec, int(x[0]), int(x[1]))
                for x in v
            ]
        return public_key_rec, received_dict
    





