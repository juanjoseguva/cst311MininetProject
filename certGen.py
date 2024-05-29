import sys
import subprocess
import os

#Set relative script path
scriptPath=os.path.dirname(__file__)
#Variable to hold ip address and CN of webserver and chatServer, common name is taken from the passedin command line arguements, which are the user input from legacy_network
webHost="10.0.1.11 " + sys.argv[1]
chatHost="10.0.2.11 " + sys.argv[2]

#Open the file /etc/hosts and read it
with open('/etc/hosts', 'rt') as f:
    s = f.read()
    #Check if /etc/hosts contains entries for the chat server and webserver
    if not ((webHost in s) and (chatHost in s)):
        #Add the entries and write out a temp file
        s = s + '\n' + '#Added by legacy_network as part of PA4' + '\n' + webHost + '\n' + chatHost + '\n'
        with open(os.path.join(scriptPath, "hosts.temp"), 'wt') as outf:
            outf.write(s)
        #Replace /etc/hosts with our temp file
        subprocess.run("sudo mv ./hosts.temp /etc/hosts".split())

#Make a directory for the final certs to live in
makeDirCommand ="sudo mkdir certs"
if not os.path.isdir(os.path.join(scriptPath, 'certs')):
                     subprocess.run(makeDirCommand.split())
#Use the openssl library to generate the key and put it in the certs folder
webKeyCommand="sudo openssl genrsa -out ./certs/webpa4.test-key.pem 2048"
subprocess.run(webKeyCommand.split())

#Use the openssl library to generate the signing request passing in the user input common name, and put it in the certs folder
webReqString='/C=US/ST=California/L=Seaside/O=CST311/OU=PA4/CN=' + sys.argv[1]
webReqCommand = "sudo openssl req -new -config /etc/ssl/openssl.cnf -key ./certs/webpa4.test-key.pem -out ./certs/webpa4.test.csr -subj " + webReqString
subprocess.run(webReqCommand.split())

#Use the openssl library to ask the root CA to sign the cert, passing in the root CA password from user input
webCertCommand="sudo openssl x509 -req -days 365 -in ./certs/webpa4.test.csr -CA /etc/ssl/demoCA/cacert.pem -CAkey /etc/ssl/demoCA/private/cakey.pem -passin pass:" + sys.argv[3] + " -CAcreateserial -out ./certs/webpa4.test-cert.pem"
subprocess.run(webCertCommand.split())


#Repeat the above steps, but for the chat server certificate
chatKeyCommand="sudo openssl genrsa -out ./certs/chatpa4.test-key.pem 2048"
subprocess.run(chatKeyCommand.split())

chatReqString='/C=US/ST=California/L=Seaside/O=CST311/OU=PA4/CN=' + sys.argv[2]
chatReqCommand = "sudo openssl req -new -config /etc/ssl/openssl.cnf -key ./certs/chatpa4.test-key.pem -out ./certs/chatpa4.test.csr -subj " + chatReqString
subprocess.run(chatReqCommand.split())

chatCertCommand="sudo openssl x509 -req -days 365 -in ./certs/chatpa4.test.csr -CA /etc/ssl/demoCA/cacert.pem -CAkey /etc/ssl/demoCA/private/cakey.pem -passin pass:" + sys.argv[3] + " -CAcreateserial -out ./certs/chatpa4.test-cert.pem"
subprocess.run(chatCertCommand.split())
