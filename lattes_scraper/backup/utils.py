import os
import pickle

from . import Backup

BACKUP_FOLDER = '.backup'

def __create_backup_folder(backup_folder:str=None):
    if not backup_folder:
        backup_folder = BACKUP_FOLDER
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    return backup_folder

def available_id(backup_folder:str=None):
    backup_folder = __create_backup_folder(backup_folder)
    ids = [int(f.split('.')[0]) for f in os.listdir(backup_folder)]
    id = max(ids) + 1 if ids else 1
    return id

def save_backup(backup:Backup, backup_folder:str=None):
    backup_folder = __create_backup_folder(backup_folder)
    if not backup.id: backup.id = available_id(backup_folder)
    with open(os.path.join(backup_folder, f'{backup.id}.pickle'), 'wb') as f:
        pickle.dump(backup, f)
    return backup.id

def read_backup(id:int, backup_folder:str=None):
    backup_folder = __create_backup_folder(backup_folder)
    with open(os.path.join(backup_folder, f'{id}.pickle'), 'rb') as f:
        backup = pickle.load(f)
    return backup

def read_backups(backup_folder:str=None):
    backup_folder = __create_backup_folder(backup_folder)
    backups = []
    for file_name in os.listdir(backup_folder):
        id = int(file_name.split('.')[0])
        backup = read_backup(id, backup_folder)
        backups.append(backup)
    return backups