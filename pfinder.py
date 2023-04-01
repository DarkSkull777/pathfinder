# -*- coding: utf-8 -*-
#!/usr/bin/python3

'''
Author: Dimas XSkull7
github.com/darkskull777
'''

from colorama import Fore
import argparse
import pathlib
import concurrent.futures
import time
import requests
import re
from urllib.parse import urlparse
import urllib3
urllib3.disable_warnings()

# -----------------------------------------------------

print(Fore.RED + '''
 ██▓███   ▄▄▄     ▄▄▄█████▓ ██░ ██      █████▒██▓ ███▄    █ ▓█████▄ ▓█████  ██▀███  
▓██░  ██▒▒████▄   ▓  ██▒ ▓▒▓██░ ██▒   ▓██   ▒▓██▒ ██ ▀█   █ ▒██▀ ██▌▓█   ▀ ▓██ ▒ ██▒
▓██░ ██▓▒▒██  ▀█▄ ▒ ▓██░ ▒░▒██▀▀██░   ▒████ ░▒██▒▓██  ▀█ ██▒░██   █▌▒███   ▓██ ░▄█ ▒
▒██▄█▓▒ ▒░██▄▄▄▄██░ ▓██▓ ░ ░▓█ ░██    ░▓█▒  ░░██░▓██▒  ▐▌██▒░▓█▄   ▌▒▓█  ▄ ▒██▀▀█▄  
▒██▒ ░  ░ ▓█   ▓██▒ ▒██▒ ░ ░▓█▒░██▓   ░▒█░   ░██░▒██░   ▓██░░▒████▓ ░▒████▒░██▓ ▒██▒
▒▓▒░ ░  ░ ▒▒   ▓▒█░ ▒ ░░    ▒ ░░▒░▒    ▒ ░   ░▓  ░ ▒░   ▒ ▒  ▒▒▓  ▒ ░░ ▒░ ░░ ▒▓ ░▒▓░     
░▒ ░       ▒   ▒▒ ░   ░     ▒ ░▒░ ░    ░      ▒ ░░ ░░   ░ ▒░ ░ ▒  ▒  ░ ░  ░  ░▒ ░ ▒░   
░░         ░   ▒    ░       ░  ░░ ░    ░ ░    ▒ ░   ░   ░ ░  ░ ░  ░    ░     ░░   ░        by ''' + Fore.GREEN + 'XSkull7' + '''
               ░  ░         ░  ░  ░           ░           ░    ░       ░  ░   ░     
                                                             ░                     
\n''')

print(Fore.YELLOW + "        ################### - PATH ADMIN FINDER - ####################")
print(Fore.YELLOW + "        #                   -  By: DarkSkull7  -                     #")
print(Fore.YELLOW + "        #    Command bantuan: python3 pfinder.py --help              #")
print(Fore.YELLOW + "        #    Contoh: python3 pfinder.py -u namaweb.com --robots      #")
print(Fore.YELLOW + "        ##############################################################\n\n")

# -----------------------------------------------------

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

def read_wordlist():
    wordlist = args.w
    if isinstance(wordlist, list):
        wordlist = args.w[0]
    try:
        with open(wordlist) as w:
            lines = w.readlines()
            return lines
    except IOError:
        print(Fore.RED + 'Kesalahan saat membaca file wordlist!')

def all_wordlist():
    wordlist = read_wordlist()
    return list(chunks(wordlist, 10))

def unique_wordlist():
    wordlist = read_wordlist()
    lines = [re.sub(r'\/.{1,}|\.[a-z]*|\/$', r'', l.strip().lower()) for l in wordlist]
    unique_lines = sorted(set(lines))
    return list(chunks(unique_lines, 10))

def scan_robots():
    print(Fore.YELLOW + 'Melakukan scanning path pada robots.txt ...')
    try:
        response = requests.get(domain + 'robots.txt', timeout=3, verify=False)
        data = response.text
        response.close()
        if(data):
            for line in data.split('\n'):
                if line.startswith("Disallow:"):
                    path = re.search(r'\s\/.*$', line)
                    if(path is not None):
                        full_url = domain + path.group(0).strip().replace('/', '')
                        try:
                            r = requests.get(full_url, timeout=4, verify=False)
                            if(r.status_code == 200):
                                print(Fore.GREEN + '[FOUND] >>> ' + full_url)
                            r.close()
                        except requests.exceptions.ConnectionError:
                            continue
        print(Fore.YELLOW + 'Pencarian pada robots.txt telah selesai...!')
    except requests.exceptions.ConnectionError:
        print(Fore.RED + "Kesalahan saat membaca robots.txt atau mungkin tidak ada di server....")

