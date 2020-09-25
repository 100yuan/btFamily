# VERSION: 1.00
# AUTHORS: xuziqiang (158856471@qq.com)

# LICENSING INFORMATION
from re import findall, search, S
from urllib.request import Request, urlopen
from novaprinter import prettyPrinter

try:
    # python3
    from html.parser import HTMLParser
    from urllib.parse import quote
except ImportError:
    # python2
    from HTMLParser import HTMLParser
    from urllib import quote


class okzy_online(object):
    url = 'http://www.okzyw.com'
    name = 'OK资源网(在线)'
    supported_categories = {'all': 'all', 'anime': 'anime', 'movies': 'movies', 'tv': 'tv'}

    page_list = []
    pags = 20 #搜索深度要翻页次数
    header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'}
    __help = '''Options: （插件高级用法,在搜索栏输入以下标签.）
     ....... --help      显示帮助.
     ...... -n*          选择频道:
     .......... -n1	     最新电影
     .......... -n2	     连续剧
     .......... -n3	     综艺片
     .......... -n4	     动漫片
     .......... -n5	     动作片
     .......... -n6	     喜剧片
     .......... -n7	     爱情片
     .......... -n8	     科幻片
     .......... -n9	     恐怖片
     .......... -n10     剧情片
     .......... -n11     战争片
     .......... -n12     国产剧
     .......... -n13     香港剧
     .......... -n14     韩国剧
     .......... -n15     欧美剧
     .......... -n16     台湾剧
     .......... -n17     日本剧
     .......... -n18     海外剧
     .......... -n19     纪录片
     .......... -n20     微电影
     .......... -n21     伦理片
     .......... -n22     福利片
     .......... -n23     国产动漫
     .......... -n24     日韩动漫
     .......... -n25     欧美动漫
     .......... -n26     内地综艺
     .......... -n27     港台综艺
     .......... -n28     日韩综艺
     .......... -n29     欧美综艺
     .......... -n31     港台动漫
     .......... -n32     海外动漫
     .......... -n33     解说
     .......... -n34     电影解说
     .......... -n35     泰国剧
     .......... -n36     动漫电影'''

    class MyHtmlParser(HTMLParser):
        """ Sub-class for parsing results """

        def error(self, message):
            pass

        UL, LI, INPUT, HREF = ('ul', 'li', 'input', 'href')

        def __init__(self, url, desc_link):
            HTMLParser.__init__(self)
            self.url = url
            self.desc_link = desc_link
            self.current_item = {}  # dict for found item
            self.page_empty = 22000
            self.inside_ul = False
            self.inside_li = False
            self.findTable = False
            self.findTitle = False

        def handle_starttag(self, tag, attrs):

            params = dict(attrs)
            if params.get('class') == 'suf':
                self.findTable = True

            if self.findTable and tag == self.UL and self.findTitle:
                self.inside_ul = True

            if self.inside_ul and tag == self.LI:
                self.inside_li = True

            if self.inside_ul and self.inside_li and tag == self.INPUT and 'value' in params:
                link = quote(params['value'], safe='/:')
                self.current_item = {'seeds': '-1', 'leech': '-1', 'link': link, 'size': '-1',
                                     'desc_link': self.desc_link, 'engine_url': self.url}

        def handle_data(self, data):
            if self.findTable and data == 'kuyun':
                self.findTitle = True

            if self.inside_li:
                if not self.current_item.get('name'):
                    self.current_item['name'] = data.strip()
                else:
                    self.current_item['name'] += data.strip()

        def handle_endtag(self, tag):
            if tag == self.UL and self.inside_ul and self.findTable and self.findTitle:
                self.findTitle = False
                self.findTable = False
                self.inside_ul = False

            if self.inside_li and tag == self.LI:
                self.inside_li = False
                if len(self.current_item) < 7:
                    return
                prettyPrinter(self.current_item)
                self.current_item = {}


    def __scan_print(self):
        msg = self.__help.split('\n', -1)
        for i in range(0, len(msg)):
            print('-1|{0}   {1}|-1|-1|-1|-1'.format(i, msg[i]))

    def __urlGet(self, url):
        link = Request(url, headers=self.header)
        try:
            response = urlopen(link, timeout=0.6).read()
        except:
            return self.__urlGet(url)
        return response.decode('utf-8')

    def __get_pageUrl(self, url):
        html = self.__urlGet(url)
        msg = findall(
            r'class="xing_vb4".*?href="([^"]+)"\s+target=".*?">(.*?)<.*?"xing_vb5">(.*?)<.*?"xing_vb6">(.*?)<', html, S)
        if not msg:
            return 'END'
        self.page_list += msg

    def __get_preprint(self, msgs):
        url = self.url + msgs[0]
        response = self.__urlGet(url)
        preMsg = search(r'>\s*kuyun\s*<.*?<ul>.*?</ul>', response, S)
        if not preMsg:
            return
        del response
        preMsg = findall(r'value="(https?://.*?)"', preMsg[0], S)
        inmsg = '[更新:{0}][{1}]{2}-'.format(msgs[-1], msgs[2], msgs[1])
        for link in preMsg:
            name = inmsg + search(r'[^/]+$', link)[0]
            link = quote(link, safe='/:')
            dic = {'name': name, 'seeds': '-1', 'leech': '-1', 'size': '-1', 'link': '-1', 'desc_link': link,
                   'engine_url': self.url}
            prettyPrinter(dic)

    def download_torrent(self, info):
        from helpers import download_file
        print(download_file(info))

    def search(self, query, cat='all'):
        """ Performs search """
        # category = self.supported_categories[cat]
        if query == '--help':
            self.__scan_print()
            return
        if query[:2] == '-n':
            for page in range(1, self.pags + 1):
                page_url = "{0}/?m=vod-type-id-{1}-pg-{2}.html".format(self.url, query[2:].strip(), page)
                self.__get_pageUrl(page_url)
        else:
            for page in range(1, self.pags + 1):
                page_url = "{0}/index.php?m=vod-search-pg-{1}-wd-{2}.html".format(self.url, page, query)
                if self.__get_pageUrl(page_url):
                    break
        for msgs in self.page_list:
            self.__get_preprint(msgs)
