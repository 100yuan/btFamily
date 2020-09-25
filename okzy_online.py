# VERSION: 1.02
# AUTHORS: xuziqiang (158856471@qq.com)

# LICENSING INFORMATION
from re import findall, S, sub
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

    pags = 30 ######用户可设置参数，修改搜索深度即主站要翻页次数#######
    request_timeout = 0.6 ######用户可设置参数，访问超时参数这里预设值0.6(秒)，用以避免网站传输停止提高可用度，请求超时后将不断刷新请求操作(相同超时间隔)直至请求达成#######
    page_empty = 7800 ######搜索网页为空时的字节数，用以判断没有后续请求#######
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

        def __init__(self, url, desc_msgs):
            HTMLParser.__init__(self)
            self.url = url
            self.desc_link = url + desc_msgs[0]
            self.swap_name = '[{0}][{1}]{2}-'.format(desc_msgs[-1], desc_msgs[2], desc_msgs[1])
            self.current_item = {}  # dict for found item
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
                self.current_item = {'seeds': '-1', 'leech': '-1', 'link': '-1', 'size': '-1',
                                     'desc_link': link, 'engine_url': self.url}

        def handle_data(self, data):
            if self.findTable and data == 'kuyun':
                self.findTitle = True

            if self.inside_li:
                if not self.current_item.get('name'):
                    self.current_item['name'] = self.swap_name + sub(r'\$?http[^(\u4e00-\u9fa5)\s]+', '', data.strip())
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
            response = urlopen(link, timeout=self.request_timeout).read()
        except:
            return self.__urlGet(url)
        return response.decode('utf-8')

    def form_msg(self, url):
        html = self.__urlGet(url)
        if len(html) < self.page_empty:
            return True
        msg = findall(
            r'class="xing_vb4".*?href="([^"]+)"\s+target=".*?">(.*?)<.*?"xing_vb5">(.*?)<.*?"xing_vb6">(.*?)<', html, S)
        if not msg:
            return 'END'
        for i in msg:
            self.__get_preprint(i)

    def __get_preprint(self, msgs):
        url = self.url + msgs[0]
        response = self.__urlGet(url)
        if len(response) > self.page_empty:
            myhtml = self.MyHtmlParser(self.url, msgs)
            myhtml.feed(response)
            myhtml.close()

    def download_torrent(self, info):
        from helpers import download_file
        print(download_file(info))

    def search(self, query, cat='all'):
        """ Performs search """
        # category = self.supported_categories[cat]
        if query == '--help':
            self.__scan_print()
            return
        page_urls = []
        if query[:2] == '-n':
            for page in range(1, self.pags + 1):
                page_urls.append("{0}/?m=vod-type-id-{1}-pg-{2}.html".format(self.url, query[2:].strip(), page))
        else:
            for page in range(1, self.pags + 1):
                page_urls.append("{0}/index.php?m=vod-search-pg-{1}-wd-{2}.html".format(self.url, page, query))
        for i in page_urls:
            if self.form_msg(i):
                return
