import socket


while True:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 4025))
    message = b"Hello!"
    client.send(message)
    client.recv(64)
    client.close

