#!/usr/bin/env python

import argparse
import os
from pathlib import Path

from PIL import Image


def convert(source, last_number, first_number=1, output=Path(os.getcwd()) / 'manual.pdf', quality=100.0):
    print('Converting images to PDF...')
    images = [
        Image.open(Path(f'{source}') / '{}.png'.format(i))
        for i in range(int(first_number), int(last_number) + 1)
    ]

    print('Saving PDF to {}...'.format(output))
    images[0].save(output, "PDF", resolution=quality, save_all=True, append_images=images[1:])


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('source', help='source path', type=str, metavar='PATH')
        parser.add_argument('-f', '--first', help='first image file number', type=int, default=1, metavar='NUMBER',
                            action='store', dest='first_number')
        parser.add_argument('-l', '--last', help='last image file number', type=int, required=True, metavar='NUMBER',
                            action='store', dest='last_number')
        parser.add_argument('-o', '--output', help='output path', type=Path, default=Path(os.getcwd()) / 'manual.pdf',
                            metavar='PATH', action='store', dest='output')
        parser.add_argument('-q', '--quality', help='result pdf quality', type=float, default=100.0, metavar='QUALITY',
                            action='store', dest='quality')
        args = parser.parse_args()

        convert(args.source, args.output, args.first_number, args.last_number, args.quality)
    except KeyboardInterrupt:
        exit()
