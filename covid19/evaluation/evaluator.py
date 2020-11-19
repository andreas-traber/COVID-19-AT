import logging
from pathlib import Path
import csv

class Evaluator:

    def __init__(self):
        self.file_name = None

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