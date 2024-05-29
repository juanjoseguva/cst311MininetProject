#!/usr/bin/env python3
"""Tls enabled web server for CST311 Programming Assignment 4"""
__author__ = "Aisclepius"
__credits__ = [
  "Juan Gutierrez",
  "Harut Lementsyan",
  "Kyle Absten"
]
import http.server
import ssl
import os
 
# Variables, including location of server certificate and private key file
server_address = "www.webpa4.test"
server_port = 4443

scriptPath = os.path.dirname(__file__)
certPath = os.path.join(scriptPath, "certs/webpa4.test-cert.pem")
keyPath = os.path.join(scriptPath, "certs/webpa4.test-key.pem")
ssl_key_file = "/etc/ssl/demoCA/webpa4.test-key.pem"
ssl_certificate_file = "/etc/ssl/demoCA/webpa4.test-cert.pem"

#Context is the TLS Server with its certificate file and key file location
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certPath, keyPath)
 
## Don't modify anything below
httpd = http.server.HTTPServer((server_address, server_port), http.server.SimpleHTTPRequestHandler)
httpd.socket = context.wrap_socket(httpd.socket,
               server_side=True)

print("Listening on port", server_port)                                
httpd.serve_forever()