def request_subdomains(subdomains):
    parse = urlparse(domain)
    for subdomain in subdomains:
        try:
            if parse.hostname.startswith('www.'):
                hostname = parse.hostname.replace('www.', '')
            else:
                hostname = parse.hostname 
            full_url =  parse.scheme + '://' + subdomain + '.' + hostname
            r = requests.get(full_url, timeout=5)
            if(r.status_code == 200):
                print(Fore.GREEN + '[Found] >>> ' + full_url)
            r.close()
        except requests.exceptions.ConnectionError:
            continue

def scan_subdomains():
    print(Fore.YELLOW + 'Melakukan scanming subdomain...')
    with concurrent.futures.ProcessPoolExecutor() as exec_subdomains:
        results_subdomain = [exec_subdomains.submit(request_subdomains, subdomains) for subdomains in unique_wordlist()]
        for f in concurrent.futures.as_completed(results_subdomain):
            if(f.result() != None):
                print(f.result())
        print(Fore.YELLOW + 'Pencarian subdomain telah selesai...!')  

def request_paths(paths):
    for path in paths:
        try:
            full_url = domain + path.strip()
            r = requests.get(full_url, timeout=5)
            if(r.status_code == 200):
                print(Fore.GREEN + '[Found] >>> ' + full_url)
            r.close()
        except requests.exceptions.ConnectionError:
            continue

def scan_paths():
    print(Fore.YELLOW + 'Melakukan scanning pada directory path...')
    with concurrent.futures.ProcessPoolExecutor() as exec_contexts:
        results_paths = [exec_contexts.submit(request_paths, paths) for paths in all_wordlist()]
        for f in concurrent.futures.as_completed(results_paths):
            if(f.result() != None):
                print(f.result())
        print(Fore.YELLOW + 'Pencarian pada directory path telah selesai...!')

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '-url', nargs=1, help='URL Base <wajib>', required=True, default=None, type=str)
    parser.add_argument('-w', '-wordlist', nargs=1, help='Scan path di dengan paths.txt ', type=str, default='paths.txt')
    parser.add_argument('--robots', action='store_true', help='Scan path pada robots.txt', default=False)
    parser.add_argument('--sub', action='store_true', help='Scan subdomain dengan file wordlist.txt', default=False)
    args = parser.parse_args()

    if not args.u:
        print(Fore.RED + '********************************************')
        print(Fore.RED + '*    URL nya belum di masukin kocak !      *')
        print(Fore.RED + '********************************************')
        print(Fore.YELLOW + 'Pakai: python3 pfinder.py -u <url> --robots --sub\n')
    if not pathlib.Path('paths.txt').exists() and not pathlib.Path(args.w[0]).exists():
        print(Fore.RED + '*************************************************************************')
        print(Fore.RED + '*          File paths.txt tidak di temukan disini !                     *')
        print(Fore.RED + '* Install ulang aja! hapus dulu:  cd $home && rm -rf pathfinder         *')
        print(Fore.RED + '*************************************************************************')
    else:
        start = time.perf_counter()
        domain = ''
        schemes = ['www.', 'http://', 'https://']
        for s in schemes:
            try:
                r = requests.get(s + args.u[0], timeout=8, verify=False)
                if r.status_code == 200:
                    domain = r.url    
                    break
            except:
                continue
        if(domain):
            print(Fore.GREEN + '[URL Cocok] >>> %s ' % domain)
            scan_paths()
            if(args.sub):
                scan_subdomains()
            if(args.robots):
                scan_robots()
        else:
            print(Fore.RED + 'Tidak dapat scan ke host :( >>> ' + args.u[0])
        finish = time.perf_counter()
        print(Fore.BLUE + 'Proses telah selesai dalam %s detik(s :)!' % str(round(finish-start, 2)))
