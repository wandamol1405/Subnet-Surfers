import socket
import threading
import json

from cryptography.fernet import Fernet

HOST = "0.0.0.0"
PORT = 5000
BUFFER_SIZE = 1024

KEY = b"FGmdKxAM9JdRLD9ppQONR6VS68Fg5Zw-rNdtelHgG3I="

cipher = Fernet(KEY)


def handle_client(client_socket, client_address):
    ip_address = client_address[0]

    print(f"Hello {ip_address} welcome to the server!", flush=True)

    try:
        while True:
            data = client_socket.recv(BUFFER_SIZE)

            if not data:
                break

            try:
                message = json.loads(data.decode("utf-8"))

                if (
                    isinstance(message, dict)
                    and "group" in message
                    and "payload" in message
                    and isinstance(message["group"], str)
                    and isinstance(message["payload"], str)
                ):

                    encrypted_payload = message["payload"]

                    print(
                        f"[ENCRYPTED] {message['group']}: {encrypted_payload}",
                        flush=True
                    )

                    decrypted_payload = cipher.decrypt(
                        encrypted_payload.encode("utf-8")
                    ).decode("utf-8")

                    print(
                        f"[DECRYPTED] {message['group']}: {decrypted_payload}",
                        flush=True
                    )

                else:
                    print(
                        f"{ip_address} wants to send an ill formatted message.",
                        flush=True
                    )

            except Exception as e:
                print(f"Error decoding message: {e}", flush=True)

    except ConnectionResetError:
        pass

    finally:
        print(f"Bye {ip_address}!", flush=True)

        client_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))

    server_socket.listen()

    print(f"Server listening on {HOST}:{PORT}", flush=True)

    try:
        while True:
            client_socket, client_address = server_socket.accept()

            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )

            client_thread.start()

    except KeyboardInterrupt:
        print("\nServer stopped.", flush=True)

    finally:
        server_socket.close()


if __name__ == "__main__":
    main()