_db = {}

with open(os.path.join(_path, '通常.txt'), mode='r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        char = Zi(line.strip(), GENERAL)
        _db[char._char] = char

with open(os.path.join(_path, '超级.txt'), mode='r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        char = Zi(line.strip(), SUPER)
        _db[char._char] = char