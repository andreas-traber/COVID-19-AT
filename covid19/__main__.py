import csv
import os
from io import BytesIO

import logging

import requests
from argparse import ArgumentParser
from pathlib import Path
import zipfile
from datetime import datetime, date, timedelta

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
                        default='08:30')
    parser.add_argument("--download_newest", '-d', required=False, action='store_true',
                        help="Time of day, when data is compared",
                        default=False)
    return parser


class DataHandler:

    def __init__(self, url, path, reference_time):
        self.url = url
        self.data_root_path = Path(path)
        self.reference_time = datetime.strptime(reference_time, "%H:%M")

    def download_and_unzip(self):
        spec_path = self.data_root_path / datetime.now().strftime('%Y%m%d%H%M%S')
        if not os.path.exists(spec_path):
            os.mkdir(spec_path)
        r = requests.get(self.url, verify=False, stream=True)
        with zipfile.ZipFile(BytesIO(r.content), 'r') as zip_file_object:
            zip_file_object.extractall(spec_path)
        logging.info('Downloaded from %s', self.url)
        logging.info('Saved to %s', spec_path)
        return spec_path

    def get_last_path(self):
        folders = os.listdir(self.data_root_path)
        folders.sort(reverse=True)
        spec_path = self.data_root_path / folders[0]
        logging.info('Last download folder was %s', spec_path)
        return spec_path

    def find_last_folder_with_ref_time(self, folder_before, date_before=datetime.today()):  # - timedelta(days=1)):
        folders = os.listdir(self.data_root_path)
        folders.sort(reverse=True)
        reached = False
        ref_time = date_before.replace(hour=self.reference_time.hour, minute=self.reference_time.minute)
        __folder_before = str(folder_before).split('/')[-1]
        for folder in folders:
            if reached:
                path_csv = self.data_root_path / folder / 'Epikurve.csv'
                with open(path_csv) as f:
                    first = True
                    for x in csv.reader(f, delimiter=';'):
                        if first:
                            first = False
                            continue
                        ts = datetime.strptime(x[2], '%Y-%m-%dT%H:%M:%S')
                        break
                    if ts <= ref_time:
                        return folder
            else:
                if folder == __folder_before:
                    reached = True


class EpikurveHandler:

    def __init__(self):
        self.file_name = Path('Epikurve.csv')

    def csv_to_dict(self, path_csv, delimiter=';'):
        p1 = {}
        with open(path_csv) as f:
            first = True
            for x in csv.reader(f, delimiter=delimiter):
                if first:
                    first = False
                    second = True
                    continue
                if second:
                    logging.info('Timestamp of %s is %s', path_csv, x[2])
                    second = False
                p1[x[0]] = int(x[1])
        return p1

    def calculate_difference(self, path1, path2):
        logging.info('Comparing %s from folder %s and %s', self.file_name, path1, path2)
        diff = {}
        p1 = self.csv_to_dict(Path(path1) / self.file_name)
        p2 = self.csv_to_dict(Path(path2) / self.file_name)

        for key in p2.keys():
            try:
                diff[key] = p2[key] - p1[key]
            except KeyError:
                diff[key] = p2[key]

        return diff

    def calc_sum(self, p1):
        sum = 0
        for key in p1.keys():
            sum += p1[key]
        return sum


def main(args):
    logging.basicConfig(format='%(levelname)s: %(message)s', level='INFO')
    data = DataHandler(args.url, args.path, args.reference_time)
    epi = EpikurveHandler()
    if args.download_newest:
        last_path = data.download_and_unzip()
    else:
        last_path = data.get_last_path()
    ref_path = data.find_last_folder_with_ref_time(last_path)
    diff = epi.calculate_difference(data.data_root_path / ref_path, last_path)
    print(diff)
    print(epi.calc_sum(diff))


if __name__ == '__main__':
    args = build_argparser().parse_args()
    main(args)
