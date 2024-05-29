#!/usr/bin/python
"""Legacy Network for CST311 Programming Assignment 4"""
__author__ = "Aisclepius"
__credits__ = [
  "Juan Gutierrez",
  "Harut Lementsyan",
  "Kyle Absten"
]
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
import subprocess
import time
from mininet.term import makeTerm

def pa4Setup():
    # Getting user input for the CN's, giving strong hint of the name they should use
    webCN = input("Enter the CN of the webserver(www.webpa4.test): ")
    chatCN = input("Enter the CN of the chat server(www.chatpa4.test): ")
    caPass = input("Enter the passphrase of your root CA: ")

    # Commands to send to subprocess, call certGen script, as list.
    setupCommands = "sudo python3 ./certGen.py".split()
    # Add the user input to the list, to be passed as command line variables to certGen
    setupCommands.extend([webCN,chatCN,caPass])

    # Call subprocess, passing list of commands in, including user input to be used as command line variables in certGen
    subprocess.run(setupCommands)

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/24')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    #Here we set r5-eth0's ip address
    r5 = net.addHost('r5', cls=Node, ip='10.0.2.1/24')
    # This command is essential to tell linux to act as a router, and be able to forward packets
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')
    #Here we set r4-eth0's ip address
    r4 = net.addHost('r4', cls=Node, ip='192.168.1.2/24')
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')
    #Here we set r3-eth0's ip address
    r3 = net.addHost('r3', cls=Node, ip='10.0.1.1/24')
    r3.cmd('sysctl -w net.ipv4.ip_forward=1')

    info( '*** Add hosts\n')
    #Create the four hosts, assigning their eth0's ip addresses and setting their default next hop router
    h1 = net.addHost('h1', cls=Host, ip='10.0.1.10/24', defaultRoute='via 10.0.1.1')
    h2 = net.addHost('h2', cls=Host, ip='10.0.1.11/24', defaultRoute='via 10.0.1.1')
    h3 = net.addHost('h3', cls=Host, ip='10.0.2.10/24', defaultRoute='via 10.0.2.1')
    h4 = net.addHost('h4', cls=Host, ip='10.0.2.11/24', defaultRoute='via 10.0.2.1')

    info( '*** Add links\n')
    #Set the link's between hosts and swtiches, no ip addresses needed
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s2)
    #Set the links between switches and routers, declaring which adapter to connect to on the router
    net.addLink(s2, r5, intfName2='r5-eth0', params2={'ip' : '10.0.2.1/24'})
    net.addLink(s1, r3, intfName2='r3-eth0', params2={'ip' : '10.0.1.1/24'} )
    #Add the link between the the routers, declaring which adapters to use, and setting the ip address on the new adapters
    net.addLink(r3, r4,
                intfName1='r3-eth1', params1={'ip' : '192.168.1.1/24'},
                intfName2='r4-eth0', params2={'ip' : '192.168.1.2/24'})
    net.addLink(r4, r5,
                intfName1='r4-eth1', params1={'ip' : '192.168.2.1/24'},
                intfName2='r5-eth1', params2={'ip' : '192.168.2.2/24'})

    
    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s2').start([c0])
    net.get('s1').start([c0])

    info( '*** Post configure switches and hosts\n')
    #Set the default route of router three, specifying the next hop router and which adapter to use
    net['r3'].cmd('ip route add default via 192.168.1.2 dev r3-eth1')
    #Set the static routes for the two subnets that r4 belongs too, specifying the relative next hop router and which adapter to use
    net['r4'].cmd('ip route add 10.0.1.0/24 via 192.168.1.1 dev r4-eth0')
    net['r4'].cmd('ip route add 10.0.2.0/24 via 192.168.2.2 dev r4-eth1')
    #Set the default route of router five, specifying the next hop router and which adapter to use
    net['r5'].cmd('ip route add default via 192.168.2.1 dev r5-eth1')

    #Launch the two server scripts on the appropriate hosts, and open a terminal for each
    term4 = makeTerm(h4, title='Node', term='xterm', cmd='sudo -E python3 PA3_Server_Team9.py; bash')
    term2 = makeTerm(h2, title='Node', term='xterm', cmd='sudo -E python3 tlswebserver.py; bash')
    #Wait to make sure the server's start and are ready to be contacted
    time.sleep(1)
    #Launch the two chat clients on the appropriate hosts, and open a terminal for each
    term1 = makeTerm(h1, title='Node', term='xterm', cmd='sudo -E python3 PA3_Client_Team9.py; bash')
    term3 = makeTerm(h3, title='Node', term='xterm', cmd='sudo -E python3 PA3_Client_Team9.py; bash')

    CLI(net)


    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    pa4Setup()
    myNetwork()
