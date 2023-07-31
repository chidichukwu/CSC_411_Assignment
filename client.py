import socket

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8080))

    while True:
        request = input("Enter a command ('generate', 'process', or 'exit'): ")
        client_socket.send(request.encode())

        if request == "exit":
            break

        response = client_socket.recv(1024).decode()
        print(response)

    client_socket.close()

if __name__ == "__main__":
    main()
    