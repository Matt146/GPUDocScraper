#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import hashlib
from urllib.parse import urlparse
import threading
import time
import os
import string
import random

site = "https://01.org/linuxgraphics/documentation/hardware-specification-prms"

def prefix_match(s, taglist):
    words = s.split()
    return [w for t in taglist for w in words if w.startswith(t)]


def get_hardware_spec_urls():
    response = requests.get(site)
    # get all the ul with the li's
    soup = BeautifulSoup(response.text, 'lxml')
    ul = soup.select('li.first.expanded.active-trail.active.menu-mlid-10623')

    # get the links
    soup1 = BeautifulSoup(str(ul), 'lxml')
    links = soup1.select("li ul li a")
    
    # get the url's from the links
    urls = []
    for link in links:
        urls.append("https://01.org" + link.get('href'))

    return urls

def get_pdf_urls(mainpage_url):
    response = requests.get(mainpage_url)
    soup = BeautifulSoup(response.text, 'lxml')
    links = soup.select('td a')

    urls = []
    for link in links:
        urls.append(link.get('href'))

    return urls

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever

def sanitize_path(fpath):
    domain = str(urlparse(fpath).netloc).replace(".", "-")
    path = str(urlparse(fpath).path)
    fpath_correct = domain + path

    return "Data-Dump/" + fpath_correct

def make_dir_if_not_exists(d):
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def download_url_pdfs(urls):
    for url in urls:
        # get the content
        response = requests.get(url)
        content = response.content

        # get the location of where the file should go
        url_prefix_trimmed = remove_prefix(url, "https://01.org/")
        file_path = sanitize_path(url_prefix_trimmed)
        dir_path = os.path.split(file_path)[0]

        # create the directory if it does not exist
        make_dir_if_not_exists(dir_path)

        # open the file and write in that dir
        f = open(file_path, "wb")
        f.write(content)
        f.close()


if __name__ == "__main__":
    hardware_spec_urls = get_hardware_spec_urls()
    for link in hardware_spec_urls:
        if link != None:
            pdf_urls = get_pdf_urls(link)
            print("* " + str(pdf_urls) + "\n")
            print("[+] Downloading PDF's...")
            download_url_pdfs(pdf_urls)