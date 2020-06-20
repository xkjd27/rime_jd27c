import sys
import ZiDB

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
#               常量
# ---------------------------------

RIME_HEADER = '---\nname: xkjd6.%s\nversion: "Q1"\nsort: original\n...\n'
PUNC = set('＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏！？｡。')

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

def isGBK(char):
    """检查字符是否属于GBK"""
    try:
        char.encode('gbk')
        return True
    except:
        return False

def zi2codes(zi):
    codes = []
    sy_codes = {}

    weights = zi.weights()
    for w in weights:
        sy = pinyins2sys(w[0])
        if (len(sy) == 0):
            continue

        # 飞键标记
        is_fly = len(sy) > 1
        if (is_fly):
            if sy[0] in sy_codes:
                sy_codes[sy[0]] = (min(sy_codes[sy[0]][0], w[1]), sy[1])
            else:
                sy_codes[sy[0]] = (w[1], sy[1])

            if sy[1] in sy_codes:
                sy_codes[sy[1]] = (min(sy_codes[sy[1]][0], w[1]), sy[0])
            else:
                sy_codes[sy[1]] = (w[1], sy[0])
        else:
            sy = sy[0]
            if sy in sy_codes:
                sy_codes[sy] = (min(sy_codes[sy][0], w[1]), sy_codes[sy][1])
            else:
                sy_codes[sy] = (w[1], None)

    b = zi.shape()
    char = zi.char()
    rank = zi.rank()
    which = zi.which()

    for sy in sy_codes:
        w, fly = sy_codes[sy]
        full_code = sy+b
        if (w < len(full_code)):
            has_short = True
            if (w > 1):
                # 不自动生成一简
                codes.append((char, full_code[:w], rank, which, None))
        else:
            has_short = False
        codes.append((char, full_code, rank, which, (has_short, fly + full_code[2:] if fly is not None else None)))

    return codes

def get_danzi_codes():
    """获取单字码表"""

    global _entries
    global _entries_r

    try:
        _entries
    except:
        _entries = None

    try:
        _entries_r
    except:
        _entries_r = None

    if (_entries == None or _entries_r == None):
        _entries = []
        _entries_r = {}

    chars = ZiDB.all()
    for zi in chars:
        codes = zi2codes(zi)
        _entries += codes
        for code in codes:
            if (code[1] in _entries_r):
                _entries_r[code[1]].append(code)
            else:
                _entries_r[code[1]] = [code]


    for entry in ZiDB.fixed():
        code = (entry[0], entry[1], -1, ZiDB.GENERAL, None)
        _entries.append(code)
        if (code[1] in _entries_r):
            _entries_r[code[1]].append(code)
        else:
            _entries_r[code[1]] = [code]
    
    return _entries, _entries_r

def clear_danzi_codes():
    """Dirtify单字码表"""
    global _entries
    global _entries_r
    _entries = None
    _entries_r = None

# ---------------------------------
#              主行为
# ---------------------------------
def traverse_danzi(build = False):
    """遍历单字码表"""
    entries, codes = get_danzi_codes() 
    entries.sort(key=lambda e: (e[1], e[2]))

    last_code = ''
    dups = []

    if build:
        danzi = open('rime/xkjd6.danzi.yaml', mode='w', encoding='utf-8', newline='\n')
        chaoji = open('rime/xkjd6.chaojizi.yaml', mode='w', encoding='utf-8', newline='\n')
        danzi.write(RIME_HEADER % 'danzi')
        chaoji.write(RIME_HEADER % 'chaojizi')
    else:
        danzi = None
        chaoji = None

    for entry in entries:
        char, code, rank, which, full_code = entry

        if which == ZiDB.GENERAL:
            f = danzi
        elif which == ZiDB.SUPER:
            f = chaoji
        else:
            continue

        # 检查重码
        if (len(code) < 6 and len(code) > 1):
            if (code == last_code):
                dups.append(char)
            else:
                if (len(dups) > 1):
                    print('重码：%6s %s' % (last_code, str(dups)))
                dups = [char]
        else:
            if (len(dups) > 1):
                print('重码：%6s %s' % (last_code, str(dups)))
            dups.clear()

        # 简码空间检查
        if (full_code and not full_code[0]):
            fly = full_code[1]
            tmp_codes = [code[:-1]]
            if (fly is not None):
                tmp_codes.append(fly[:-1])

            avaliable_short = None
            substitute = None
            while True:
                short_avaliable = True
                for sc in tmp_codes:
                    if sc in codes and len(codes[sc]) == 1:
                        if (codes[sc][0][3] != ZiDB.SUPER or which != ZiDB.GENERAL):
                            short_avaliable = False
                        else:
                            substitute = codes[sc][0][0]
                    else:
                        substitute = None
            
                if not short_avaliable:
                    if (avaliable_short is not None):
                        if (substitute is not None):
                            print('可替换："%s" %6s -> %6s (替换超级字 "%s")' % (char, code, avaliable_short, substitute))
                        else:
                            print('可缩码："%s" %6s -> %6s (%s)' % (char, code, avaliable_short, ('通常' if which == ZiDB.GENERAL else '超级')))
                    break

                avaliable_short = tmp_codes[0]
                tmp_codes = [sc[:-1] for sc in tmp_codes]

        last_code = code

        if f is not None:
            f.write(char+'\t'+code+'\n')
    
    if (len(dups) > 1):
        print('重码：%6s %s' % (last_code, str(dups)))

    if (danzi is not None):
        danzi.close()
    if (chaoji is not None):
        chaoji.close()

    if build:
        print('码表已保存')
    else:
        print('检查完毕')

def full_cizu_check(build = False):
    pass

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else None

    if action == "build_danzi":
        traverse_danzi(True)
    elif action == "danzi_change":
        pass
    elif action == "full_cizu_check":
        full_cizu_check()

    traverse_danzi(True)

