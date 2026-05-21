import socket
import json

from cryptography.fernet import Fernet

print("Bienvenido al cliente de chat del grupo (version segura 0_0) \n")
print("========================================================================================\n")
print("""
 sssss  u    u  bbbb   n   n  eeeee  ttttt     sssss  u    u  rrrrr   fffff  eeeee  rrrrr   sssss 
 s      u    u  b   b  nn  n  e        t       s      u    u  r   r   f      e      r   r   s     
 sssss  u    u  bbbb   n n n  eeee     t       sssss  u    u  rrrrr   ffff   eeee   rrrrr   sssss 
     s  u    u  b   b  n  nn  e        t           s  u    u  r  r    f      e      r  r        s 
 sssss   uuuu   bbbb   n   n  eeeee    t       sssss   uuuu   r   r   f      eeeee  r   r   sssss 
""")
print("========================================================================================\n")

HOST = input("Ingrese IP del servidor: ")
PORT = int(input("Ingrese puerto del servidor: "))

KEY = b"FGmdKxAM9JdRLD9ppQONR6VS68Fg5Zw-rNdtelHgG3I="

cipher = Fernet(KEY)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))

    print(f"Connected to {HOST}:{PORT}")

    group_name = input("Ingrese nombre del grupo: ")

    while True:
        text = input("Mensaje ('exit' para salir): ")

        if text.lower() == "exit":
            break

        encrypted_payload = cipher.encrypt(
            text.encode("utf-8")
        ).decode("utf-8")

        message = {
            "group": group_name,
            "payload": encrypted_payload
        }

        serialized_message = json.dumps(message)

        client.sendall(serialized_message.encode("utf-8"))

except Exception as e:
    print("Error:", e)

finally:
    client.close()

    print("Connection closed.")