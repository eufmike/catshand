import os, sys
import requests
import re
import argparse
from lxml import html, etree
from fake_useragent import UserAgent
import urllib
from catshand.webtool import UrlShortenTinyurl, podcastlistgen, urlparser

def linkparser():
    ep_idx = 1
    podcastlist = podcastlistgen(ep_idx)
    platforms = ['Apple', 'Google', 'Spotify', 'KKbox']

    podcastlist = urlparser(podcastlist, ep_idx, platforms)

    print('Export:')
    for platform in platforms:
        shorurl_tmp = podcastlist[platform]['short url']
        print(f'{platform.capitalize()}: {shorurl_tmp}')

def main():
    description = 'linkparser collects the most recent podcast links.'
    parser = argparse.ArgumentParser(description=description)
    args = parser.parse_args()
    linkparser()
    return

if __name__ == "__main__":
    main()
