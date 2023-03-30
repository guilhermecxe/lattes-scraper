import os
import pickle

BACKUP_PATH = '.backup'

class Backup:
    def __init__(self, results_pages_source=None, id=None, name=None):
        if results_pages_source and id: # updating a backup
            self.results_pages_source = results_pages_source
            self.id = id
            self.__save()
        elif id: # reading a backup
            self.id = id
            self.__read()
        elif results_pages_source: # creating a backup
            self.name = name
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
            previous_backup = pickle.load(f)
        self.results_pages_source = previous_backup.results_pages_source
        self.name = previous_backup.name if 'name' in dir(previous_backup) else None
        