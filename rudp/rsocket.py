import socket
import array
from rudp.message import Message
import random
import time
import threading

# This class is responsible for constructing a reliable socket
# to the host over a udp socket. Message fragmentation is also implemented here
from const import DATAGRAM_MESSAGE_SIZE


class ReliableSocket:
    def __init__(self, server_address, server_port):
        self.__server_address = server_address
        self.__server_port = server_port
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.__timer = threading.Timer(3.0, hello)
        self.__messages = []
        self.__current_message = None

        self.__sequence_counter = 0


    @staticmethod
    def partition(data):
        result = []

        _data = data
        _data_size = len(_data)

        while _data_size > DATAGRAM_MESSAGE_SIZE:
            result.append(_data[:DATAGRAM_MESSAGE_SIZE])
            _data = _data[DATAGRAM_MESSAGE_SIZE:]
            _data_size -= DATAGRAM_MESSAGE_SIZE

        result.append(_data)

        return result


    def __fragment(self, data):
        datagrams = ReliableSocket.partition(data)
        if len(datagrams) > 1:
            is_fragmented = True
        else:
            is_fragmented = False

        fragmentation_id = random.randint(1, int(time.time()))

        for datagram, i in datagrams:
            self.__current_message = Message(
                sequence_number=self.__sequence_counter,
                is_fragmented=is_fragmented,
                is_last_fragment=(i == len(datagrams) - 1),
                fragmentation_offset=1000,
                fragmentation_id=fragmentation_id
            )

    def __retransmit_current_message(self):
        return None

    def send(self, data):
        # self.__sock.sendto(array.array('B', [17, 24, 121, 1, 12, 222, 34, 76, 88, 92]).tostring(),
        #                    (self.__server_address, self.__server_port))
        print((data.encode('utf-8'))[0])
        print(bytes(data, 'utf-8'))

        self.__sock.sendto(data.encode("utf-8"), (self.__server_address, self.__server_port))
        t = self.__sock.recv(1024)
        print('MESSAGE : ' + t.decode("utf-8"))
