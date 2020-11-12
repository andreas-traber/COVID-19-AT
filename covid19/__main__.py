import csv
import os
from io import BytesIO
from time import strptime

import requests
from argparse import ArgumentParser
from pathlib import Path
import zipfile
from datetime import datetime, date

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
    return parser


class DataHandler:

    def __init__(self, url, path):
        self.url = url
        self.data_root_path = Path(path)

    def download_and_unzip(self):
        spec_path = self.data_root_path / datetime.now().strftime('%Y%m%d%H%M%S')
        if not os.path.exists(spec_path):
            os.mkdir(spec_path)
        r = requests.get(self.url, verify=False, stream=True)
        with zipfile.ZipFile(BytesIO(r.content), 'r') as zip_file_object:
            zip_file_object.extractall(spec_path)
        return spec_path

    def find_last_folder_with_ref_time(self, folder_before, date_before=date.today()):
        folders = os.listdir(self.data_root_path)
        folders.sort(reverse=True)
        reached = False
        # rev_time = date_before +
        for folder in folders:
            if reached:
                path_csv = self.data_root_path / folder / 'Epikurve.csv'
                with open(path_csv) as f:
                    first = True
                    for x in csv.reader(f, delimiter=';'):
                        if first:
                            first = False
                            continue
                        ts = strptime(x[2], '%Y-%m-%dT%H:%M:%S')
            else:
                if folder == folder_before:
                    reached = True
            print(folder)


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
                    continue
                p1[x[0]] = int(x[1])
        return p1

    def calculate_difference(self, path1, path2):
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
    data = DataHandler(args.url, args.path)
    epi = EpikurveHandler()
    last_path = data.download_and_unzip()
    diff = epi.calculate_difference('../data/20201112084844', last_path)
    print(diff)
    print(epi.calc_sum(diff))
    # data.find_last_folder_with_ref_time('../data/20201112110341')


if __name__ == '__main__':
    args = build_argparser().parse_args()
    main(args)
