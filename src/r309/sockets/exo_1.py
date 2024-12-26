"""Socket simple

Reprendre les codes du cours et les implémenter.
"""

import multiprocessing
import socket
import time


def server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(("127.0.0.1", 25587))
            server.listen(1)
            sock, _ = server.accept()

            while True:
                request = sock.recv(1024).decode()
                print(request)

                if request == "bye":
                    print("Server say goodbye!")
    except:
        print("Server say goodbye! (Forced)")


if __name__ == "__main__":
    server_process = multiprocessing.Process(target=server)
    server_process.start()

    time.sleep(1)

    with socket.socket() as client:
        client.connect(("127.0.0.1", 25587))
        client.send("Hello world!".encode())
        time.sleep(1)
        client.send("bye".encode())
        time.sleep(1)

    server_process.kill()
