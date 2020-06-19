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

class ZiDB:
    def __init__(self):
        self.db = {}
        self._fixed = []

        path = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(path, '通常.txt'), mode='r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                char = Zi(line.strip(), 'general')
                self.db[char._char] = char

        with open(os.path.join(path, '超级.txt'), mode='r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                char = Zi(line.strip(), 'super')
                self.db[char._char] = char
    
        with open(os.path.join(path, '无理.txt'), mode='r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                char = Zi(line.strip(), 'hidden')
                self.db[char._char] = char

        with open(os.path.join(path, '固定.txt'), mode='r', encoding='utf-8') as f:
            for entry in f.readlines():
                data = entry.strip().split('\t')
                self._fixed.append((data[0], data[1]))
    
    def get(self, char):
        if char not in self.db:
            return None
        return self.db[char]

    def all(self):
        return self.db.values()

    def fixed(self):
        return self._fixed