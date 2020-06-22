import os

_fixed_general = None
_fixed_super = None
_db_general = None
_db_super = None

UNDEFINED = 0       # 未定义
GENERAL = 1         # 通常
SUPER = 2           # 超级

# 拼音表
VALID_PY = {
    '~a', '~ai', '~an', '~ang', '~ao', 'ba', 'bai', 'ban', 'bang', 'bao',
    'bei', 'ben', 'beng', 'bi', 'bian', 'biao', 'bie', 'bin', 'bing', 'bo',
    'bu', 'ca', 'cai', 'can', 'cang', 'cao', 'ce', 'cen', 'ceng', 'cha',
    'chai', 'chan', 'chang', 'chao', 'che', 'chen', 'cheng', 'chi', 'chong',
    'chou', 'chu', 'chua', 'chuai', 'chuan', 'chuang', 'chui', 'chun', 'chuo',
    'ci', 'cong', 'cou', 'cu', 'cuan', 'cui', 'cun', 'cuo', 'da', 'dai',
    'dan', 'dang', 'dao', 'de', 'dei', 'den', 'deng', 'di', 'dia', 'dian',
    'diao', 'die', 'ding', 'diu', 'dong', 'dou', 'du', 'duan', 'dui', 'dun',
    'duo', '~e', '~ei', '~en', '~eng', '~er', 'fa', 'fan', 'fang', 'fei',
    'fen', 'feng', 'fiao', 'fo', 'fou', 'fu', 'ga', 'gai', 'gan', 'gang',
    'gao', 'ge', 'gei', 'gen', 'geng', 'gong', 'gou', 'gu', 'gua', 'guai',
    'guan', 'guang', 'gui', 'gun', 'guo', 'ha', 'hai', 'han', 'hang', 'hao',
    'he', 'hei', 'hen', 'heng', 'hong', 'hou', 'hu', 'hua', 'huai', 'huan',
    'huang', 'hui', 'hun', 'huo', 'ji', 'jia', 'jian', 'jiang', 'jiao', 'jie',
    'jin', 'jing', 'jiong', 'jiu', 'jv', 'juan', 'jue', 'jun', 'ka', 'kai',
    'kan', 'kang', 'kao', 'ke', 'kei', 'ken', 'keng', 'kong', 'kou', 'ku',
    'kua', 'kuai', 'kuan', 'kuang', 'kui', 'kun', 'kuo', 'la', 'lai', 'lan',
    'lang', 'lao', 'le', 'lei', 'leng', 'li', 'lia', 'lian', 'liang', 'liao',
    'lie', 'lin', 'ling', 'liu', 'lo', 'long', 'lou', 'lu', 'luan', 'lun',
    'luo', 'lv', 'lue', 'ma', 'mai', 'man', 'mang', 'mao', 'me', 'mei', 'men',
    'meng', 'mi', 'mian', 'miao', 'mie', 'min', 'ming', 'miu', 'mo', 'mou',
    'mu', 'na', 'nai', 'nan', 'nang', 'nao', 'ne', 'nei', 'nen', 'neng', 'ni',
    'nian', 'niang', 'niao', 'nie', 'nin', 'ning', 'niu', 'nong', 'nou', 'nu',
    'nuan', 'nuo', 'nun', 'nv', 'nue', '~o', '~ou', 'pa', 'pai', 'pan',
    'pang', 'pao', 'pei', 'pen', 'peng', 'pi', 'pian', 'piao', 'pie', 'pin',
    'ping', 'po', 'pou', 'pu', 'qi', 'qia', 'qian', 'qiang', 'qiao', 'qie', 'qin',
    'qing', 'qiong', 'qiu', 'qv', 'quan', 'que', 'qun', 'ran', 'rang', 'rao',
    're', 'ren', 'reng', 'ri', 'rong', 'rou', 'ru', 'rua', 'ruan', 'rui', 'run', 'ruo',
    'sa', 'sai', 'san', 'sang', 'sao', 'se', 'sen', 'seng', 'sha', 'shai',
    'shan', 'shang', 'shao', 'she', 'shei', 'shen', 'sheng', 'shi', 'shou',
    'shu', 'shua', 'shuai', 'shuan', 'shuang', 'shui', 'shun', 'shuo', 'si',
    'song', 'sou', 'su', 'suan', 'sui', 'sun', 'suo', 'ta', 'tai', 'tan',
    'tang', 'tao', 'te', 'teng', 'ti', 'tian', 'tiao', 'tie', 'ting',
    'tong', 'tou', 'tu', 'tuan', 'tui', 'tun', 'tuo', 'wa', 'wai', 'wan',
    'wang', 'wei', 'wen', 'weng', 'wo', 'wu', 'xi', 'xia', 'xian', 'xiang',
    'xiao', 'xie', 'xin', 'xing', 'xiong', 'xiu', 'xv', 'xuan', 'xue', 'xun',
    'ya', 'yan', 'yang', 'yao', 'ye', 'yi', 'yin', 'ying', 'yo', 'yong',
    'you', 'yv', 'yuan', 'yue', 'yun', 'za', 'zai', 'zan', 'zang', 'zao', 'ze',
    'zei', 'zen', 'zeng', 'zha', 'zhai', 'zhan', 'zhang', 'zhao', 'zhe', 'zhei',
    'zhen', 'zheng', 'zhi', 'zhong', 'zhou', 'zhu', 'zhua', 'zhuai', 'zhuan',
    'zhuang', 'zhui', 'zhun', 'zhuo', 'zi', 'zong', 'zou', 'zu', 'zuan', 'zui',
    'zun', 'zuo'
}

