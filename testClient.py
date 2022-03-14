import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
LOCAL_IP = socket.gethostbyname(socket.gethostname())

s.connect((LOCAL_IP, 9999))

while True:
    try:
        #TODO: work i progress....
        rx = s.recv(1, 0x40) # 0x40 = MSG_DONTWAIT a.k.a. O_NONBLOCK
        print(rx.decode('utf8'))
    except:
        pass