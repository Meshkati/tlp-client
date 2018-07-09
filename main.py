from rsocket import ReliableSocket


def main():
    print('Hello world')
    socket_reliable = ReliableSocket('127.0.0.1', 8080)
    socket_reliable.send('اaTHis')


if __name__ == '__main__':
    main()
