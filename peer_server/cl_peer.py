import os
import numpy as np
import torch
import datetime
from torchvision.datasets import mnist  # 导入 pytorch 内置的 mnist 数据

from torch import nn
from torch.autograd import Variable
from torch.utils.data import DataLoader
from peer_server.net import classifier
from t_encryption.ThreeLayerEnc import ThreeEncClient
from op_peer.op_chain import ChainInterface
from util.utils import data_path
from util.utils import mnist_base_path

from itertools import chain

import matplotlib.pyplot as plt
from numpy import math
# %matplotlib inline


class Peer:
    def __init__(self, j, peer_key_pre):
        super().__init__()
        self.i = 0
        self.j = j
        self.peer_key_pre = peer_key_pre
        self.train_set = mnist.MNIST(data_path, train=True, download=True)
        self.test_set = mnist.MNIST(data_path, train=False, download=True)
        self.train_set = mnist.MNIST(
            data_path, train=True, transform=self.data_tf, download=True)  # 重新载入数据集，申明定义的数据变换
        self.test_set = mnist.MNIST(
            data_path, train=False, transform=self.data_tf, download=True)
        # split dataset to 10 shares
        self.train_list = torch.utils.data.random_split(
            self.train_set, [6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000])
        print('train_0:', len(self.train_list[0]), 'train_1:', len(
            self.train_list[1]))

        self.val_list = torch.utils.data.random_split(
            self.test_set, [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000])
        print('val_0:', len(self.val_list[0]), 'val_1:', len(self.val_list[1]))
        # global simple PS
        self.ps_dict = torch.load(mnist_base_path)

        self.empty_dict = torch.load(mnist_base_path)
        # for enc
        self.peer_enc = ThreeEncClient()
        # for chaincode
        self.op_c = ChainInterface()
        self.tls_data_path = "/tmp/share/enc.txt"
        # initialize empty_dict to 0
        self.empty_dict['fc.0.weight'] = np.zeros((400, 784), dtype=float).tolist()
        self.empty_dict['fc.0.bias'] = np.zeros((400,), dtype=float).tolist()
        self.empty_dict['fc.2.weight'] = np.zeros((200, 400), dtype=float).tolist()
        self.empty_dict['fc.2.bias'] = np.zeros((200,), dtype=float).tolist()
        self.empty_dict['fc.4.weight'] = np.zeros((100, 200), dtype=float).tolist()
        self.empty_dict['fc.4.bias'] = np.zeros((100,), dtype=float).tolist()
        self.empty_dict['fc.6.weight'] = np.zeros((10, 100), dtype=float).tolist()
        self.empty_dict['fc.6.bias'] = np.zeros((10,), dtype=float).tolist()
        # mynet list
        self.mynet = []
        # netwrok definition
        for i in range(10):
            train_data = DataLoader(
                self.train_list[i], batch_size=64, shuffle=True)
            test_data = DataLoader(
                self.val_list[0], batch_size=128, shuffle=False)
            criterion = nn.CrossEntropyLoss()
            new_net = classifier(train_data, test_data)
            # load model from base pth
            new_net.load_state_dict(torch.load(mnist_base_path))
            new_net.set_criterion(criterion)
            optimizer = torch.optim.SGD(
                new_net.parameters(), 1e-1)  # 使用随机梯度下降，学习率 0.1
            new_net.set_optimizer(optimizer)
            self.mynet.append(new_net)

    def data_tf(self, x):
        x = np.array(x, dtype='float32') / 255
        x = (x - 0.5) / 0.5  # 标准化，这个技巧之后会讲到
        x = x.reshape((-1,))  # 拉平
        x = torch.from_numpy(x)
        return x

    def run_epoch(self, net, epoch, id):
        losses = []
        acces = []
        eval_losses = []
        eval_acces = []
        train_loss = 0
        train_acc = 0
        net.train()
        for im, label in net.train_data:
            im = Variable(im)
            label = Variable(label)
            # 前向传播
            out = net(im)
            loss = net.criterion(out, label)
            # 反向传播
            net.optimizer.zero_grad()
            loss.backward()
            net.optimizer.step()
            # 记录误差
            train_loss += loss.item()
            # 计算分类的准确率
            _, pred = out.max(1)
            num_correct = (pred == label).sum().item()
            acc = num_correct / im.shape[0]
            train_acc += acc

        losses.append(train_loss / len(net.train_data))
        acces.append(train_acc / len(net.train_data))
        # 在测试集上检验效果
        eval_loss = 0
        eval_acc = 0
        net.eval()  # 将模型改为预测模式
        for im, label in net.test_data:
            im = Variable(im)
            label = Variable(label)
            out = net(im)
            loss = net.criterion(out, label)
            # 记录误差
            eval_loss += loss.item()
            # 记录准确率
            _, pred = out.max(1)
            num_correct = (pred == label).sum().item()
            acc = num_correct / im.shape[0]
            eval_acc += acc

        eval_losses.append(eval_loss / len(net.test_data))
        eval_acces.append(eval_acc / len(net.test_data))
        print('epoch: {}, id:{},Train Loss: {:.6f}, Train Acc: {:.6f}, Eval Loss: {:.6f}, Eval Acc: {:.6f}'
              .format(epoch, id, train_loss / len(net.train_data), train_acc / len(net.train_data),
                      eval_loss / len(net.test_data), eval_acc / len(net.test_data)))
        self.i = self.i + 1

    def partial_max_changed(self, old, new, partial):
        first = True
        for k, v in old.items():
            if first == True:
                no = np.array(old[k]).flatten()
                nn = np.array(new[k]).flatten()
                first = False
            else:
                no = np.concatenate((no, np.array(old[k]).flatten()))
                nn = np.concatenate((nn, np.array(new[k]).flatten()))
        diff = abs(nn - no)
        max_index = np.argsort(-diff)
        needed = len(diff) * partial
        for i in range(len(diff)):
            if i < needed:
                if max_index[i] <= 313599:
                    row = math.floor(max_index[i] / 784)
                    column = max_index[i] % 784
                    self.empty_dict['fc.0.weight'][row][column] = (new['fc.0.weight'][row][column] - \
                        old['fc.0.weight'][row][column]).tolist()
                elif max_index[i] >= 313600 and max_index[i] <= 313999:
                    pos = max_index[i] - 313600
                    self.empty_dict['fc.0.bias'][pos] = (new['fc.0.bias'][pos] - \
                        old['fc.0.bias'][pos]).tolist()
                elif max_index[i] >= 314000 and max_index[i] <= 393999:
                    tmp = max_index[i] - 314000
                    row = math.floor(tmp / 400)
                    column = tmp % 400
                    self.empty_dict['fc.2.weight'][row][column] = (new['fc.2.weight'][row][column] - \
                        old['fc.2.weight'][row][column]).tolist()
                elif max_index[i] >= 394000 and max_index[i] <= 394199:
                    pos = max_index[i] - 394000
                    self.empty_dict['fc.2.bias'][pos] = (new['fc.2.bias'][pos] - \
                        old['fc.2.bias'][pos]).tolist()
                elif max_index[i] >= 394200 and max_index[i] <= 414199:
                    tmp = max_index[i] - 394200
                    row = math.floor(tmp / 200)
                    column = tmp % 200
                    self.empty_dict['fc.4.weight'][row][column] = (new['fc.4.weight'][row][column] - \
                        old['fc.4.weight'][row][column]).tolist()
                elif max_index[i] >= 414200 and max_index[i] <= 414299:
                    pos = max_index[i] - 414200
                    self.empty_dict['fc.4.bias'][pos] = (new['fc.4.bias'][pos] - \
                        old['fc.4.bias'][pos]).tolist()
                elif max_index[i] >= 414300 and max_index[i] <= 415299:
                    tmp = max_index[i] - 414300
                    row = math.floor(tmp / 100)
                    column = tmp % 100
                    self.empty_dict['fc.6.weight'][row][column] = (new['fc.6.weight'][row][column] - \
                        old['fc.6.weight'][row][column]).tolist()
                elif max_index[i] >= 415300 and max_index[i] <= 415309:
                    pos = max_index[i] - 415300
                    self.empty_dict['fc.4.bias'][pos] = (new['fc.6.bias'][pos] - \
                        old['fc.6.bias'][pos]).tolist()
            else:
                break
        return self.empty_dict

    def chaincode_init(self):
        self.op_c.ps_chaincode_install()
        args = ['ParameterInitial', '10', '32', '16', '0.01']
        self.op_c.ps_chaincode_instantiate(args)

    def peer_run_epoch(self):
        # download
        tmp_ps_dict = self.ps_dict
        model_dict = self.mynet[self.j].state_dict()
        model_dict.update(tmp_ps_dict)
        self.mynet[self.j].load_state_dict(model_dict)
        print("System befor run epoch is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        self.run_epoch(self.mynet[self.j], self.i, self.j)
        print("System after run epoch is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        # upload
        # find 10% max changed
        current_dict = self.mynet[self.j].state_dict()
        peer_dict = self.partial_max_changed(tmp_ps_dict, current_dict, 0.1)
        # encryption
        print("System befor enc time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        encrypt_text, encrypt_key, signature = self.peer_enc.three_layer_enc(
            peer_dict)
        print("System after enc time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        # put encrypt_text to chain, encrypt_key and signature into file
        print("send key is :", "send" + str(self.peer_key_pre + self.i))
        print("System befor invoke time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        self.op_c.ps_chaincode_invoke(
            "addGradientData", ["send" + str(self.peer_key_pre + self.i), encrypt_text], self.j)
        print("System after invoke time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        with open(self.tls_data_path, "w") as f:
            f.writelines([bytes.decode(encrypt_key), "\r\n", bytes.decode(signature)])

    def peer_tensor_to_dict(self, m_dict):
        for k, v in m_dict.items():
            m_dict[k] = m_dict[k].tolist()
    
    def peer_dict_to_tensor(self, m_dict):
        for k, v in m_dict.items():
            m_dict[k] = torch.Tensor(m_dict[k])

    def load_cl_dict(self, key):
        # get encryted data from chain
        print("System load_cl_dict query time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        encrypt_text = self.op_c.ps_chaincode_query("getGradientData", ["send" + str(key + self.i) + "b"], self.j)
        print("System load_cl_dict after time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        with open(tls_data_path, "r") as f:
            encrypt_key, signature = f.readlines()
        print("System load_cl_dict deenc befor time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        notensor_dict = self.peer_enc.three_layer_deenc(encrypt_text, encrypt_key.strip(), signature.strip())
        print("System load_cl_dict deenc after time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
        self.peer_dict_to_tensor(notensor_dict)
        self.ps_dict = notensor_dict


