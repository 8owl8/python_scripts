#!/usr/bin/python3.10
import optparse

import scapy.all as scapy
import argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="IP Жертвы: 192.168.0.1 / Диапазон IP - 192.168.0.0/24")
    options = parser.parse_args()
    return options

# сканирование по протоколу arp - вывод клиентов сети
"""нужно создать пакет и направаить на широковещательный адрес"""
def scan(ip):
    arp_request = scapy.ARP(pdst=ip) # переменная, которая содердит экземпляр объекта АРП пакета для пула IP
    broadcast = scapy.Ether(dst="FF:FF:FF:FF:FF:FF") #отправка пакета на широковещательный адрес
    arp_request_broadcast = broadcast/arp_request #создаем новый пакет, объединяя арп и бродкаст
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0] #вручную отправка пакетов, которая содержит
    # Ether и запись в переменную, которая будет содержать пару из 2 списков (отвеченные пакеры и неотвеченные)
    # timeout нужен для ограничения времени ожидания ответа (1 секунда)
    # verbose= False убирает лишнюю информацию в терминале

    client_list = [] #список для словарей из цикла

    for element in answered_list:
        client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc} #создаем словарь для каждого элемента нашего большого списка,
        # где забираем через параметры psrc и hwsrc IP и MAC соответственно
        client_list.append(client_dict) #доваление словаря в список
    return client_list


def print_result(results_list):
    print("IP\t\t\tAt MAC Address\n----------------------------------------------------------------------------------") #вывод заголовка таблицы
    for client in results_list: #через цикл мы вытягиваем из словоря по ключам значения IP и MAC
        print(client["ip"] + "\t\t" + client["mac"])
        print("----------------------------------------------------------------------------------")


options = get_arguments()
scan_result = scan(options.target)
print_result(scan_result)
