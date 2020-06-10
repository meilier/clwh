tls_data_path = "/tmp/share/enc.txt"
control_file_path = "/tmp/share/control.cfg"


with open(control_file_path,"w") as f:
    a = "b'mV8HyvAm/+qBSXhJpZrwk7DiPEVLhlPpzLlM3yYi11U+P4kW3L9/FsW6sXiofcb84tepGjnFFHYeeGO1nKuq9MCKhhZdzbj8uM9QeThjoAiYuZG40pAgUQQ443G6gLKclIP2ErEXvy7GSz5y8hVM+F3uRZYZszLo5RXYLD8f8mM='"
    b = "b'DDZdJobiZkwV3kbpxN2yjpQvl2SVySxQ9bMVLl6HJqUdFjlBUUhp8H0LuuasUrVksRQ9Iu+NS69r8mW83pl+Tuz6Tp4GTRldLAxqL6VWNsILAZlNVziEhXspGxzCVpOjnLcl2fn9CZvOJ/dn/wk6f+gi43S+LH1lqvINvptEG9I='"
    f.writelines([a,"\r\n", b])

with open(control_file_path,"r") as f:
    a , b = f.readlines()
    print(a.strip())
    print(b.strip())


