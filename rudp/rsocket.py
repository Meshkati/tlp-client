import socket
import array
from rudp.message import Message
import random
import time
import threading
import const

# This class is responsible for constructing a reliable socket
# to the host over a udp socket. Message fragmentation is also implemented here
from const import DATAGRAM_MESSAGE_SIZE


class ReliableSocket:
    def __init__(self, server_address, server_port):
        self.__server_address = server_address
        self.__server_port = server_port
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.__timer = None
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

    def my_send(self, data):
        print('Enconding ', bytes(data, "utf-8"))
        l = []
        d = bytes(data, "utf-8")
        for e in d:
            l.append(e)
        print('L is ', l)
        self.__fragment(l)

    def __fragment(self, data):

        datagrams = ReliableSocket.partition(data)
        print('t ' ,datagrams)
        if len(datagrams) > 1:
            is_fragmented = True
        else:
            is_fragmented = False

        print('datagrams', datagrams)
        print('is_fragmented', is_fragmented)
        fragmentation_id = random.randint(1, int(time.time()))
        print('fragmentation_id', fragmentation_id)
        for i, datagram in enumerate(datagrams):
            self.__current_message = Message(
                sequence_number=self.__sequence_counter,
                is_fragmented=is_fragmented,
                is_last_fragment=(i == len(datagrams) - 1),
                fragmentation_offset=1000,
                fragmentation_id=fragmentation_id
            )

            self.__current_message.set_data(datagram)

            self.__timer = threading.Timer(const.DATAGRAM_TIMEOUT_SECONDS, self.__ace_receive_timeout)
            self.__timer.start()
            self.__underlying_send(Message.serialize(self.__current_message))
            message = self.__sock.recv(1024)
            rec_mess_obj = Message.deserialize(message)
            while not ((rec_mess_obj.get_sequence_number() == self.__current_message.get_sequence_number()) and (rec_mess_obj.is_ack())):
                self.__timer.cancel()
                self.__timer = threading.Timer(const.DATAGRAM_TIMEOUT_SECONDS, self.__ace_receive_timeout)
                self.__timer.start()
                message = self.__sock.recv(1024)
                rec_mess_obj = Message.deserialize(message)

            self.__timer.cancel()

    def __ace_receive_timeout(self):
        self.__timer = threading.Timer(const.DATAGRAM_TIMEOUT_SECONDS, self.__ace_receive_timeout)
        self.__timer.start()
        self.__underlying_send(Message.serialize(self.__current_message))

    def __underlying_send(self, byte_array):
        self.__sock.sendto(array.array('B', byte_array), (self.__server_address, self.__server_port))

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
