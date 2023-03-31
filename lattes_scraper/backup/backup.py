import os
import pickle

BACKUP_PATH = '.backup'

class Backup:
    def __init__(self, item=None, name=None):
        self.id = None
        self.name = name
        self.item = item

    def __str__(self):
        return f'<Backup: id={self.id}, name={self.name}>'

    def __repr__(self):
        return self.__str__()