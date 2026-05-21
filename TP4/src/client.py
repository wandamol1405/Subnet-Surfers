import socket
import json

print("Bienvenido al cliente de chat del grupo \n")
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

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))
    print(f"Connected to {HOST}:{PORT}")

    group_name = input("Ingrese nombre del grupo: ")

    while True:
        text = input("Mensaje ('exit' para salir): ")

        if text.lower() == "exit":
            break

        message = {
            "group": group_name,
            "payload": text
        }

        serialized_message = json.dumps(message)

        client.sendall(serialized_message.encode("utf-8"))

except ConnectionRefusedError:
    print("Could not connect to the server.")

except Exception as e:
    print("Error:", e)

finally:
    client.close()
    print("Connection closed.")