import socket
import datetime
import sys
import threading  # 导入模块，这两模块都是python自带的
from peer_server.cl_peer import Peer

class ControlPeer:
    def __init__(self, j, port):
        super().__init__()
        # 创建基于IPv4和TCP协议的Scoket
        self.j = j
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.s.bind(('127.0.0.1', port))
        self.s.listen(5)  # 调用listen 开始监听
        print('waiting for connection')
        self.message = ""
        self.sock = ""
        self.mPeer = Peer(j, 1000 * (j + 1))
        self.cp_client = ControlPeerClient(int(sys.argv[3]))#peer-A 8811, peer-B 8812
        if j == 0:
            self.id = "A"
        elif j == 1:
            self.id = "B"

    def sendThread(self, sock):
        while True:
            #if self.message == "PULL_OK" or self.message == "PUSH_OK":        
            try:
                sock.send(self.message.encode('utf-8'))
            except OSError as err:
                print("user os error: {0}".format(err))
                break
            self.message = ""
            
    def receiveThread(self,sock):
        while True:
            data = sock.recv(1024)  # 接受数据
            print("receive data is : ", data.decode('utf-8'))
            if len(data) == 0:
                print("connection lost")
                self.sock.close()
                break
            if data.decode('utf-8') == "PULL":
                print("System peer PULL time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
                # send message to run epoch
                self.mPeer.peer_run_epoch()
                self.cp_client.send_and_close(self.id + "PULL_OK")#################todo rebind!
            elif data.decode('utf-8') == "PUSH":
                # send message to decode chaindata
                print("System peer PUSH time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
                if self.j == 0:
                    self.mPeer.load_cl_dict(2000)
                elif self.j == 1:
                    self.mPeer.load_cl_dict(1000)
                print("System load_cl_dict finished time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
                self.cp_client.send_and_close(self.id + "PUSH_OK")
            else:
                print("wrong message")

    def send_message(self, msg):
        self.message = msg

    def run(self):
        while True:
            print("start to listening at ", self.port)
            self.sock, addr = self.s.accept()  # 等待并返回一个服务端的连接
            t_r = threading.Thread(target=self.receiveThread, args=(self.sock,))  # 创建新的线程来处理TCP连接
            t_s = threading.Thread(target=self.sendThread, args=(self.sock,))
            t_r.start()  # 开始运行
            t_s.start()
            
class ControlPeerClient:
    def __init__(self, port):
        super().__init__()
        self.port = port

    def send_and_close(self, message):
        tcp_socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket_client.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        #tcp_socket_client.bind(("127.0.0.1", self.port))
        tcp_socket_client.connect(("127.0.0.1",8800))
        tcp_socket_client.send(message.encode('utf-8'))
        tcp_socket_client.close()



if __name__ == '__main__':
    c = ControlPeer(int(sys.argv[1]), int(sys.argv[2]))
    print("System chaincode init time  befor is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
    if int(sys.argv[1]) == 0:
        c.mPeer.chaincode_init()
    print("System chaincode init time  after is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
    accept_t = threading.Thread(target = c.run)
    accept_t.start()
    print("start to send START")
    print("System start time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
    if int(sys.argv[1]) == 0:
        print("Peer A 0 ready to send START")
        c.cp_client.send_and_close("START")
