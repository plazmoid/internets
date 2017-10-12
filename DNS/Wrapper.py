#coding:utf-8
from Packet import DNSPacket
import socket as s
import base64 as b64
import time

def cr_dns(data):
    packet = DNSPacket(('ns1.mamka.tvoja', 'A'))
    data = b64.b64encode(data).replace(b'/', b'.').replace(b'+', b'-').decode('cp1251')
    eq = data.find('=')
    data = data[:eq] + str(len(data)-eq)
    print(data)
    packet.addField('Answers', data, 'A', '166.20.3.47')
    #packet.addField('Answers', 'gle.co', 'A', '16.2.3.3')
    packet.serializedata()
    with s.socket(s.AF_INET, s.SOCK_DGRAM, s.IPPROTO_UDP) as serv:
        serv.connect(('8.8.8.8', 53))
        serv.send(packet.getRawData())


def main():
    with s.socket(s.AF_INET, s.SOCK_RAW) as serv:
        serv.bind(('', 83))
        #conn, addr = serv.accept()
        recvd = b'.'
        while recvd != b'':
            recvd = serv.recv(2048)
            print(recvd)
            cr_dns(recvd)
            time.sleep(1)
            

if __name__ == '__main__':
    main()