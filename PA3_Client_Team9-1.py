#!env python

"""Chat client for CST311 Programming Assignment 4
This code has been altered for PA4 to implement a TLS connection

"""
__author__ = "Aisclepius"
__credits__ = [
  "Juan Gutierrez",
  "Harut Lementsyan",
  "Kyle Absten"
]

import socket as s
import ssl

# Configure logging
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Set global variables
# TODO: Replace with user input, default to 'localhost'
server_name = 'www.chatpa4.test'
serverAddr = '10.0.2.11'
server_port = 12000

def main():
    #Create TLS context
    context = ssl.create_default_context()
    client_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
    #Wrap client socket in the TLS context
    secureClientSocket = context.wrap_socket(client_socket, server_hostname=server_name)
    secureClientSocket.connect((server_name, server_port))

    message = input(f"Enter a message from the client: ")

    secureClientSocket.send(message.encode())

    response = secureClientSocket.recv(1024).decode()
    response_parts = response.split(", ")
    response_dict = {}

    for part in response_parts:
        if ": " in part:
            client_id, client_message = part.split(": ", 1)
            response_dict[client_id.strip()] = client_message.strip()

    client_x_message = response_dict.get("X", "")
    client_y_message = response_dict.get("Y", "")

    print(f"Server response: X: {client_x_message}, Y: {client_y_message}")

    client_socket.close()

if __name__ == "__main__":
    main()
