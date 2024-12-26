import socket
import threading


def handle_client(client_socket, clients):
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                continue
            print(f"Received: {message.decode()}")
            if message.decode() != "bye":
                broadcast(message, client_socket, clients)
            else:
                client_socket.close()
                clients.remove(client_socket)
                break

            if message.decode() == "arret":
                print("Breaking...")
                raise InterruptedError()
        except InterruptedError:
            raise
        except:
            clients.remove(client_socket)
            client_socket.close()
            break


def broadcast(message, current_socket, clients):
    for client in clients:
        try:
            client.send(message)
        except:
            client.close()
            clients.remove(client)


def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 25587))
    server_socket.listen(5)
    print("Server started, waiting for connections...")

    clients = []

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            clients.append(client_socket)
            client_thread = threading.Thread(
                target=handle_client, args=(client_socket, clients)
            )
            client_thread.start()
    except InterruptedError:
        print("Server stopped")
    finally:
        server_socket.close()


def client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 25587))

    def receive_messages():
        while True:
            try:
                message = client_socket.recv(1024)
                if message:
                    print(f"< {message.decode()}")

                if message.decode() == "bye":
                    print("Breaking...")
                    break
            except:
                print("Disconnected from server")
                client_socket.close()
                break

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

    while True:
        message = input("> ")
        if not message:
            continue
        try:
            client_socket.send(message.encode())
        except:
            print("Disconnected from server")
            client_socket.close()
            break


if __name__ == "__main__":
    choice = input("Start server or client? (s/c): ").lower()

    if choice == "s":
        server()
    elif choice == "c":
        client()
