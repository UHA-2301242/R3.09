import socket
import threading

HOST = "127.0.0.1"
PORT = 25583


def serveur():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)
        print("Serveur démarre, en attente d'une connexion...")
        client_sock, addr = server.accept()
        print(f"Connexion établie avec {addr}")

        def handle_messages(sock):
            while True:
                try:
                    message = sock.recv(1024).decode()
                    if message == "arret":
                        break
                    if message == "bye":
                        sock.close()
                    print(f"Client > {message}")
                except:
                    break

        thread = threading.Thread(target=handle_messages, args=[client_sock])
        thread.start()

        while True:
            message = input("Serveur > ")
            if message == "arret":
                break
            client_sock.send(message.encode())

        client_sock.close()
        thread.join()


def client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
        client_sock.connect((HOST, PORT))
        print("Connexion établie avec le serveur")

        def receive_messages():
            while True:
                try:
                    message = client_sock.recv(1024).decode()
                    if message == "bye":
                        print("Breaking...")
                        break
                    print(f"Serveur > {message}")
                except:
                    break

        thread = threading.Thread(target=receive_messages)
        thread.start()

        while True:
            message = input("Client > ")
            client_sock.send(message.encode())
            if message == "bye":
                break

        client_sock.close()
        thread.join()


if __name__ == "__main__":
    choice = input("Serveur ou client ? (s/c): ").lower()
    if choice == "s":
        serveur()
    elif choice == "c":
        client()
