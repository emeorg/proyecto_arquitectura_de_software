import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bus_address = ('soabus', 5000)
sock.connect(bus_address)

try:
    message = b'00010sinitservi'
    sock.sendall(message)
    sinit = 1

    while True:
        print("Waiting for transaction")
        amount_received = 0
        amount_expected = int(sock.recv(5))

        while amount_received < amount_expected:
            data = sock.recv(amount_expected - amount_received)
            amount_received += len(data)

        print("Processing ...")
        print('received {!r}'.format(data))

        if (sinit == 1):
            sinit = 0
            print('Received sinit answer')
        else:
            print("Send answer")
            message = b'00013serviReceived'
            sock.sendall(message)
finally:
    sock.close()