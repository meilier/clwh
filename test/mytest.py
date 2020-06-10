import  threading
import time

flag = True
class Mytest:
    def run(self):
        while flag == True:
            print("shide")
            time.sleep(1)

if __name__ == "__main__":
    m = Mytest()
    t = threading.Thread(target=m.run)
    t.start()
    print("t has started")
    time.sleep(5)
    flag = False