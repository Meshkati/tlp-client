import socket
import array

# This class is responsible for constructing a reliable socket
# to the host over a udp socket. Message fragmentation is also implemented here


class ReliableSocket:
    def __init__(self, server_address, server_port):
        self.__server_address = server_address
        self.__server_port = server_port
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

    def send(self, data):
        # self.__sock.sendto(array.array('B', [17, 24, 121, 1, 12, 222, 34, 76, 88, 92]).tostring(),
        #                    (self.__server_address, self.__server_port))
        self.__sock.sendto(data.encode("utf-8"), (self.__server_address, self.__server_port))
