#!/usr/bin/env python3

from json import loads
from socket import AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from socket import socket

client1 = socket(AF_INET, SOCK_DGRAM)
client1.sendto("T".encode('utf-8'), ('192.168.15.148', 22002))

client2 = socket(AF_INET, SOCK_DGRAM)
client2.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
client2.bind(("", 22001))
try:
    while True:
        data, addr = client2.recvfrom(1024)
        values = loads(data.decode("utf-8"))
        print("msg ({}): {}".format(addr, values))
        if 'gps' in values:
            print(values['gps']['lat'])
finally:
    client1.sendto("F".encode('utf-8'), ('192.168.15.148', 22002))

