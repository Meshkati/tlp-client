import threading
from const import DATAGRAM_TIMEOUT_SECONDS


class Message:
    def __init__(self, rsocket_ins):
        self.__sequence_number = 0
        self.__is_fragmented = False
        self.__is_ack = False
        self.__is_last_fragment = False
        self.__fragmentation_offset = 0
        self.__fragmentation_id = 0
        self.__data = []
        self.timer_thread = threading.Timer(DATAGRAM_TIMEOUT_SECONDS, self.__ace_receive_timeout)
        self.__rsocket_ins = rsocket_ins

        self.__is_acked = False

    def __init__(self, rsocket_ins, sequence_number, is_fragmented, is_last_fragment, fragmentation_offset, fragmentation_id):
        self.__sequence_number = sequence_number
        self.__is_fragmented = is_fragmented
        self.__is_ack = False
        self.__is_last_fragment = is_last_fragment
        self.__fragmentation_offset = fragmentation_offset
        self.__fragmentation_id = fragmentation_id
        self.__data = []
        self.timer_thread = threading.Timer(DATAGRAM_TIMEOUT_SECONDS, self.__ace_receive_timeout)
        self.__rsocket_ins = rsocket_ins

        self.__is_acked = False

    @staticmethod
    def serialize(message):
        return []

    @staticmethod
    def deserialize(*bytes):
        return []

    def ack_message(self):
        self.__is_acked = True

    def __ace_receive_timeout(self):
        self.__rsocket_ins.message_sender(self)
