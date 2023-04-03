import os, sys
import requests
import re
import argparse
from lxml import html, etree
from fake_useragent import UserAgent
import urllib
from catshand.webtool import UrlShortenTinyurl, podcastlistgen, urlparser

def linkparser(args):
    ep_idx = 1
    podcastlist = podcastlistgen(ep_idx)
    platforms = ['Apple', 'Google', 'Spotify', 'KKbox']

    podcastlist = urlparser(podcastlist, ep_idx, platforms)

    print('Export:')
    for platform in platforms:
        shorurl_tmp = podcastlist[platform]['short url']
        print(f'{platform.capitalize()}: {shorurl_tmp}')

def add_subparser(subparsers):
    description = 'linkparser collects the most recent podcast links.'
    subparsers = subparsers.add_parser('linkparser', help=description)
    subparsers.set_defaults(func=linkparser)
    # parser = argparse.ArgumentParser(description=description)
    # args = parser.parse_args()
    return

# if __name__ == "__main__":
#     main()
