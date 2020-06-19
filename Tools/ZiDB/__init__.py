import os

class Zi:
    def __init__(self, line, which="general"):
        data = line.split('\t')
        self._char = data[0]
        self._rank = int(data[1])
        self._shape = data[2]
        self._pinyins = []
        self._type = which
        for i in range(3, len(data), 2):
            self._pinyins.append((data[i], int(data[i+1])))

    def pinyins(self):
        result = set()
        for entry in self._pinyins:
            result.add(entry[0])
        return result

    def char(self):
        return self._char

    def weights(self):
        return self._pinyins
    
    def shape(self):
        return self._shape

    def rank(self):
        return self._rank

    def which(self):
        return self._type


_db = {}
_fixed = []

_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(_path, '通常.txt'), mode='r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        char = Zi(line.strip(), 'general')
        _db[char._char] = char

with open(os.path.join(_path, '超级.txt'), mode='r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        char = Zi(line.strip(), 'super')
        _db[char._char] = char

with open(os.path.join(_path, '无理.txt'), mode='r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        char = Zi(line.strip(), 'hidden')
        _db[char._char] = char

with open(os.path.join(_path, '固定.txt'), mode='r', encoding='utf-8') as f:
    for entry in f.readlines():
        data = entry.strip().split('\t')
        _fixed.append((data[0], data[1]))

def get(char):
    if char not in _db:
        return None
    return _db[char]

def all():
    return _db.values()

def fixed():
    return _fixed