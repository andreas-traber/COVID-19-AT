import logging
from datetime import datetime, timedelta, date
from pathlib import Path
import csv
import os
import pandas as pd


class Evaluator:

    def __init__(self, data_root_path='data'):
        self.file_name = None
        self.title = None
        self.data_root_path = Path(data_root_path)
        self.data = {}  # pd.DataFrame()
        self.timestamp_pos = -1
        self.data_pos = 1
        self.date_pos = 0
        self.date_format = '%d.%m.%Y'

    def set_timestamps(self, overwrite_duplicate_folders=True):
        folders = os.listdir(self.data_root_path)
        for folder in folders:
            path_csv = self.data_root_path / folder / self.file_name
            with open(path_csv) as f:
                first = True
                for x in csv.reader(f, delimiter=';'):
                    if first:
                        first = False
                        continue
                    ts = datetime.strptime(x[self.timestamp_pos], '%Y-%m-%dT%H:%M:%S')
                    if overwrite_duplicate_folders:
                        self.data[ts] = {'folders': [folder]}
                    else:
                        try:
                            self.data[ts]['folders'].append(folder)
                        except KeyError:
                            self.data[ts] = {'folders': [folder]}
                    break

    def get_all_of_day(self, day=datetime.today()):
        day1 = day.replace(hour=0, microsecond=0, second=0)

        day2 = day.replace(hour=23, microsecond=59, second=59)
        s = pd.Series(self.data.keys())
        return s[s.between(day1, day2)]

    def get_first_of_day(self, day=datetime.today()):
        return self.get_all_of_day(day).min()

    def get_last_of_day(self, day=datetime.today()):
        return self.get_all_of_day(day).max()

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
                    logging.info('Timestamp of %s is %s', path_csv, x[self.timestamp_pos])
                    second = False
                p1[datetime.strptime(x[self.date_pos], self.date_format).date()] = int(x[self.data_pos])
        return p1

    def calculate_difference(self, path1, path2):
        """
        Calculate differences for 2 CSVs, where each entry is the accumulated sum for each day
        :param path1: path where the first CSV is found
        :param path2: path where the second CSV is found
        :return:
        """
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

    def calculate_difference_incr(self, path1, path2):
        """
        Calculate difference for 2 CSVs, where each entry is the amount of cases for each day
        :param path1: path where the first CSV is found
        :param path2: path where the second CSV is found
        :return:
        """
        logging.info('Comparing %s from folder %s and %s', self.file_name, path1, path2)
        diff = {}
        p1 = self.csv_to_dict(Path(path1) / self.file_name)
        p2 = self.csv_to_dict(Path(path2) / self.file_name)

        last_key1 = sorted(p1.keys())[-1]
        last_key2 = sorted(p2.keys())[-1]
        diff[last_key1] = p2[last_key2] - p1[last_key1]

        return diff

    def calc_sum(self, p1):
        sum = 0
        for key in p1.keys():
            sum += p1[key]
        return sum

    def accumulate_data(self):
        diff_to = pd.Series(self.data.keys()).max()
        diff_from = self.get_first_of_day(diff_to)
        if diff_to == diff_from:
            diff_from = self.get_first_of_day(datetime.today() - timedelta(days=1))
        while True:
            diff = self.calculate_difference(self.data_root_path / self.data[diff_from]['folders'][0],
                                             self.data_root_path / self.data[diff_to]['folders'][0])
            sum = self.calc_sum(diff)
            self.data[diff_to]['increment'] = {'reference_ts': diff_from, 'value': sum}
            diff_to = diff_from
            diff_from = self.get_first_of_day(diff_to - timedelta(days=1))
            if pd.isnull(diff_from):
                break

    def show_data(self):
        print('''-----------------------------
              %s
              -----------------------------''' % self.title)
        for key in sorted(self.data.keys()):
            try:
                print('Änderung von %s zu %s: %s' % (
                    self.data[key]['increment']['reference_ts'], key, self.data[key]['increment']['value']))
            except KeyError:
                pass
