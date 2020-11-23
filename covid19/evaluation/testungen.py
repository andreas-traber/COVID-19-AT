from pathlib import Path
from covid19.evaluation.evaluator import Evaluator

class Testungen(Evaluator):

    def __init__(self):
        super().__init__()
        self.file_name = Path('AllgemeinDaten.csv')
        self.data_pos = 5
        self.date_pos = -1
        self.date_format = '%Y-%m-%dT%H:%M:%S'
        self.title = 'Testungen'
        self.calculate_difference = super().calculate_difference_incr

