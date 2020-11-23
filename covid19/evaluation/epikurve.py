from pathlib import Path
from covid19.evaluation.evaluator import Evaluator

class Epikurve(Evaluator):

    def __init__(self):
        super().__init__()
        self.file_name = Path('Epikurve.csv')
        self.title = 'Neuinfizierte'