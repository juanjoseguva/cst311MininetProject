#!env python
""" A discussion on multithreading: While this problem could indeed be 
solved by multithreading, our solution revolved around the use of
the 'select' module in the standard Python library, which is used for 
monitoring multiple file descriptors like sockets or other I/O objects
for readibility, writability, or exceptional conditions. We added our 
client sockets to a read list for select, which listened for when data
was available from one of the two sockets.

This script has been modified to enable a TLS connection
"""


"""Chat server for CST311 Programming Assignment 4"""
__author__ = "Aisclepius"
__credits__ = [
  "Juan Gutierrez",
  "Harut Lementsyan",
  "Kyle Absten"
]

import socket as s
import select
import ssl
import os
import time
# Configure logging
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

port = 12000
serverAddr= '10.0.2.11'

#Variable for holding certificate and key paths
scriptPath = os.path.dirname(__file__)
certPath = os.path.join(scriptPath, "certs/chatpa4.test-cert.pem")
keyPath = os.path.join(scriptPath, "certs/chatpa4.test-key.pem")
certfile = '/etc/ssl/demoCA/chatservpa4.test-cert.pem'
keyfile = '/etc/ssl/demoCA/chatservpa4.test-key.pem'

def handle_client(client_socket, client_name):
    # Receive message from the client
    message = client_socket.recv(1024).decode()
    print(f"{client_name}: '{message}'")
    return client_name, message

def main():
    #TLS protocol, context passing in the path's to the cert and key
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certPath, keyPath)
    
    # Create a TCP socket
    server_socket = s.socket(s.AF_INET, s.SOCK_STREAM) #SOCK_STREAM = TCP packets
    server_socket.bind(('', port)) #Assign port num
    server_socket.listen(2) #How many requests can be queued at once

    # Ready messages
    log.info("The server is ready to receive on port " + str(port))
    print("Waiting for connections...")

    # Wait for two client connections, array makes this expandable
    client_sockets = []
    client_names = ['X', 'Y']

    for i in range(2):
        # .accept() means the server will loop here until there is a connection
        client_socket, address = server_socket.accept()
        #Wrap the socket in the TLS context
        secureSocket=context.wrap_socket(client_socket, server_side=True)
        client_name = client_names[i]  # Assign client name based on the connection order
        client_sockets.append((client_name, secureSocket))
        print(f"Client {client_name} connected.")

    message_count = 0
    client_responses = []

    while message_count < 2:  # Continue checking until 2 clients have sent messages
        while True:
            # Use select to check for sockets with data
            read_sockets, _, _ = select.select([client_socket for _, client_socket in client_sockets], [], [])
            if read_sockets:
                break  # Exit socket selection loop once there is a socket with data

        for client_name, client_socket in client_sockets:
            if client_socket in read_sockets:
                response_client_name, response = handle_client(client_socket, client_name)
                client_responses.append(f"{response_client_name}: {response}")
                message_count += 1
                break

    response = ", ".join(client_responses)

    # Send response to both clients
    for _, client_socket in client_sockets:
        client_socket.send(response.encode())

    # Close the connections
    for _, client_socket in client_sockets:
        client_socket.close()
    server_socket.close()

if __name__ == "__main__":
    main()
