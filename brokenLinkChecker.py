#!/usr/bin/env python3

import argparse
import requests
import logging as log
from os.path import exists
from bs4 import BeautifulSoup

COLOR = {
    'default':'\033[0;0m',
    'red':'\033[0;31m',
    'green':'\033[0;32m',
    'yellow':'\033[0;33m',
    'blue':'\033[0;94m'
}

def banner():
    banner = '''\033[0;94m
    ▄▄▄▄    ██▓    ▄████▄ 
    ▓█████▄ ▓██▒   ▒██▀ ▀█ 
    ▒██▒ ▄██▒██░   ▒▓█    ▄
    ▒██░█▀  ▒██░   ▒▓▓▄ ▄██
    ▒░▓█  ▀█▓░██████▒ ▓███▀ 
    ░░▒▓███▀▒░ ▒░▓  ░ ░▒ ▒  
    ░▒░▒   ░ ░ ░ ▒    ░  ▒  
    ░    ░   ░ ░  ░       
    ░ ░          ░  ░ ░     

    (Broken Link Checker)
    \033[0;0m
    '''
    print(banner)

def init_args():
    # Set arguments
    parser = argparse.ArgumentParser(description='Check if your favorite are still alive.')
    parser.add_argument('filename', help='exported favorite file')
    parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        log.basicConfig(format="%(message)s", level=log.INFO)

    return args.filename

def verify_file(fav_file):
    log.info(COLOR['blue'] + f'[*] Checking file {fav_file} exists.' + COLOR['default'])
    if not exists(fav_file):
        print(COLOR['red'] + f'[-] {fav_file} not found.' + COLOR['default'])
        exit(1)
    log.info(COLOR['green'] + f'[+] File {fav_file} exists !' + COLOR['default'])

def extract_links(fav_file):
    log.info(COLOR['blue'] + '[*] Extracting links...' + COLOR['default'])
    links = []
    with open(fav_file,'r') as fav:
        fav_content = fav.read()
        soup = BeautifulSoup(fav_content, 'html.parser')
        for tag in soup.find_all('a'):
            if 'https' in tag['href']:
                links.append(tag['href'])
    log.info(COLOR['green'] + '[+] Links extracted !' + COLOR['default'])
    return links

def check_broken_links(links):
    broken_links = []
    print(COLOR['blue'] + '[*] Checking Broken Links...It might takes a few minutes.' + COLOR['default'])

    for link in links:
        try:
            headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0'}
            r = requests.get(link, headers=headers, timeout=10)

            if r.status_code == 200 or r.status_code == 301 or r.status_code == 403:
                log.info(COLOR['green'] + f'[+] Link {link} -> Good' + COLOR['default'])
            else:
                log.info(COLOR['red'] + f'[-] Link {link} might be broken. ({r.status_code})' + COLOR['default'])
                broken_links.append(link)

        except requests.exceptions.Timeout:
            log.info(COLOR['red'] + f'[-] Link {link} might be broken (Error: Timeout) ' + COLOR['default'])
            broken_links.append(link)
            continue

        except requests.exceptions.TooManyRedirects:
            log.info(COLOR['yellow'] + f'[+] Link {link} -> OK (Warning: TooManyRedirects) ' + COLOR['default'])
            continue

        except requests.exceptions.SSLError:
            log.info(COLOR['yellow'] + f'[+] Link {link} -> OK (Warning: Certificate validation failed)' + COLOR['default'])

        except requests.exceptions.ConnectionError:
            log.info(COLOR['red'] + f'[-] Link {link} might be broken (Error: ConnectionError) ' + COLOR['default'])
            broken_links.append(link)
            continue

        except requests.exceptions.RequestException:
            print('Error not handle')
            continue

    # Display broken links after checking.
    print('\n')
    if broken_links:
        print(COLOR['red'] + '[-] Broken Links found.' + COLOR['default'])
        for broken_link in broken_links:
            print(broken_link)
    else:
        print(COLOR['green'] + '[+] All links are OK.' + COLOR['default'])

    print(COLOR['blue'] +'[*] Broken Link Checker ended.' + COLOR['default'])

if __name__ == '__main__':
    try:
        banner()
        fav_file = init_args()
        verify_file(fav_file)
        links = extract_links(fav_file)
        check_broken_links(links)
    except KeyboardInterrupt:
        print(COLOR['yellow'] + '[*] Broken Link Checker ended by user.' + COLOR['default'])
        exit(0)