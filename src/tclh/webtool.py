import urllib
import requests
from lxml import html, etree
from fake_useragent import UserAgent

class UrlShortenTinyurl:
    URL = "http://tinyurl.com/api-create.php"

    def shorten(self, url_long):
        try:
            url = self.URL + "?" \
                + urllib.parse.urlencode({"url": url_long})
            res = requests.get(url)
            # print("STATUS CODE:", res.status_code)
            # print("   LONG URL:", url_long)
            # print("  SHORT URL:", res.text)
            return res.text
        except Exception as e:
            raise
 
def podcastlistgen(ep_idx):  
    podcastlist = {
        'Apple': {
            'url': 'https://podcasts.apple.com/us/podcast/%E4%B8%89%E8%85%B3%E8%B2%93%E5%AF%A6%E9%A9%97%E5%AE%A4-tripod-cats-great-adventure-presented-by-mtba/id1555954868',
            'xpath': f'/html/body/div[4]/main/div[1]/div/section[1]/div/div[2]/div[4]/div/ol/li[{ep_idx}]/div/div/a/@href',
            'prefix': '',
        },
        'Google': {
            'url': 'https://podcasts.google.com/feed/aHR0cHM6Ly9hcGkuc291bmRvbi5mbS92Mi9wb2RjYXN0cy9kZjZmMjUxZC05MTlkLTQyNjItODIxMS01MzNhNGQzODM2ZWYvZmVlZC54bWw',
            'xpath': f'/html/body/c-wiz/div/div[2]/div/div[2]/div[2]/a[1]/@href',
            'prefix': 'https://podcasts.google.com',
        },
        'Spotify': {
            'url': 'https://open.spotify.com/show/7LWPt4lzd15lnk2NZmGcr1',
            'xpath': "/html/head/meta[@property = 'music:song']/@content",
            'prefix': 'https://open.spotify.com',
        },
        'KKbox': {
            'url': 'https://podcast.kkbox.com/sg/channel/DZTWGU-wb9IAfomhp7',
            'xpath': "/html/body/div[1]/div/section[2]/div[1]/a[1]/@href",
            'prefix': 'https://podcast.kkbox.com',
        }
    }
    return podcastlist

def urlparser(podcastlist, ep_idx, platforms = ['Apple', 'Google', 'Spotify', 'KKbox']):
    for platform in platforms:
        if platform == 'Apple': 
            page = requests.get(podcastlist[platform]['url'])
            tree = html.fromstring(page.text)
            #with open('html.html', 'w', encoding="utf-8") as f:
            #    f.write(page.text)
            link = tree.xpath(podcastlist[platform]['xpath'])[ep_idx - 1]
            
        elif platform == 'Google':
            page = requests.get(podcastlist[platform]['url'])
            tree = html.fromstring(page.text)
            #with open('html.html', 'w', encoding="utf-8") as f:
            #    f.write(page.text)
            link = podcastlist[platform]['prefix'] + tree.xpath(podcastlist[platform]['xpath'])[ep_idx - 1][1:]
            
        elif platform == 'Spotify':
            page = requests.get(podcastlist[platform]['url'], headers = {'User-agent': 'Mozilla/5.0'})
            tree = html.fromstring(page.text)
            #with open('html.txt', 'w', encoding="utf-8") as f:
            #    f.write(page.text)
            link = tree.xpath(podcastlist[platform]['xpath'])[ep_idx - 1]

        elif platform == 'KKbox':
            page = requests.get(podcastlist[platform]['url'])
            tree = html.fromstring(page.text)
            #with open('html.html', 'w', encoding="utf-8") as f:
            #    f.write(page.text)
            link = podcastlist[platform]['prefix'] + tree.xpath(podcastlist[platform]['xpath'])[ep_idx - 1]

        obj = UrlShortenTinyurl()
        podcastlist[platform]['short url'] = obj.shorten(link)
    
    return podcastlist