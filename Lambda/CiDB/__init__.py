import os
from PinyinConsts import VALID_PY, isWordCommon

_fixed = None
_db = None

class Ci:
    def __init__(self, word, pinyins):
        self._word = word
        self._pinyins = pinyins
        self._common = isWordCommon(word)

    @classmethod
    def fromLine(cls, line):
        obj = cls.__new__(cls)
        super(Ci, obj).__init__()

        data = line.split('\t')
        obj._word = data[0]
        obj._pinyins = []
        obj._common = isWordCommon(obj._word)
        for i in range(1, len(data), 3):
            obj._pinyins.append((tuple(data[i].split('/')), int(data[i+1]), int(data[i+2])))
        
        return obj

    def __hash__(self):
        return hash(self._word)

    def line(self):
        line = '%s' % (self._word)
        for pinyin in self._pinyins:
            line += '\t%s\t%d\t%d' % ("/".join(pinyin[0]), pinyin[1], pinyin[2])
        return line
    
    def pinyins(self):
        return set(tuple(pinyin[0]) for pinyin in self._pinyins)

    def word(self):
        return self._word

    def common(self):
        return self._common

    def weights(self):
        return self._pinyins

    def change_code_length(self, pinyins, length):
        """
        更换词组简码长度
        ----------
        pinyins: set(tuple(str))
            需要修改的拼音
        length: int
            码长
        """
        for i in range(len(self._pinyins)):
            weight = self._pinyins[i]
            if weight[0] in pinyins:
                self._pinyins[i] = (weight[0], length, weight[2])

    def change_code_rank(self, pinyins, rank):
        """
        更换词组简码权值
        ----------
        pinyins: set(tuple(str))
            需要修改的拼音
        rank: int
            权值
        """
        for i in range(len(self._pinyins)):
            weight = self._pinyins[i]
            if weight[0] in pinyins:
                self._pinyins[i] = (weight[0], weight[1], rank)
    
    def get_rank_of(self, pinyins):
        """
        查找词组简码权值
        ----------
        pinyins: set(tuple(str))
            需要查找的拼音
        """
        result = 0
        for weight in self._pinyins:
            result = max(result, weight[2])
        return result


    def add_pinyins(self, pinyins):
        """
        为词组添加拼音
        ----------
        pinyins: list[tuple(py: tuple(str), len: int, rank: int)]
            list[tuple(拼音, 码长, 码序权值)]
        """
        sound = sound_chars(self._word)

        existing = self.pinyins()
        for pinyin in pinyins:
            pyt = tuple(pinyin[0])
            assert len(pyt) == len(sound), '`%s`词拼音`%s`不合法(长度不符)' % (self._word, " ".join(pyt))
            for py in pyt:
                assert py in VALID_PY, '`%s`词拼音`%s`不合法(%s)' % (self._word, " ".join(pyt), py)
        
            if pyt not in existing:
                self._pinyins.append((pyt, pinyin[1], pinyin[2]))

    def remove_pinyins(self, pinyins):
        og_pinyins = self._pinyins
        self._pinyins = []

        for pinyin in og_pinyins:
            if pinyin[0] not in pinyins:
                self._pinyins.append(pinyin)

    def sound_chars(self):
        return sound_chars(self._word)

_path = os.path.dirname(os.path.abspath(__file__))

def _loadDB():
    global _db
    if _db is None:
        _db = {}
    else:
        return
    
    with open(os.path.join(_path, '通常.txt'), mode='r', encoding='utf-8') as f:
        for line in f:
            word = Ci.fromLine(line.strip())
            _db[word._word] = word

# 符号
NUM_CHAR = '零一二三四五六七八九'
SYMBOL_CHAR = set('＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏！？｡。,.!@#$%^&*()[]{}/\\-+=\'\"|;:<>~`')

def sound_chars(words):
    """词组取音字"""

    sanitized = []
    for char in words:
        if char.isdigit():
            sanitized.append(NUM_CHAR[int(char)])
        elif char not in SYMBOL_CHAR:
            sanitized.append(char)

    if len(sanitized) > 4:
        sanitized = sanitized[:3] + [sanitized[-1]]

    return "".join(sanitized)

def get(word) -> Ci:
    _loadDB()
    
    if word not in _db:
        return None
    return _db[word]

def all():
    _loadDB()
    return _db.values()

def add(word, pinyins):
    """
    添加词组到词库
    ----------
    word : str
        需要添加的词组
    pinyins: list[tuple(py: tuple(str), len: int, rank: int)]
        list[tuple(拼音, 码长, 码序权值)]
    """

    _loadDB()
    
    assert len(word) != 1, '`%s`不是词组' % word
    assert word not in _db, '`%s`词已存在' % word
    assert len(pinyins) != 0, '`%s`词没有提供拼音' % word

    sound = sound_chars(word)

    for pinyin in pinyins:
        assert len(pinyin[0]) == len(sound), '`%s`词拼音`%s`不合法(长度不符)' % (word, " ".join(pinyin[0]))
        for py in pinyin[0]:
            assert py in VALID_PY, '`%s`词拼音`%s`不合法(%s)' % (word, " ".join(pinyin[0]), py)

    new_ci = Ci(word, pinyins)
    _db[word] = new_ci
    
    return new_ci

def remove(word, pinyins):
    """
    删除词组拼音，如果空音则彻底删除
    ----------
    word : str
        目标词组
    pinyins: set(tuple(str))
        需要删除的拼音
    """

    _loadDB()
    _db = None

    assert _db is not None, '`%s`词不存在' % word

    _db[word].remove_pinyins(pinyins)

    if len(_db[word].pinyins()) <= 0:
        del _db[word]

def commit():
    _loadDB()

    with open(os.path.join(_path, '通常.txt'), mode='w', encoding='utf-8', newline='\n') as f:
        all_words = sorted(all(), key=lambda x: x._word)
        for ci in all_words:
            f.write(ci.line()+'\n')

def reset():
    '''Discard all changes and reload'''
    global _db
    global _fixed
    del _fixed
    del _db
    _fixed = None
    _db = None

def fixed():
    global _fixed

    if _fixed is None:
        _fixed = []
        with open(os.path.join(_path, '静态.txt'), mode='r', encoding='utf-8') as f:
            for entry in f:
                line = entry.strip()
                if (len(line) <= 0 or line.startswith('#')):
                    continue

                data = line.split('\t')
                common = isWordCommon(data[0])
                _fixed.append((data[0], data[1], common))

    return _fixed

