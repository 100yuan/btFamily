#VERSION: 1.00
#AUTHORS: xuziqiang (thelive1@qq.com)

# LICENSING INFORMATION

from requests import get
from re import findall, search, S
from threading import Thread
from helpers import download_file
from novaprinter import prettyPrinter

#############外部函数#############
def __help():
    return '''Options: （插件高级用法,在搜索栏输入以下标签.）
 ....... --help	显示帮助.
 ....... ?      搜索最新电影
 ...... -n*     选择频道:
 .......... -n1	电影下载
 .......... -n2	720高清
 .......... -n3	1080p高清
 .......... -n4	3D电影下载
 .......... -n5	蓝光电影
 .......... -n9	福利影片
 ......... -n10	电视剧'''

def scan_print(msg=__help()):
    msg = msg.split('\n', -1)
    for i in range(0, len(msg)):
        print(f'-1|{i}   {msg[i]}|-1|-1|-1|-1')

#############!外部函数############


class bt_family(object):
    """
    `url`, `name`, `supported_categories` should be static variables of the engine_name class,
     otherwise qbt won't install the plugin.

    `url`: The URL of the search engine.
    `name`: The name of the search engine, spaces and special characters are allowed here.
    `supported_categories`: What categories are supported by the search engine and their corresponding id,
    possible categories are ('all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books').
    """
    url = 'http://www.3btjia.com'
    name = 'BT之家'
    supported_categories = {'all': '0', 'movies': '6', 'tv': '4'}

    def __init__(self):
        self.url = 'http://www.3btjia.com'
        self.header =  {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'}

    def __get_url(self, url):
        try: response = get(url, headers=self.header, timeout=0.5).text
        except: return self.__get_url(url)
        return response


    def select(self, what):
        if what == '--help':
            scan_print()
            return 'end'
        elif what[:2] == '-n':
            return '/forum-index-fid-' + what[2:].strip()
        else:
            return '/search-index-fid-0-orderby-timedesc-daterage-0-keyword-' + what


    def url_msg(self, what):
        lis = []
        path = self.select(what)
        if path == 'end':
            return 'end'
        for currPage in range(1, 41):
            url = self.url + path + f'-page-{currPage}.htm'
            url_list = self.__get_url(url)
            url_list = findall(r'<a target="[^"]+" href="([^"]+)" class="[^"]+">(.*?)</a>', url_list)
            if url_list == []:
                return lis
            for i in url_list:
                if 'BT下载' in i[1]:
                    lis.append(i)
        return lis

    def get_dic_lis(self, desc_link):
        url = desc_link[0]
        response = self.__get_url(url)
        msgs = findall(r'<td colspan="6">.*?<a href="([^"]+)".*?/>([^>]+)</a>.*?<td> *(\d+) *次</td>\s*<td class="grey">(.*?)</td>', response, S)
        for i in msgs:
            link, lench, name = i[0], i[2], f'[更新:{i[-1]}]{i[1]}'
            try: size = search(r'\d+\.?\d* ?(?:G|M|K)(?=B?]?)', desc_link[1])[0] + 'B'
            except: size = '-1'
            link = link.replace('dialog', 'download').replace('-ajax-1', '')
            dic = {'name': name, 'seeds': '-1', 'leech': lench, 'size': size, 'link': link, 'desc_link': url, 'engine_url': self.url}
            prettyPrinter(dic)

    def __thread(self, url_lis):
        tables = []
        for i in url_lis:
            table = Thread(target=self.get_dic_lis, args=[i])
            tables.append(table)
            table.start()
        for table in tables:
            table.join()

    def download_torrent(self, info):
        print(download_file(info))

    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat='all'):
        url_lis = self.url_msg(what)
        if url_lis != 'end':
            self.__thread(url_lis)

'''''
if __name__ == '__main__':
    c = bt_family()
    c.search('-n9')
'''
