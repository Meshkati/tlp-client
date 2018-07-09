
# This class is responsible for constructing a reliable socket
# to the host over a udp socket. Message fragmentation is also implemented here


class ReliableSocket:
    def __init__(self, server_address, server_port):
        self.__server_address = server_address
        self.__server_port = server_port
