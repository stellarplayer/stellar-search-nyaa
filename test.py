import os
import sys
import time
import random
import socket
import http.client
from urllib.parse import urlencode, quote_plus, urlparse
import requests
from bs4 import BeautifulSoup

import socket
import requests.packages.urllib3.util.connection as urllib3_cn


def allowed_gai_family():
    return socket.AF_INET

urllib3_cn.allowed_gai_family = allowed_gai_family


class ConnectionError(Exception):
    pass


class CustomAdapter(requests.adapters.HTTPAdapter):
    def get_connection(self, url, proxies=None):
        print(f'{url=}')
        parts = urlparse(url)
        ips = socket.gethostbyname_ex(parts.hostname)[-1]
        

        replaced = parts._replace(netloc=ips[0])
        print(replaced.geturl())

        return super().get_connection(replaced.geturl(), proxies=proxies)


class Client:
    def __init__(self):
        self.url = 'https://nyaa.si/'
        self.proxys = [
            'https://torproxy.cyou/?cdURL=',
            'https://unblockweb.me/?cdURL='
        ]
        self.proxy_index = 0

    def get_url(self, url):
        if self.proxy_index == -1:
            return url
        if self.proxy_index < len(self.proxys):
            return f'{self.proxys[self.proxy_index]}{quote_plus(url)}'
        raise ConnectionError()

    def search(self, q='', p=''):
        params = {'f': '0', 'c': '1_0', 'q': q}
        if p:
            params['p'] = p
        query = urlencode(params)
        url = f'{self.url}?{query}'

        resp = None
        
        while 1:
            try:
                final_url = self.get_url(url)

                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                }
                begin = time.time()                
                resp = requests.get(final_url, headers=headers)
                print(f'{time.time() - begin}')
                break
            except ConnectionError:
                self.proxy_index = -1
                break
            except:
                import traceback
                traceback.print_exc()
                self.proxy_index += 1

        result = []
        page = 0
        if resp:
            soup = BeautifulSoup(resp.text, 'html.parser')
            rows = soup.select('body > div > div.table-responsive > table > tbody > tr')
            for row in rows:
                name_el = row.select('td:nth-child(2) > a')
                size_el = row.select('td:nth-child(4)')
                magnate_el = row.select('td:nth-child(3) > a:nth-child(2)')
                downloaded_el = row.select('td:nth-child(8)')
                if name_el and size_el and magnate_el and downloaded_el:
                    name = name_el[-1].string
                    size = size_el[0].string
                    magnate = magnate_el[0].get('href')
                    downloaded = downloaded_el[0].string
                    result.append({'name': name, 'size': size, 'url': magnate, 'downloads': downloaded})
            page = 0
            pages = soup.select('.pagination > li > a')
            if pages:
                page = int(pages[-2].string)

        return result, page
        

if __name__ == '__main__':
    c = Client()
    result, page = c.search('一拳超人',1)
    print(page)