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

        fragmentation_id = random.randint(1, int(time.time()))
        fragmentation_offset = 0
        for i, datagram in enumerate(datagrams):
            self.__current_message = Message(
                sequence_number=self.__sequence_counter,
                is_fragmented=is_fragmented,
                is_last_fragment=(i == len(datagrams) - 1),
                fragmentation_offset=fragmentation_offset,
                fragmentation_id=fragmentation_id
            )
            fragmentation_offset = len(datagram)

            self.__current_message.set_data(datagram)

            self.__timer = threading.Timer(const.DATAGRAM_TIMEOUT_SECONDS, self.__ace_receive_timeout)
            self.__timer.start()
            self.__underlying_send(Message.serialize(self.__current_message))
            message = self.__sock.recv(1024)
            rec_mess_obj = Message.deserialize(message)
            print('Sent ', self.__current_message)
            print('Receive', rec_mess_obj)
            while True:
                if rec_mess_obj.is_ack():
                    if not (rec_mess_obj.get_sequence_number() == self.__current_message.get_sequence_number()):
                        self.__timer.cancel()
                        self.__timer = threading.Timer(const.DATAGRAM_TIMEOUT_SECONDS, self.__ace_receive_timeout)
                        self.__timer.start()
                    else:
                        break

                message = self.__sock.recv(const.DATAGRAM_SIZE)
                rec_mess_obj = Message.deserialize(message)

            self.__timer.cancel()

            self.__sequence_counter += 1

    def __ace_receive_timeout(self):
        self.__timer = threading.Timer(const.DATAGRAM_TIMEOUT_SECONDS, self.__ace_receive_timeout)
        self.__timer.start()
        self.__underlying_send(Message.serialize(self.__current_message))

    def __underlying_send(self, byte_array):
        self.__sock.sendto(array.array('B', byte_array), (self.__server_address, self.__server_port))

    def send(self, data):
        # self.__sock.sendto(array.array('B', [17, 24, 121, 1, 12, 222, 34, 76, 88, 92]).tostring(),
        #                    (self.__server_address, self.__server_port))
        print((data.encode('utf-8'))[0])
        print(bytes(data, 'utf-8'))

        self.__sock.sendto(data.encode("utf-8"), (self.__server_address, self.__server_port))
        t = self.__sock.recv(1024)
        print('MESSAGE : ' + t.decode("utf-8"))

    @staticmethod
    def gen_ack(message):
        m = Message(
            sequence_number=0,
            is_fragmented=False,
            is_last_fragment=True,
            fragmentation_offset=0,
            fragmentation_id=0
        )
        m.set_sequence_number(sequenc=message.get_sequence_number())
        m.set_to_ack()
        return m

    def receive(self):
        messages = []
        message_bytes = self.__sock.recv(const.DATAGRAM_SIZE)
        message = Message.deserialize(message_bytes)
        messages.append(message)
        ack = ReliableSocket.gen_ack(message)
        self.__underlying_send(Message.serialize(ack))

        while not message.is_last_fragment():
            message_bytes = self.__sock.recv(const.DATAGRAM_SIZE)
            message = Message.deserialize(message_bytes)
            messages.append(message)
            ack = ReliableSocket.gen_ack(message)
            self.__underlying_send(Message.serialize(ack))

        message_bytes = self.__sock.recv(const.DATAGRAM_SIZE)
        message = Message.deserialize(message_bytes)
        messages.append(message)
        ack = ReliableSocket.gen_ack(message)
        self.__underlying_send(Message.serialize(ack))

        # messages.append(message)
        data = []
        for me in messages:
            data += me.get_data()

        return data
