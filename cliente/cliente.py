import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bus_address = ('soabus', 5000)
sock.connect(bus_address)

try:
    while True:
        if (input('Send Hello world to servi ? y/n: ') != 'y'):
            break
        message = b'00016serviHello world'
        sock.sendall(message)

        print("Waiting for transaction")
        amount_received = 0
        amount_expected = int(sock.recv(5))

        while amount_received < amount_expected:
            data = sock.recv(amount_expected - amount_received)
            amount_received += len(data)

        print("Checking servi answer ...")
        print('received {!r}'.format(data))
finally:
    sock.close()