class Ci:
    def __init__(self, word, pinyins, which=UNDEFINED):
        self._word = word
        self._pinyins = pinyins
        self._which = which

    @classmethod
    def fromLine(cls, line, which=UNDEFINED):
        obj = cls.__new__(cls)
        super(Ci, obj).__init__()

        data = line.split('\t')
        obj._word = data[0]
        obj._pinyins = []
        obj._which = which
        for i in range(1, len(data), 3):
            obj._pinyins.append((tuple(data[i].split('/')), int(data[i+1]), int(data[i+2])))
        
        return obj

    def line(self):
        line = '%s' % (self._word)
        for pinyin in self._pinyins:
            line += '\t%s\t%d\t%d' % ("/".join(pinyin[0]), pinyin[1], pinyin[2])
        return line
    
    def pinyins(self):
        return set(tuple(pinyin[0]) for pinyin in self._pinyins)

    def word(self):
        return self._word

    def which(self):
        return self._which

    def weights(self):
        return self._pinyins

    def change_which(self, which):
        """
        更换词组隶属码表
        ----------
        which: CiDB.GENERAL | CiDB.SUPER
            通常表 | 超级表
        """
        self._which = which

    def change_code_length(self, pinyin, length):
        """
        更换词组简码长度
        ----------
        pinyin: tuple(str)
            需要修改的拼音
        length: int
            码长
        """
        for i in range(len(self._pinyins)):
            weight = self._pinyins[i]
            if weight[0] == pinyin:
                self._pinyins[i] = (weight[0], length, weight[2])

    def change_code_rank(self, pinyin, rank):
        """
        更换词组简码权值
        ----------
        pinyin: tuple(str)
            需要修改的拼音
        rank: int
            权值
        """
        for i in range(len(self._pinyins)):
            weight = self._pinyins[i]
            if weight[0] == pinyin:
                self._pinyins[i] = (weight[0], weight[1], rank)

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
            assert len(pyt) == len(sound), '"%s" 词拼音 "%s" 不合法（长度不符）' % (self._word, " ".join(pyt))
            for py in pyt:
                assert py in VALID_PY, '"%s" 词拼音 "%s" 不合法（非法拼音）' % (self._word, " ".join(pyt))
        
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
    global _db_general
    global _db_super
    if _db_general == None or _db_super == None:
        _db_general = {}
        _db_super = {}
    else:
        return
    
    with open(os.path.join(_path, '通常.txt'), mode='r', encoding='utf-8') as f:
        for line in f:
            word = Ci.fromLine(line.strip(), GENERAL)
            _db_general[word._word] = word

    with open(os.path.join(_path, '超级.txt'), mode='r', encoding='utf-8') as f:
        for line in f:
            word = Ci.fromLine(line.strip(), SUPER)

            if (word._word in _db_general):
                print('警告，通常词和超级词重复：', word.word())
            else:
                _db_super[word._word] = word

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
    
    if word not in _db_general:
        if word not in _db_super:
            return None
        return _db_super[word]
    return _db_general[word]

def all(which):
    _loadDB()
    if which == GENERAL:
        return _db_general.values()
    else:
        return _db_super.values()

def add(word, pinyins, which = GENERAL):
    """
    添加词组到词库
    ----------
    word : str
        需要添加的词组
    pinyins: list[tuple(py: tuple(str), len: int, rank: int)]
        list[tuple(拼音, 码长, 码序权值)]
    which: CiDB.GENERAL | CiDB.SUPER
        通常表 | 超级表
    """

    _loadDB()
    
    assert len(word) != 1, '"%s" 不是词组' % word
    assert word not in _db, '"%s" 词已存在' % word
    assert len(pinyins) != 0, '"%s" 词没有提供拼音' % word

    sound = sound_chars(word)

    for pinyin in pinyins:
        assert len(pinyin[0]) == len(sound), '"%s" 词拼音 "%s" 不合法（长度不符）' % (word, " ".join(pinyin[0]))
        for py in pinyin[0]:
            assert py in VALID_PY, '"%s" 词拼音 "%s" 不合法（非法拼音）' % (word, " ".join(pinyin[0]))
    
    _db[word] = Ci(word, pinyins, which)

def remove(word, pinyins):
    """
    删除词组拼音，如果空音则彻底删除
    ----------
    word : str
        目标词组
    pinyins: set(str)
        需要删除的拼音
    """

    assert word in _db, '"%s" 词不存在' % word
    _db[word].remove_pinyins(pinyins)

    if len(_db[word].pinyins()) <= 0:
        del _db[word]

def commit():
    _loadDB()

    with open(os.path.join(_path, '通常.txt'), mode='w', encoding='utf-8', newline='\n') as f:
        all_words = sorted(all(GENERAL), key=lambda x: x._word)
        for ci in all_words:
            f.write(ci.line()+'\n')

    with open(os.path.join(_path, '超级.txt'), mode='w', encoding='utf-8', newline='\n') as f:
        all_words = sorted(all(SUPER), key=lambda x: x._word)
        for ci in all_words:
            f.write(ci.line()+'\n')

def fixed(which):
    global _fixed_general
    global _fixed_super
    if (which == GENERAL):
        if _fixed_general is None:
            _fixed_general = []
            with open(os.path.join(_path, '通常特定.txt'), mode='r', encoding='utf-8') as f:
                for entry in f:
                    line = entry.strip()
                    if (len(line) <= 0 or line.startswith('#')):
                        continue

                    data = line.split('\t')
                    _fixed_general.append((data[0], data[1]))
        
        return _fixed_general
    else:
        if _fixed_super is None:
            _fixed_super = []
            with open(os.path.join(_path, '超级特定.txt'), mode='r', encoding='utf-8') as f:
                for entry in f:
                    line = entry.strip()
                    if (len(line) <= 0 or line.startswith('#')):
                        continue

                    data = line.split('\t')
                    _fixed_super.append((data[0], data[1]))
        return _fixed_super