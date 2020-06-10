import os
import numpy as np
import torch
import datetime
from torchvision.datasets import mnist # 导入 pytorch 内置的 mnist 数据

from torch import nn
from torch.autograd import Variable
from torch.utils.data import DataLoader
from peer_server.net import classifier
from t_encryption.ThreeLayerEnc import ThreeEncServer
from op_peer.op_chain import ChainInterface
from util.utils import mnist_base_path

from itertools import chain

import matplotlib.pyplot as plt
from numpy import math

import re

# %matplotlib inline


class Server:
    def __init__(self):
        super().__init__()
        self.ps_dict = torch.load(mnist_base_path)
        for k, v in self.ps_dict.items():
            self.ps_dict[k] = self.ps_dict[k].tolist()
        # for enc
        self.server_enc = ThreeEncServer()
        # for chaincode
        self.op_c = ChainInterface()
        self.tls_data_path = "/tmp/share/enc.txt"
        self.turn = 1

    def add_ps_dict(self, peer_id):
        """
        get enc data from chain
        performing add operation
        add enc data to chain
        send push to another peer
        """
        if peer_id == 1:
            key_pre = 1000
        elif peer_id == 2:
            key_per = 2000
        else:
            print("wrong peer id")
        print("System server query befor time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        enc_text = self.op_c.ps_chaincode_query("getGradientData", ["send" + str(key_pre + self.turn)], peer_id)
        print("System server query after time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        with open(self.tls_data_path, "rb") as f:
            encrypt_key, signature = f.readlines()
        print("System server deenc befor time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        he_data = self.server_enc.three_layer_deenc(enc_text, encrypt_key.strip(), signature.strip())
        print("System server deenc after time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        self.add_operation(he_data)
        # enc ps_dict
        print("System server enc befor time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        encrypt_text, encrypt_key, signature = self.server_enc.three_layer_enc(self.ps_dict)
        print("System server enc after time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        print("System server invoke befor time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        self.op_c.ps_chaincode_invoke_ps("addGradientData", ["send" + str(key_pre + self.turn) + "b", encrypt_text])
        print("System server invoke after time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        with open(self.tls_data_path, "w") as f:
            f.writelines([bytes.decode(encrypt_key), "\r\n", bytes.decode(signature)])



    def add_operation(self, m_dict):
        for k, v in m_dict.items():
            print("len(v) is: ", str(len(v)))
            if re.search('weight', k):
                for j in range(len(v)):
                    self.ps_dict[k][j] = [self.ps_dict[k][j][i] + v[j][i] for i in range(len(v[0]))]
            else:
                self.ps_dict[k] = [self.ps_dict[k][i] + v[i] for i in range(len(v))]
