import os
from io import BytesIO

import requests
from argparse import ArgumentParser
from pathlib import Path
import zipfile
from datetime import datetime

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'


def build_argparser():
    parser = ArgumentParser()
    parser.add_argument("--url", "-u", required=False, type=str,
                        help="URL zip file with data",
                        default='https://info.gesundheitsministerium.at/data/data.zip')
    parser.add_argument("--path", "-p", required=False, type=str,
                        help="Path where data is saved",
                        default='../data')
    parser.add_argument("--reference_time", "-t", required=False, type=str,
                        help="Time of day, when data is compared",
                        default='08:00')
    return parser


def download_and_unzip(url, path):
    spec_path = Path(path) / datetime.now().strftime('%Y%m%d%H%M%S')
    if not os.path.exists(spec_path):
        os.mkdir(spec_path)
    filename = url.split('/')[-1]
    r = requests.get(url, verify=False, stream=True)
    with zipfile.ZipFile(BytesIO(r.content), 'r') as zip_file_object:
        zip_file_object.extractall(spec_path)


def main(args):
    download_and_unzip(args.url, args.path)


if __name__ == '__main__':
    args = build_argparser().parse_args()
    main(args)
