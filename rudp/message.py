import threading
import const
from util.byte_util import int_to_byte, byte_to_int


class Message:
    def __init__(self):
        self.__sequence_number = 0
        self.__is_fragmented = False
        self.__is_ack = False
        self.__is_last_fragment = False
        self.__fragmentation_offset = 0
        self.__fragmentation_id = 0
        self.__data = []
        self.timer_thread = threading.Timer(const.DATAGRAM_TIMEOUT_SECONDS, self.__ace_receive_timeout)
        self.__is_acked = False

    def __init__(self, sequence_number, is_fragmented, is_last_fragment, fragmentation_offset, fragmentation_id):
        self.__sequence_number = sequence_number
        self.__is_fragmented = is_fragmented
        self.__is_ack = False
        self.__is_last_fragment = is_last_fragment
        self.__fragmentation_offset = fragmentation_offset
        self.__fragmentation_id = fragmentation_id
        self.__data = []
        self.timer_thread = threading.Timer(const.DATAGRAM_TIMEOUT_SECONDS, self.__ace_receive_timeout)
        self.__is_acked = False

    def append_data(self, byte):
        self.__data.append(byte)

    def get_sequence_number(self):
        return self.__sequence_number

    def is_ack(self):
        return self.__is_ack


    @staticmethod
    def serialize(message):
        bytes_arr = []

        bytes_arr += int_to_byte(message.__sequence_number, 4)
        print(bytes_arr)

        flags_byte = 0

        if message.__is_fragmented:
            flags_byte += pow(2, const.IS_FRAGMENTED_BIT_FLAG)

        if message.__is_ack:
            flags_byte += pow(2, const.IS_ACK_BIT_FLAG)

        if message.__is_last_fragment:
            flags_byte += pow(2, const.IS_LAST_FRAGMENT_BIT_FLAG)

        print(flags_byte)
        bytes_arr.append(flags_byte)
        print(bytes_arr)

        bytes_arr += int_to_byte(message.__fragmentation_offset, 8)
        bytes_arr += int_to_byte(message.__fragmentation_id, 8)
        bytes_arr += message.__data

        return bytes_arr

    @staticmethod
    def deserialize(bytes_arr):
        is_fragmented = ((pow(2, const.IS_FRAGMENTED_BIT_FLAG) & bytes_arr[const.FLAGS_BYTE_INDEX]) == bytes_arr[const.FLAGS_BYTE_INDEX])
        is_ack = ((pow(2, const.IS_ACK_BIT_FLAG) & bytes_arr[const.IS_ACK_BIT_FLAG]) == bytes_arr[const.IS_ACK_BIT_FLAG])
        is_last_fragment = ((pow(2, const.IS_LAST_FRAGMENT_BIT_FLAG) & bytes_arr[const.IS_LAST_FRAGMENT_BIT_FLAG]) == bytes_arr[const.IS_LAST_FRAGMENT_BIT_FLAG])
        message = Message(
            sequence_number=byte_to_int(
                bytes_arr[const.SEQUENCE_NUMBER_START_INDEX: const.SEQUENCE_NUMBER_LENGTH + const.SEQUENCE_NUMBER_START_INDEX]),
            is_fragmented=is_fragmented,
            is_last_fragment=is_last_fragment,
            fragmentation_offset=byte_to_int(bytes_arr[const.FRAGMENT_OFFSET_START_INDEX: const.FRAGMENT_OFFSET_START_INDEX + const.FRAGMENT_OFFSET_LENGTH]),
            fragmentation_id=byte_to_int(bytes_arr[const.FRAGMENTATION_ID_START_INDEX: const.FRAGMENTATION_ID_START_INDEX + const.FRAGMENTATION_ID_LENGTH])
        )

        message.__is_ack = is_ack
        message.__data = bytes_arr[const.PAYLOAD_START_INDEX:]
        return message

    def ack_message(self):
        self.__is_acked = True

    def __ace_receive_timeout(self):
        self.__rsocket_ins.message_sender(self)
