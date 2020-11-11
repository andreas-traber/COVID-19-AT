import csv
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
    r = requests.get(url, verify=False, stream=True)
    with zipfile.ZipFile(BytesIO(r.content), 'r') as zip_file_object:
        zip_file_object.extractall(spec_path)


def calculate_difference(path1, path2):
    p1 = {}
    p2 = {}
    diff = {}
    with open(Path(path1) / 'Epikurve.csv') as f:
        first = True
        for x in csv.reader(f, delimiter=';'):
            if first:
                first = False
                continue
            p1[x[0]] = int(x[1])

    with open(Path(path2) / 'Epikurve.csv') as f:
        first = True
        for x in csv.reader(f, delimiter=';'):
            if first:
                first = False
                continue
            p2[x[0]] = int(x[1])

    for key in p2.keys():
        try:
            diff[key] = p2[key] - p1[key]
        except KeyError:
            diff[key] = p2[key]

    return diff


def main(args):
    # download_and_unzip(args.url, args.path)
    print(calculate_difference('../data/20201111081214', '../data/20201111154155'))


if __name__ == '__main__':
    args = build_argparser().parse_args()
    main(args)
