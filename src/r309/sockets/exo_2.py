import socket


def serveur():
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 25587))
            sock.listen(1)
            print("Serveur démarre, en attente d'une connexion...")
            client_sock, addr = sock.accept()
            print(f"Connexion établie avec {addr}")
            while True:
                message = input("Serveur > ")
                if message == "arret":
                    client_sock.send("arret".encode())
                    break
                if message == "bye":
                    client_sock.send("bye".encode())
                    break
                client_sock.send(message.encode())
                reponse = client_sock.recv(1024).decode()
                print(f"Client > {reponse}")
            client_sock.close()
            if message == "arret":
                break


def client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("127.0.0.1", 25587))
        print("Connexion établie avec le serveur")
        while True:
            message = input("Client > ")
            sock.send(message.encode())
            reponse = sock.recv(1024).decode()
            print(f"Serveur > {reponse}")

            if message in ("bye", "arret"):
                break


if __name__ == "__main__":
    choice = input("Serveur ou client ? (s/c): ").lower()
    if choice == "s":
        serveur()
    elif choice == "c":
        client()
