from Packet import DNSPacket
import socket as s
import re
import sys


def beautifulpacket(data):
    for i,v in data:
        if len(v) == 0:
            continue
        print(i)
        if type(v) == list:
            for k in v:
                print('\t', k)
        else:
            print('\t', v)
        print('***')

def dnsing(url, types, addr):
    params = {'Name': url,
              'Class': 'IN'}
    
    for wtype in types:
        params['Type'] = wtype
        packet = DNSPacket()
        packet.addField('Queries', params)
        #print(packet.getParsedData())
        #print(packet.getRawData())
        
        with s.socket(s.AF_INET, s.SOCK_DGRAM) as sock:
            sock.settimeout(3)
            sock.sendto(packet.getRawData(), (addr, 53))
            data, _ = sock.recvfrom(2048)
            print('ANSWER:', data)
            beautifulpacket(DNSPacket(data).getParsedData())

def usage():
    print('Usage: %s URL -t type1 type2 ... [-s dnsserv IP]' % (__file__))
    sys.exit(1)

def main():
    '''Client.py ya.ru -t A NS AAAA -s'''
    try:
        src = sys.argv[1]
        if src.startswith('-s') or src.startswith('-t'):
            raise IndexError
        args = ' '.join(sys.argv)
        types = re.findall(r'-t([^-$]*)', args)[0].strip().split(' ')
    except IndexError:
        usage()
    try:
        servaddr = re.findall(r'-s(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})?', args)[0].strip()
    except IndexError:
        servaddr = '8.8.8.8'
        print('Wrong server address, using default:', servaddr)
    dnsing(src, types, servaddr)
    
main()