import requests
from bs4 import BeautifulSoup
from w3lib import html
from loguru import logger
from magic_assistant.web_page import WebPage
from magic_assistant.utils.utils import clean_text
from playwright.sync_api import sync_playwright


class BingPlugin():
    def __init__(self):
        self._headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                         "Cookie": "_EDGE_V=1; MUID=15E5F3BB4C7F6F7F357BE14F4D196EF2; MUIDB=15E5F3BB4C7F6F7F357BE14F4D196EF2; SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=1EA9A7F73F574CC49D8073D4027FC5EE&dmnchg=1; SRCHUSR=DOB=20230415&T=1686128239000&POEX=W; SRCHHPGUSR=SRCHLANG=zh-Hans&BRW=XW&BRH=S&CW=1846&CH=346&SCW=1846&SCH=2883&DPR=1.0&UTC=480&DM=0&HV=1686128414&WTS=63820852670&PRVCW=1846&PRVCH=968&EXLTT=31; _HPVN=CS=eyJQbiI6eyJDbiI6NDIsIlN0IjoyLCJRcyI6MCwiUHJvZCI6IlAifSwiU2MiOnsiQ24iOjQyLCJTdCI6MCwiUXMiOjAsIlByb2QiOiJIIn0sIlF6Ijp7IkNuIjo0MiwiU3QiOjAsIlFzIjowLCJQcm9kIjoiVCJ9LCJBcCI6dHJ1ZSwiTXV0ZSI6dHJ1ZSwiTGFkIjoiMjAyMy0wNi0wN1QwMDowMDowMFoiLCJJb3RkIjowLCJHd2IiOjAsIkRmdCI6bnVsbCwiTXZzIjowLCJGbHQiOjAsIkltcCI6NjI1fQ==; _UR=QS=0&TQS=0; _RwBf=ilt=1288&ihpd=2&ispd=12&rc=200&rb=0&gb=0&rg=200&pc=200&mtu=0&rbb=0&g=0&cid=&clo=0&v=14&l=2023-06-07T07:00:00.0000000Z&lft=2023-05-27T00:00:00.0000000-07:00&aof=0&o=2&p=&c=&t=0&s=0001-01-01T00:00:00.0000000+00:00&ts=2023-06-07T09:00:13.0737042+00:00&rwred=0&wls=&lka=0&lkt=0&TH=; MicrosoftApplicationsTelemetryDeviceId=e11f7de6-9d9e-446e-9701-550aac173017; USRLOC=HS=1&ELOC=LAT=22.998899459838867|LON=113.11499786376953|N=%E7%A6%85%E5%9F%8E%E5%8C%BA%EF%BC%8C%E5%B9%BF%E4%B8%9C%E7%9C%81|ELT=4|; ABDEF=V=13&ABDV=11&MRNB=1685922148514&MRB=0; ANON=A=2B2F34CE54AFF56D47CDA209FFFFFFFF&E=1c38&W=1; ANIMIA=FRE=1; _tarLang=default=zh-Hans; _TTSS_IN=hist=WyJlbiIsImF1dG8tZGV0ZWN0Il0=; _TTSS_OUT=hist=WyJ6aC1IYW5zIl0=; MMCASM=ID=F628F98DD8CE45499D2F77AE7C3EE660; imgv=lodlg=1; TRBDG=FIMPR=1; NAP=V=1.9&E=1bde&C=DejVBJfg-Iq1aXw5IoVbvegmzYJgXHK-oM9WsiZCzADgD-VOorz9VA&W=1; PPLState=1; KievRPSSecAuth=FAB6BBRaTOJILtFsMkpLVWSG6AN6C/svRwNmAAAEgAAACCx0ElBS+ZP5OATwXEbBDfCADwG9xYaniWLUSO8FuQ/5BGgy/I5CXGkJqMbMF4jFZJDtmjYn5zANL82rA4EpcJ8QlVIuTvQ8zYJg9C6UwyOmT+jjU1pzNUtrL+hFZ9Ikt24YQllv/SSTQgzEVW0Qh40lYDfrPV5T4giyWytQ1p6JGnRoPV734rRC16BjnBtgWZZ5fIuufDPYqawXpZX9/mS8eLjljw2KkttRkhibk337Y/iIXeBVVyiJTneRbh2mGrCgbWwCji8KsMJCeQmkVdfsM1hGTlVNYkiaaRvt7YT3JuctUz3mS8ONCUd5M88p0gRBZY7mLCNkWMJZYz7ntfdxvwcdjbrXiNIw4HE0HsffuKgzdR5rk7/3tVN4wZJ+HNRCco+NyxcSIIUaJqICLy6MZvHNNxrKVAcMWZHcHvE1WEPreGKPBW2XaOcJoxLGnekaKwGANyN1+17Z9tEtspANt0XgcwAUSIlEjvjEbVvdp44pD9T+5zDAK5gBRzrtbN71PF3HVwugNPVixSd66arLnE8serOlUwALFPfmEuZnsdHx4n1AthSo82BDFo7/Kx1BNvUp7d0jerR5yBwb8No2AUahO9wIcCUoaGw6Aj7EQeUUq09U6HSc7cLkSGq+90y4NG5G2Gz2Ltbqf5Vh2fvSaOjlD7fuw46g0O9phCsNx64tK/pM4Y26OzK2WUJQcGOEJBQVlwGmtWMJVh49l1Y9dDrvreh+3M/sXO+Q0rozK9JHzkUWE5ox70EMwWS2+1ZylCwapKExaEUqYwACHaKMPPg5s0ZbqNFuT9CiJeo45ucGS+5yZlOKNZpsSavrrRuENohD6f8zOWTO3bfY5oa/KpxWx0Bx3R+eX6x28M6SlscGng3licV3b5e68I3vJjU7MoZXJ6Ro+IjGCVjjzmd3vF8N6Tv9PW8LF+FkbLAYb2Ga9/6+Sj6UWkDcX38zwQ263MfTURpnEOHhMz5BH4Fva+Ewe+zb224PwMo4ywhyzpw/7TGOrRS8Ye2ge3d5sk6gc/5II2g4Xied8QayXRrfx3ABZN+XlJITP9zzIZu9VbmQ14D3ltgltR6vhSpQtgblLWeZVbMRqgaA4PzDN52qpuceXh3ZlUpFZaHUuHYTAmSnkS2Pwm4dWy+msYD5MCQFzWRVbnRfOLKCopyqATydJbM2ksTLmYdgzsB18xg2IfZ7zYt8blzGhZZDrHrsh1v7cvEw9Xg2zh8HJmncrlOyHsTUz9EQ57MyR4Wk5eUPUMgzGcRO6p1+jhX8VgLd6k5rtevqqL8OgST4G7qhjvToiEEkxZoT8Y3ma5D6+sp8L+NQVZSI9chkuvGj4w7srvzOZOtYSGrAG5S2+gqbovczIs/ms8zeQ2mZdyCUn/bKvcX/cmZYNGQnRov5qYrbXHd6XuQYwXedZkhKN8NHiqhWw+0N1wiJIK6J7TfgdmYJDKYUAAQ0AW9EYgjCJix0xZCuaxO6kCxT; _U=13raa-bSbCnQ_5UvbnIkQXiZ9XIANdFRZZUHf2Zm8CHuWvMnXHliiDu2MBSAFPmSJ_eg4at5B5pJJpAmExg1fFlt4SZzHaLmLEkIZWnEIb5BfbwyCCawPm8QwaXqEYh80hScFJQeF4zj4dzmeedjQMrSiYp-zFKHeUVyzckRjS_XROiaRo2pW6adxMrZoLVZ1Jin9wrx7srjQQQKsryVb2X91mrgUbWTP-FXv1aKoxW0; WLID=VVX4rUycw+6ifNX5xitsqSvQshFdpSSWarxydXt0LslPxE3MmwU8y5DmFEoqxbEYJW+dKx6H/uvYjBGhZHYwkboroLonM+NNNAJSjpFskMk=; SNRHOP=I=&TS=; _EDGE_S=SID=364260C7FB47611F244D73EFFA95608E; WLS=C=2d35cb21f8dc4fac&N=Guanglong; _SS=SID=364260C7FB47611F244D73EFFA95608E&R=200&RB=0&GB=0&RG=200&RP=200; ipv6=hit=1686131845082&t=4; SUID=A; BFPRResults=FirstPageUrls=1B5C0FDC6A1EBA7BA16B13220A957D2E%2CAE389D34B5E262E14A073ED92F6578FB%2C1176262815AA774B2C458143AA02DAC5%2C7C9A3C686960B98982D51C3F6DCD9F58%2C5B66C537EDD673BF9FDCD339C1ABE922%2C2339AF8363467229889B7888BE5FA0A2%2CF73650466D62BB6F609521CB35D9EDCF%2C73549AB94B22734E1CE6D07AEE07CE30%2CBFBAE972A5BD27B516F8A0A899497CE1%2CF825AF2F6E488E11EA72DB50DB366B54&FPIG=E8B5C8B72A794406BA9351BFB4A17F00"}
        self._web_page_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"}

        self.url = "https://cn.bing.com/search?q="

    def parse(self, query: str, result_cnt: int=10):
        website_list = []

        query = query.replace(" ", "+")
        url = self.url + query
        rsp = requests.get(url, headers=self._headers)
        soup = BeautifulSoup(rsp.content.decode(), 'html.parser')
        h2_list = soup.find_all('h2')
        for h2 in h2_list:
            if len(h2.contents) > 0:
                try:
                    web_page = WebPage(url=h2.contents[0].get("href"), name=h2.contents[0].text)
                    web_page.content = self.get_web_content(web_page.url)
                    website_list.append(web_page)
                except Exception as e:
                    logger.error("catch exception:%s" % str(e))

            if len(website_list) >= result_cnt:
                break

        if len(website_list) == 0:
            logger.error("parse failed, queyr:%s, website_list_cnt:%d" % (query, len(website_list)))
        else:
            logger.debug("parse suc, queyr:%s, website_list_cnt:%d" % (query, len(website_list)))
        return website_list

    def get_web_content(self, url) -> str:
        try:
            text = self._try_get_web_content_by_bs(url)
        except Exception as e:
            text = self._try_get_web_content_by_playwright(url)

        logger.debug("_decode_html suc, content_length:%d" % (len(text)))
        return text

    def _decode_html(self, html_content: str) -> str:
        refined_html = html.remove_tags_with_content(html_content, which_ones=('a', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'))
        soup_without_a = BeautifulSoup(refined_html, 'html.parser')

        text = clean_text(soup_without_a.text)
        return text
    def _try_get_web_content_by_bs(self, url) -> str:
        rsp = requests.get(url, headers=self._web_page_headers, timeout=3)
        text = self._decode_html(rsp.content)

        logger.debug("_decode_html suc, content_length:%d" % (len(text)))
        return text

    def _try_get_web_content_by_playwright(self, url) -> str:
        text = ""
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=False)
                content = browser.new_context()
                page = content.new_page()
                page.goto(url)
                page.wait_for_url(url)
                text = self._decode_html(page.content())
                content.close()
                browser.close()
        except Exception as e:
            logger.error("catch exception:%s" % str(e))

        return text

if __name__ == "__main__":
    bing_adapter = BingPlugin()
    bing_adapter.get_web_content('https://weibo.com/3274122890/Nb0GAiqXs')
    # from playwright.sync_api import Playwright, sync_playwright

    # # 创建浏览器
    # def run(playwright: Playwright) -> None:
    #     # 创建浏览器
    #     browser = playwright.chromium.launch(headless=False)
    #
    #     # 使用 selenium 如果要打开多个网页，需要创建多个浏览器，但是 playwright 中只需要创建多个上下文即可
    #     # 例如：content1 = browser.new_context()、content2 = browser.new_context() 分别去访问网页做处理
    #     content = browser.new_context()
    #
    #     # 每个 content 就是一个会话窗口，可以创建自己的页面，也就是浏览器上的 tab 栏，在每个会话窗口中，可以创建多个页面，也就是多个 tab 栏
    #     # 例如：page1 = content.new_page()、page2 = content.new_page() 封面去访问页面
    #     page = content.new_page()
    #
    #     # 页面打开指定网址
    #     page.goto('https://weibo.com/3274122890/Nb0GAiqXs')
    #
    #
    #     # 延迟关闭（为啥需要延迟一下，这里是用于测试，因为代码执行完马上就回关闭，运行太快了，还以为崩溃了
    #     # 暂时没找到配置不需要进行自动关闭，但是肯定跟 selenium 一样有这个配置）
    #     # sleep(10) # 之前使用使用 sleep 的方式进行等待，传入的是单位是秒
    #     # 但是在 playwright 中有自带的延迟等待，单位是毫秒
    #     page.wait_for_timeout(10000)
    #
    #     # 使用完成关闭上下文（也就是会话窗口）
    #     content.close()
    #
    #     # 关闭浏览器
    #     browser.close()


    # 调用
    # with sync_playwright() as playwright:
    #     browser = playwright.chromium.launch(headless=False)
    #
    #     # 使用 selenium 如果要打开多个网页，需要创建多个浏览器，但是 playwright 中只需要创建多个上下文即可
    #     # 例如：content1 = browser.new_context()、content2 = browser.new_context() 分别去访问网页做处理
    #     content = browser.new_context()
    #
    #     # 每个 content 就是一个会话窗口，可以创建自己的页面，也就是浏览器上的 tab 栏，在每个会话窗口中，可以创建多个页面，也就是多个 tab 栏
    #     # 例如：page1 = content.new_page()、page2 = content.new_page() 封面去访问页面
    #     page = content.new_page()
    #
    #     # 页面打开指定网址
    #     page.goto('https://weibo.com/3274122890/Nb0GAiqXs')
    #
    #
    #     # 延迟关闭（为啥需要延迟一下，这里是用于测试，因为代码执行完马上就回关闭，运行太快了，还以为崩溃了
    #     # 暂时没找到配置不需要进行自动关闭，但是肯定跟 selenium 一样有这个配置）
    #     # sleep(10) # 之前使用使用 sleep 的方式进行等待，传入的是单位是秒
    #     # 但是在 playwright 中有自带的延迟等待，单位是毫秒
    #     page.wait_for_timeout(10000)
    #
    #     # 使用完成关闭上下文（也就是会话窗口）
    #     content.close()
    #
    #     # 关闭浏览器
    #     browser.close()
