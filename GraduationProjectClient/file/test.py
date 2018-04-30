'''
import struct
count = "123"
passwd = "456"

count = count.encode()
print(type(count))
count = struct.pack("10s",count)
#count = count.decode()
count = str(count,"utf-8")
print(type(count))
print(count)
'''

# 不要删除 有用 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!

'''
import struct
block = 15


def struct_str(string):
    length = len(string)
    if length > block - 4:
        return False, None

    length_str = struct.pack('i', length)
    length_str = str(length_str,"utf-8")
    # print(type(length_str))
    new_str = length_str + string
    str_pack = struct.pack(str(block) + 's', new_str.encode())
    return True, str_pack


def get_struct_str(data):
    length = struct.unpack('i', data[0:4])[0]
    print(length)
    str_content = struct.unpack('{length}s'.format(length=length), data[4:4 + length])[0]
    str_content = str(str_content, "utf-8")
    print(str_content)


if __name__ == '__main__':
    state,data = struct_str('非常好')
    get_struct_str(data)

'''
import threading
import time

def hello():

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    global timer
    timer = threading.Timer(2.0, hello)
    timer.start()


if __name__ == "__main__":
    timer = threading.Timer(2.0, hello)
    timer.start()
