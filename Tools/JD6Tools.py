# Sorry but this is for non-tech savvy people
from ZiDB import ZiDB

# ---------------------------------
#             布局定义
# ---------------------------------

# 键道6 键->声母
JD6_K2S = {
    'q': ['q', 'zh'],
    'w': ['w', 'ch'],
    'e': ['sh'],
    'r': ['r'],
    't': ['t'],
    'y': ['y'],
    'p': ['p'],
    's': ['s'],
    'd': ['d'],
    'f': ['f', 'zh'],
    'g': ['g'],
    'h': ['h'],
    'j': ['j', 'ch'],
    'k': ['k'],
    'l': ['l'],
    'z': ['z'],
    'x': ['x', '~'],
    'c': ['c'],
    'b': ['b'],
    'n': ['n'],
    'm': ['m'],
}

# 键道6 声母->键
JD6_S2K = {
    'q': ['q'],
    'w': ['w'],
    'r': ['r'],
    't': ['t'],
    'y': ['y'],
    'p': ['p'],
    's': ['s'],
    'd': ['d'],
    'f': ['f'],
    'g': ['g'],
    'h': ['h'],
    'j': ['j'],
    'k': ['k'],
    'l': ['l'],
    'z': ['z'],
    'x': ['x'],
    'c': ['c'],
    'b': ['b'],
    'n': ['n'],
    'm': ['m'],
    'zh': ['q', 'f'],
    'ch': ['j', 'w'],
    'sh': ['e'],
    '~': ['x'],
}

# 键道6 zh/ch拼合 + 飞键
JD6_SFLY = {
    'zh': [
        {'u', 'un', 'en', 'eng', 'an', 'ang', 'ao', 'e', 'ai', 'ao', 'ei'},
        {'a', 'ai', 'ao', 'e', 'i', 'ong', 'ou', 'ua', 'uai', 'uan', 'uang', 'ui', 'uo'}
    ],
    'ch': [
        {'u', 'un', 'en', 'eng', 'an', 'ang', 'ao', 'e', 'ai', 'ao'},
        {'a', 'ao', 'e', 'i', 'ong', 'ou', 'ua', 'uai', 'uan', 'uang', 'ui', 'uo'}
    ]
}

# 键道6 键->韵母
JD6_K2Y = {
    'q': ['ua', 'iu'],
    'w': ['ei', 'un'],
    'e': ['e'],
    'r': ['eng'],
    't': ['uan'],
    'y': ['ong', 'iong'],
    'p': ['ang'],
    's': ['a', 'ia'],
    'd': ['ou', 'ie'],
    'f': ['an'],
    'g': ['uai', 'ing'],
    'h': ['ai', 'ue'],
    'j': ['u', 'er'],
    'k': ['i'],
    'l': ['uo', 'v', 'o'],
    'z': ['ao'],
    'x': ['iang', 'uang'],
    'c': ['iao'],
    'b': ['in', 'ui'],
    'n': ['en'],
    'm': ['ian', 'uang'],
}

# 键道6 韵母->键
JD6_Y2K = {
    'ua': ['q'],
    'iu': ['q'],
    'ei': ['w'],
    'un': ['w'],
    'e': ['e'],
    'eng': ['r'],
    'uan': ['t'],
    'ong': ['y'],
    'iong': ['y'],
    'ang': ['p'],
    'a': ['s'],
    'ia': ['s'],
    'ou': ['d'],
    'ie': ['d'],
    'an': ['f'],
    'uai': ['g'],
    'ing': ['g'],
    'ai': ['h'],
    'ue': ['h'],
    'u': ['j'],
    'er': ['j'],
    'i': ['k'],
    'uo': ['l'],
    'v': ['l'],
    'o': ['l'],
    'ao': ['z'],
    'iang': ['x'],
    'uang': ['x', 'm'],
    'iao': ['c'],
    'in': ['b'],
    'ui': ['b'],
    'en': ['n'],
    'ian': ['m'],
}

# ---------------------------------
#             辅助函数
# ---------------------------------
def sheng(py):
    """取全拼声母"""
    if py.startswith('zh'):
        return 'zh'
    if py.startswith('ch'):
        return 'ch'
    if py.startswith('sh'):
        return 'sh'
    return py[0]

def yun(py):
    """取全拼韵母"""
    if py.startswith('zh') or py.startswith('ch') or py.startswith('sh'):
        return py[2:]
    return py[1:]

def pinyins2sys(py):
    """全拼转双拼"""
    shengmu = sheng(py)
    yunmu = yun(py)

    s = []
    if (shengmu in JD6_SFLY):
        # 一类
        if yunmu in JD6_SFLY[shengmu][0]:
            s.append(JD6_S2K[shengmu][0])
        # 二类
        if yunmu in JD6_SFLY[shengmu][1]:
            s.append(JD6_S2K[shengmu][1])
    else:
        s = JD6_S2K[shengmu]

    y = JD6_Y2K[yun(py)]
    sy = []
    for ss in s:
        for yy in y:
            sy.append(ss+yy)
    return sy

def zi2codes(zi):
    codes = []
    sy_codes = {}

    weights = zi.weights()
    for w in weights:
        sys = pinyins2sys(w[0])
        for sy in sys:
            if sy in sy_codes:
                sy_codes[sy] = min(sy_codes[sy], w[1])
            else:
                sy_codes[sy] = w[1]

    b = zi.shape()
    char = zi.char()
    rank = zi.rank()
    which = zi.which()
    for sy in sy_codes:
        w = sy_codes[sy]
        full_code = sy+b
        if (w < len(full_code)):
            codes.append((char, full_code[:w], rank, which))
        codes.append((char, full_code, rank, which))

    return codes

# ---------------------------------
#              主行为
# ---------------------------------

# 读取字库
Zi = ZiDB()

def make_danzi_dict():
    """生成单字码表"""
    entries = []
    chars = Zi.all()
    for zi in chars:
        entries += zi2codes(zi)

    for entry in Zi.fixed():
        entries.append((entry[0], entry[1], -1, 'general'))
    
    entries.sort(key=lambda e: (e[1], e[2]))
    last_code = ''
    dups = []

    danzi = open('danzi.txt', mode='w', encoding='utf-8')
    chaoji = open('chaojidanzi.txt', mode='w', encoding='utf-8')

    for entry in entries:
        code = entry[1]
        char = entry[0]
        which = entry[3]

        if which == 'general':
            f = danzi
        elif which == 'super':
            f = chaoji
        else:
            f = None

        # 检查重码
        if (len(code) < 6 and len(code) > 1):
            if (code == last_code):
                dups.append(char)
            else:
                if (len(dups) > 1):
                    print('重码：', last_code, dups)
                dups = [char]
        else:
            if (len(dups) > 1):
                print('重码：', last_code, dups)
            dups.clear()

        last_code = code

        if f is not None:
            f.write(char+'\t'+code+'\n')
    
    if (len(dups) > 1):
        print('重码：', last_code, dups)

    danzi.close()
    chaoji.close()

make_danzi_dict()