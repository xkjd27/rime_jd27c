import os
import re

UNDEFINED = 0       # 未定义
GENERAL = 1         # 通常
SUPER = 2           # 超级
HIDDEN = 3          # 无理

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

class Zi:
    def __init__(self, line, which=HIDDEN):
        data = line.split('\t')
        self._char = data[0]
        self._rank = int(data[1])
        self._shape = data[2]
        self._pinyins = []
        self._type = which
        self._comment = None
        for i in range(3, len(data) - 1, 2):
            self._pinyins.append((data[i], int(data[i+1])))
        
        if (len(data) % 2 == 0):
            self._comment = data[-1]

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

    def comment(self):
        if self._comment is None:
            return ''
        return self._comment
    
    def line(self):
        line = '%s\t%d\t%s' % (self._char, self._rank, self._shape)
        for pinyin in self._pinyins:
            line += '\t%s\t%d' % pinyin
        if self._comment is not None:
            line += '\t%s' % self._comment
        return line


_db = {}
_fixed = []

_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(_path, '通常.txt'), mode='r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        char = Zi(line.strip(), GENERAL)
        _db[char._char] = char

with open(os.path.join(_path, '超级.txt'), mode='r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        char = Zi(line.strip(), SUPER)
        if (char._char in _db):
            print('警告，通常字和超级字重复：', char.char())
        else:
            _db[char._char] = char

with open(os.path.join(_path, '无理.txt'), mode='r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        char = Zi(line.strip(), HIDDEN)
        if (char._char in _db):
            print('警告，通常字和无理字重复：', char.char())
        else:
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

def add(char, shape, pinyins, rank, which = HIDDEN, comment = None):
    assert re.search("^[aiouv]{3,4}$", shape), '形码不合法'
    assert char not in _db, '该字已存在'
    assert len(pinyins) != 0, '没有提供拼音'
    for pinyin in pinyins:
        assert pinyin in VALID_PY, '拼音 "%s" 不合法' % pinyin

    line = '%s\t%d\t%s' % (char, rank, shape)
    for pinyin in pinyins:
        line += '\t%s\t6' % pinyin
    if comment is not None:
        line += '\t%s' % comment
    _db[char] = Zi(line, which)

def commit():
    all_char = sorted(all(), key=lambda x: x._char)
    danzi = open(os.path.join(_path, '通常.txt'), mode='w', encoding='utf-8', newline='\n')
    chaoji = open(os.path.join(_path, '超级.txt'), mode='w', encoding='utf-8', newline='\n')
    hidden = open(os.path.join(_path, '无理.txt'), mode='w', encoding='utf-8', newline='\n')

    for zi in all_char:
        if zi.which() == GENERAL:
            danzi.write(zi.line()+'\n')
        elif zi.which() == SUPER:
            chaoji.write(zi.line()+'\n')
        else:
            hidden.write(zi.line()+'\n')
    
    danzi.close()
    chaoji.close()
    hidden.close()
