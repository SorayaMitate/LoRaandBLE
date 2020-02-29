import pandas as pd

from const import *

const = Const()        

class Result():
    def __init__(self):
        self.list_per = []
        self.list_snr = []

    def out(self):
        return {'SNR':self.list_snr, 'PER':self.list_per}
