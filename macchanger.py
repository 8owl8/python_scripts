import subprocess
import optparse
import re
""" import re Этот модуль предоставляет операции сопоставления регулярных выражений"""
"""
optparse это более удобная, гибкая и мощная библиотека для анализа параметров командной строки.
 
Как он анализирует командную строку: optparse устанавливает атрибуты на основе 
предоставленных пользователем значений командной строки. 
optparse поддерживает как длинные,  так и короткие параметры, позволяет объединять короткие параметры вместе
и позволяет различным образом связывать параметры  с их аргументами. Таким образом, все следующие командные 
строки эквивалентны приведенному выше примеру: 

* dest - это переменная, которая будет содержать в себе значение введеных пользователем аргументов
"""
def get_arguments():
        parser = optparse.OptionParser() #Вы создаете экземпляр OptionParser,  заполните его параметрами и проанализируйте командную строку.
        parser.add_option("-i", "--interface", dest="interface", help="Inteface to change its MAC address")
        parser.add_option("-m", "--mac", dest="new_mac", help="New MAC Address")
        (options, arguments) = parser.parse_args() #запись данных в options и arguments
        if not options.interface:
            parser.error("[-] Введите корректное значение или воспользуйтесь подсказкой, используя --help")
        elif not options.new_mac:
            parser.error("[-] Введите корректное значение или воспользуйтесь подсказкой, используя --help")
        return options

def change_mac(interface, new_mac):
    print("[+] Изменение MAC адреса для интерфейса " + interface)
    #Вызов системных команд для смены мак адреса
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", new_mac])
    subprocess.call(["ifconfig", interface, "up"])

def get_current_mac(interface):
    # try except используется для отлова ошибок
    try:
        ifconfig_result = subprocess.check_output(["ifconfig", interface])
        clear_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", str(ifconfig_result))
        if clear_result:
            return clear_result.group(0)
        else:
            print("[-] Не могу прочитать MAC адрес")
    except:
        exit()


options = get_arguments() # эта переменная содержит в себе аргументы из get_arguments

current_mac = get_current_mac(options.interface)
print("[+] Текущий MAC = " + str(current_mac))

change_mac(options.interface, options.new_mac)
current_mac = get_current_mac(options.interface) #проверка перезаписи мак адреса
if current_mac == options.new_mac:
    print("[+] MAC адрес успешно изменен на " + current_mac)
