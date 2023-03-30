import os
import pickle

BACKUP_PATH = '.backup'

class Backup:
    def __init__(self, mode, item=None, id=None, name=None):
        if mode == 'create':
            self.name = name
            self.item = item
            if not os.path.exists(BACKUP_PATH):
                os.makedirs(BACKUP_PATH)
                self.id = 1
            else:
                ids = [int(f.split('.')[0]) for f in os.listdir(BACKUP_PATH)]
                self.id = max(ids) + 1 if ids else 1
            self.__save()
        elif mode == 'update':
            self.id = id
            self.__read()
            if name: self.name = name
            self.item = item
            self.__save()
        elif mode == 'read':
            self.id = id
            self.__read()

    def __save(self):
        with open(os.path.join(BACKUP_PATH, f'{self.id}.pickle'), 'wb') as f:
            pickle.dump(self, f)

    def __read(self):
        with open(os.path.join(BACKUP_PATH, f'{self.id}.pickle'), 'rb') as f:
            backup = pickle.load(f)
        self.item = backup.item
        self.name = backup.name
        