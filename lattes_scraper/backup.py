import os
import pickle

BACKUP_PATH = '.backup'

class Backup:
    def __init__(self, results_pages_source=None, id=None):
        if results_pages_source and id:
            self.results_pages_source = results_pages_source
            self.id = id
            self.__save()
        elif id:
            self.id = id
            self.__read()
        elif results_pages_source:
            self.results_pages_source = results_pages_source
            if not os.path.exists(BACKUP_PATH):
                os.makedirs(BACKUP_PATH)
                self.id = 1
            else:
                ids = [int(f.split('.')[0]) for f in os.listdir('.backup')]
                self.id = max(ids) + 1 if ids else 1
            self.__save()

    def __save(self):
        with open(os.path.join(BACKUP_PATH, f'{self.id}.pickle'), 'wb') as f:
            pickle.dump(self, f)

    def __read(self):
        with open(os.path.join(BACKUP_PATH, f'{self.id}.pickle'), 'rb') as f:
            self.results_pages_source = pickle.load(f).results_pages_source