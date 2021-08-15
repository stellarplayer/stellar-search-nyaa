import os
import sys
import StellarPlayer
import threading
import time
import random
import requests
from bs4 import BeautifulSoup
from .test import Client

class Plugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self, player:StellarPlayer.IStellarPlayer):
        super().__init__(player)
        self.c = Client()
        self.q = '字幕'
        self.result = []
        self.page = 0

    def get_layout(self, page=0):
        result_layout = [
            [
                {'type': 'label', 'name': 'name'},
                {'type': 'label', 'name': 'size', 'width': 80},
                {'type': 'label', 'name': 'downloads', 'width': 80},
                {'type': 'link', 'name': '播放', 'width': 70, '@click': 'on_play_click'},
            ]
        ]

        pages = []
        if page:
            pages.append({'type': 'label', 'name': f'共 {page} 页：', 'width': 70})
            for i in range(int(page)):
                pages.append({'type': 'link', 'name': f'{i+1}', 'width': 30, '@click': 'on_page_click'})
            pages.append({'type': 'space'})

        controls = [
            {'type': 'space', 'height': 30},
            {
                'group': [
                    {'type': 'space'},
                    {'type': 'edit', 'name': 'search', 'height': 30, 'width': 0.7, 'label': ' ',
                     '@input': 'on_search_input', ':value': 'q'},
                    {'type': 'button', 'name': '搜索', 'height': 30, 'width': 0.1, '@click': 'on_search_click'},
                    {'type': 'space'},
                ],
                'height': 30
            },
            {'type': 'space', 'height': 10},
            {
                'group': [
                    {'type': 'space'},
                    {'type': 'link', 'name': '海贼王', 'width': 75, '@click': 'on_hot_click'},
                    {'type': 'link', 'name': '一拳超人', 'width': 100, '@click': 'on_hot_click'},
                    {'type': 'link', 'name': '银魂', 'width': 50, '@click': 'on_hot_click'},
                    {'type': 'link', 'name': '咒术回战', 'width': 100, '@click': 'on_hot_click'},
                    {'type': 'link', 'name': '进击的巨人', 'width': 120, '@click': 'on_hot_click'},
                    {'type': 'link', 'name': '工作细胞', 'width': 100, '@click': 'on_hot_click'},
                    {'type': 'space'},
                ],
                'height': 30
            },
            {'type': 'space', 'height': 10},
            {
                'type': 'list',
                'name': 'result',
                'itemheight': 27,
                'itemlayout': result_layout,
                'value': self.result,
                'marginSize': 5,
                '@dblclick': 'on_result_dblclick',
                'separator': True
            },
        ]

        if pages:
            controls.append(
                {
                    'group': pages,
                    'height': 30
                }
            )
        print(controls)
        return controls
  
    def show(self):
        controls = self.get_layout()
        result, controls = self.doModal('main', 1000, 600, 'nyaa 搜索', controls)

    def loading(self, show=True):
        if hasattr(self.player,'loadingAnimation'):
            self.player.loadingAnimation('main', stop=not show)

    def search(self, q, p=''):
        self.result = []
        t = threading.Thread(target=self.search_thread, args=(q, p))
        t.start()

    def search_thread(self, q, p):
        self.loading()
        begin = time.time()
        self.result, page = self.c.search(q, p)
        self.updateLayout('main', self.get_layout(page))
        print(f'search use {time.time() - begin}')
        self.loading(False)

    def on_search_click(self, *a, **k):
        self.search(self.q)

    def on_search_input(self, *a, **k):
        pass

    def on_page_click(self, pageId, controlName):
        self.search(self.q, controlName)

    def on_hot_click(self, pageId, controlName):
        self.q = controlName
        self.search(controlName)
        print("on_hot_click end")

    def on_result_dblclick(self, page, control, item):
        url = self.result[item]['url']
        self.player.play(url)

    def on_play_click(self, page, listControl, item, itemControl):
        url = self.result[item]['url']
        self.player.play(url)
    
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    return Plugin(player)

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()

