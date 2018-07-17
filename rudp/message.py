class Message:
    def __init__(self):
        self.__sequence_number = 0
        self.__is_fragmented = False
        self.__is_ack = False
        self.__is_last_fragment = False
        self.__fragmentation_offset = 0
        self.__fragmentation_id = 0
        self.__data = []


    @staticmethod
    def serialize(message):
        return []

    @staticmethod
    def deserialize(*bytes):
        return []