# class AF:
#     def __init__(self):
#         super().__init__()
#         self.a = "haha"
#         b = self.a
#         print(b)
# a = AF()



a = [1,2,3,4]

def change(li):
    li[2] = li[2] + 1
change(a)
print(a)