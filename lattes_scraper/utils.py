import os
import pickle

def print_backups(folder_path):
    for file_name in os.listdir(folder_path):
        with open(os.path.join(folder_path, file_name), 'rb') as f:
            backup = pickle.load(f)
            print(f'{backup.id}: {backup.name}')