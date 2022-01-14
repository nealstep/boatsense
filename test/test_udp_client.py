#!/usr/bin/env python3

from json import loads
from socket import AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from socket import socket

client = socket(AF_INET, SOCK_DGRAM)
client.sendto("T", ('192.168.15.148', 22002))

client = socket(AF_INET, SOCK_DGRAM)
client.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
client.bind(("", 22001))
while True:
    data, addr = client.recvfrom(1024)
    values = loads(data.decode("utf-8"))
    print("msg ({}): {}".format(addr, values))
    if 'gps' in values:
        print(values['gps']['lat'])
