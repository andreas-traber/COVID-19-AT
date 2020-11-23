from pathlib import Path
from covid19.evaluation.evaluator import Evaluator

class Todesfaelle(Evaluator):

    def __init__(self):
        super().__init__()
        self.file_name = Path('TodesfaelleTimeline.csv')
        self.title = 'Todesfälle'
        self.calculate_difference = super().calculate_difference_incr

