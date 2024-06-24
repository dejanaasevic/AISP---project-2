import os
import pickle

def save_trie(trie, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(trie, file)

def load_trie(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return None
    with open(file_path, 'rb') as file:
        try:
            return pickle.load(file)
        except EOFError:
            return None

def save_graph(graph, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(graph, file)

def load_graph(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return None
    with open(file_path, 'rb') as file:
        try:
            return pickle.load(file)
        except EOFError:
            return None