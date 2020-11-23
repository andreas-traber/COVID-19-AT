

import logging

from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from pprint import pprint

from covid19.connection.gesundheitsministerium import Gesundheitsministerium
from covid19.evaluation.epikurve import Epikurve
from covid19.evaluation.todesfaelle import Todesfaelle
from covid19.evaluation.testungen import Testungen
import csv

def build_argparser():
    parser = ArgumentParser()
    parser.add_argument("--url", "-u", required=False, type=str,
                        help="URL zip file with data",
                        default='https://info.gesundheitsministerium.at/data/data.zip')
    parser.add_argument("--path", "-p", required=False, type=str,
                        help="Path where data is saved",
                        default='data')
    parser.add_argument("--reference_time", "-t", required=False, type=str,
                        help="Time of day, when data is compared",
                        default='08:30')
    parser.add_argument("--download_newest", '-d', required=False, action='store_true',
                        help="Time of day, when data is compared",
                        default=False)
    return parser





def main(args):
    logging.basicConfig(format='%(levelname)s: %(message)s', level='ERROR')
    gesund = Gesundheitsministerium(args.url, args.path, args.reference_time)
    if args.download_newest:
        gesund.download_and_unzip()
    epi = Epikurve()
    epi.set_timestamps()
    epi.accumulate_data()
    epi.show_data()

    tod = Todesfaelle()
    tod.set_timestamps()
    tod.accumulate_data()
    tod.show_data()

    test = Testungen()
    test.set_timestamps()
    test.accumulate_data()
    test.show_data()
    #"""
    """
    ref_path = gesund.find_last_folder_with_ref_time(last_path)
    diff = epi.calculate_difference(gesund.data_root_path / ref_path, last_path)
    print(diff)
    print(epi.calc_sum(diff))
    diff = tod.calculate_difference(gesund.data_root_path / ref_path, last_path)
    print(diff)
    print(tod.calc_sum(diff))
    """

if __name__ == '__main__':
    args = build_argparser().parse_args()
    main(args)
