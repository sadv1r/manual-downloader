#!/usr/bin/env python

import sys

sys.dont_write_bytecode = True

import argparse
import os
import requests
from pathlib import Path
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import parse_qs
from pdf_converter import convert

from bs4 import BeautifulSoup


def debug(message):
    if args.verbose:
        print(message)


def print_percent_done(index, total, bar_len=50, title='Downloading'):
    if args.verbose or not total:
        return

    percent_done = int(index) / int(total) * 100
    percent_done = round(percent_done, 1)

    done = round(percent_done / (100 / bar_len))
    togo = bar_len - done

    done_str = '█' * int(done)
    togo_str = '░' * int(togo)

    print(f'\t⏳ {title}: [{done_str}{togo_str}] {percent_done}% done', end='\r')

    if round(percent_done) == 100:
        print('\t✅')


def get_page_number(url):
    parsed_url = urlparse(url)
    page_numbers = parse_qs(parsed_url.query).get('p')
    if page_numbers:
        return page_numbers[0]
    return None


def download(page_url, format='pdf', output=os.getcwd()):
    host = urljoin(page_url, '/')
    debug(f'Host: {host}')

    total_pages_checked = False
    first_page_number = None

    while True:
        page_number = get_page_number(page_url)

        if not page_number:
            page_number = 1

        if not first_page_number:
            first_page_number = page_number

        debug(f'Page: {page_url}')

        resp = requests.get(page_url)
        if not resp.ok:
            print(f'Boo! {resp.status_code}')
            print(resp.text)
            break

        soup = BeautifulSoup(resp.text, 'html.parser')

        if not total_pages_checked:
            total_pages_checked = True
            pages_slider_tag = soup.find('div', {'class': 'viewer-toolbar__slider'}).find('div', recursive=False).string
            total_pages_count = pages_slider_tag.split(' ')[-1]
            debug(f'Total pages: {total_pages_count}')

        image_tags = soup.find_all('img', {'class': 'bi x0 y0 w1 h1'})

        if len(image_tags) == 0:
            break

        image_tag = image_tags[0]

        image_path = image_tag.get('src')

        image_url = urljoin(host, image_path)
        debug(f'Image: {image_url}')

        resp = requests.get(image_url)
        if not resp.ok:
            print(f'Boo! {resp.status_code}')
            print(resp.text)
            break

        with open(Path(output) / f'{page_number}.png', 'wb') as f:
            f.write(resp.content)

        # noinspection PyUnboundLocalVariable
        print_percent_done(page_number, total_pages_count)

        next_page_tag = soup.find('a', {
            'class': 'router-link-active router-link-exact-active glide__arrow glide__arrow--right'})

        next_page_path = next_page_tag.get('href')

        next_page_number = get_page_number(next_page_path)
        if not next_page_number:
            break

        page_url = urljoin(host, next_page_path)

    if format == 'pdf':
        convert(output, total_pages_count, first_number=first_page_number, output=Path(output) / 'manual.pdf')


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('url', help='URL to download', type=str, metavar='URL')  # TODO type=Path?
        parser.add_argument('-f', '--format', help='output format', choices=['pdf', 'png'], default='pdf')  # jpg?
        parser.add_argument('-o', '--output', help='output path', type=Path, default=os.getcwd(), metavar='PATH',
                            action='store', dest='output')
        parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true', dest='verbose')
        args = parser.parse_args()

        download(args.url, args.format, args.output)
    except KeyboardInterrupt:
        exit()
