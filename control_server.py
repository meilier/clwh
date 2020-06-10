import socket
import datetime
import threading  # 导入模块，这两模块都是python自带的
from peer_server.cl_server import Server

class ControlServer:
    def __init__(self):
        super().__init__()
        # 创建基于IPv4和TCP协议的Scoket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        # 监听端口 IP 填写本机IP 如果不知道本机IP地址 可以在 cmd 输入 ipconfig/all查看
        self.s.bind(('127.0.0.1', 8800))
        self.s.listen(5)  # 调用listen 开始监听
        print('waiting for connection')
        self.message = ""
        self.sock = ""
        self.mServer = Server()

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
            if data.decode('utf-8') == "APULL_OK":
                # send message to decode chaindata
                print("System APULL_OK time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
                self.mServer.add_ps_dict(1)
                cServer = ControlServerClient(8802)
                print("System server APUSH time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
                cServer.send_and_close("PUSH")
            elif data.decode('utf-8') == "APUSH_OK":
                print("System APUSH_OK time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
                # send another peer PUSH message
                cServer = ControlServerClient(8802)
                print("System server APULL time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
                cServer.send_and_close("PULL")
            elif data.decode('utf-8') == "BPULL_OK":
                print("System BPULL_OK time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
                # send message to decode chaindata
                self.mServer.add_ps_dict(2)
                cServer = ControlServerClient(8801)
                print("System server BPUSH time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
                cServer.send_and_close("PUSH")
            elif data.decode('utf-8') == "BPUSH_OK":
                print("System BPUSH_OK time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
                # send another peer PUSH message
                cServer = ControlServerClient(8801)
                print("System server BPULL time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
                cServer.send_and_close("PULL")
            elif data.decode('utf-8') == "START":
                print("System server receive START time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
                cs_client = ControlServerClient(8801)
                print("System server START PULL time is :", datetime.datetime.now().strftime("%H:%M:%S.%f"))
                cs_client.send_and_close("PULL")
            else:
                print("wrong message")

    def send_message(self, msg):
        self.message = msg

    def run(self):
        while True:
            print("ps server waiting for connection")
            self.sock, addr = self.s.accept()  # 等待并返回一个客服端的连接
            t_r = threading.Thread(target=self.receiveThread, args=(self.sock,))  # 创建新的线程来处理TCP连接
            t_s = threading.Thread(target=self.sendThread, args=(self.sock,))
            t_r.start()  # 开始运行
            t_s.start()
            
class ControlServerClient:
    def __init__(self, port):
        super().__init__()
        self.port = port


    def send_and_close(self, message):
        self.tcp_socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket_client.connect(("127.0.0.1", self.port))
        self.tcp_socket_client.send(message.encode('utf-8'))
        self.tcp_socket_client.close()

if __name__ == '__main__':
    c = ControlServer()
    accept_t = threading.Thread(target = c.run)
    accept_t.start()
    
