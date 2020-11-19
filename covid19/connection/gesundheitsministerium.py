import logging
from datetime import datetime, date, timedelta
from pathlib import Path
import requests
import os
from io import BytesIO
import zipfile
import csv


requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'


class Gesundheitsministerium:

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