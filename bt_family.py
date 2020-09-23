# VERSION: 1.01
# AUTHORS: xuziqiang (158856471@qq.com)

# LICENSING INFORMATION

from urllib.request import Request, urlopen
from re import findall, search, S
from novaprinter import prettyPrinter

try:
    # python3
    from urllib.parse import quote
except ImportError:
    # python2
    from urllib import quote


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

    __header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'}
    __page_list = []

    __help = '''Options: （插件高级用法,在搜索栏输入以下标签.）
     ....... --help	显示帮助.
     ...... -n*     选择频道:
     .......... -n1	最新电影
     .......... -n2	720高清
     .......... -n3	1080p高清
     .......... -n4	3D电影下载
     .......... -n5	蓝光电影
     .......... -n9	福利影片
     ......... -n10	电视剧'''

    def __scan_print(self):
        msg = self.__help.split('\n', -1)
        for i in range(0, len(msg)):
            print(f'-1|{i}   {msg[i]}|-1|-1|-1|-1')

    def __urlGet(self, url):
        link = Request(url, headers=self.__header)
        try:
            response = urlopen(link, timeout=0.6).read()
        except:
            return self.__urlGet(url)
        return response.decode('utf-8')

    def __select(self, what):
        if what == '--help':
            self.__scan_print()
            return 'end'
        elif what[:2] == '-n':
            return '/forum-index-fid-' + what[2:].strip()
        else:
            return '/search-index-fid-0-orderby-timedesc-daterage-0-keyword-' + what

    def __desc_list(self, url):
        bt_list = self.__urlGet(url)
        bt_list = findall(r'<a target="[^"]+" href="([^"]+)" class="[^"]+">(.*?)</a>', bt_list)
        for i in bt_list:
            self.__get_dic_lis(i)

    def __url_msg(self, what):
        path = self.__select(what)
        if path == 'end':
            return
        urls = []
        for currPage in range(1, 41):
            urls.append(self.url + path + f'-page-{currPage}.htm')
        for i in urls:
            self.__desc_list(i)

    def __get_dic_lis(self, desc_link):
        url = desc_link[0]
        response = self.__urlGet(url)
        msgs = findall(
            r'<td colspan="6">.*?<a href="([^"]+)".*?/>([^>]+)</a>.*?<td> *(\d+) *次</td>\s*<td class="grey">(.*?)</td>',
            response, S)
        for i in msgs:
            link, lench, name = i[0], i[2], f'[更新:{i[-1]}]{i[1]}'
            try:
                size = search(r'\d+\.?\d* ?(?:G|M|K)(?=B?]?)', desc_link[1])[0] + 'B'
            except:
                size = '-1'
            link = quote(link.replace('dialog', 'download').replace('-ajax-1', ''), safe='/:')
            dic = {'name': name, 'seeds': '-1', 'leech': lench, 'size': size, 'link': link, 'desc_link': url,
                   'engine_url': self.url}
            prettyPrinter(dic)

    def download_torrent(self, info):
        from helpers import download_file
        print(download_file(info))

    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat='all'):
        self.__url_msg(what)
