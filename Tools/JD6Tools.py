import sys
import os
import ZiDB
import CiDB
import itertools

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

# 拼音变体转换表
PY_TRANSFORM = {
    'a': '~a', 
    'ai': '~ai',
    'an': '~an',
    'ang': '~ang',
    'ao': '~ao',
    'e': '~e',
    'ei': '~ei',
    'en': '~en',
    'eng': '~eng',
    'er': '~er',
    'o': '~o',
    'ou': '~ou',
    'ju': 'jv',
    'qu': 'qv',
    'xu': 'xv'
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

def pinyin2sy(py):
    """全拼转双拼"""
    shengmu = sheng(py)
    yunmu = yun(py)

    s = []
    if (shengmu in JD6_SFLY):
        # 一类
        if yunmu in JD6_SFLY[shengmu][0]:
            s.append(JD6_S2K[shengmu][0].upper())
        # 二类
        if yunmu in JD6_SFLY[shengmu][1]:
            s.append(JD6_S2K[shengmu][1].upper())
    else:
        s = JD6_S2K[shengmu]

    y = JD6_Y2K[yun(py)]
    sy = []
    for ss in s:
        for yy in y:
            sy.append(ss+yy)

    return sy

def pinyin2s(py):
    """全拼转声拼"""
    shengmu = sheng(py)
    yunmu = yun(py)

    s = []
    if (shengmu in JD6_SFLY):
        # 一类
        if yunmu in JD6_SFLY[shengmu][0]:
            s.append(JD6_S2K[shengmu][0].upper())
        # 二类
        if yunmu in JD6_SFLY[shengmu][1]:
            s.append(JD6_S2K[shengmu][1].upper())
    else:
        s = JD6_S2K[shengmu]

    return s

def transform_py(py):
    """全拼预处理"""
    pinyin = py.strip().lower()
    if pinyin in PY_TRANSFORM:
        return PY_TRANSFORM[pinyin]
    return pinyin

def isGBK(char):
    """检查字符是否属于GBK"""
    try:
        char.encode('gbk')
        return True
    except:
        return False

def zi2codes(zi, short = True, full = True):
    codes = []
    sy_codes = {}

    weights = zi.weights()
    for w in weights:
        sy = pinyin2sy(w[0])
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

        if (w <= 0):  # 忽略无理读音
            continue
    
        if (w < len(full_code)):
            has_short = True
            if (w > 1 and short):   # 不自动生成一简
                codes.append((char, full_code[:w], rank, which, None))
        else:
            has_short = False
        
        if full:
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

def word_pinyin2codes(pys):
    """词拼音转声码"""

    # 飞键：通常最多允许双飞
    #   例：zhe/zhuang
    #       生成：fefm,fefx
    #       忽略：qefx,qefm
    #   例：zhuang/zhuang
    #       生成：fmfm,fxfx
    #       忽略：fmfx,fxfm
    #   例：zhe/zhe/zhe
    #       生成：fff,qqq
    #       忽略：ffq,fqf,fqq,qff,qfq,qqf
    # 四飞特例:
    #   例: che/che/chao
    #       生成：jjq,wwf,jjf,wwq

    if len(pys) <= 2:
        # 二字词
        codes = set("".join(wordpy) for wordpy in itertools.product(*[pinyin2sy(py) for py in pys]))

        if len(codes) > 2:
            og_codes = codes
            codes = set()

            for code in og_codes:
                zh = [s.upper() for s in JD6_S2K['zh']]
                if ((code[0] == zh[0] and code[2] == zh[1]) or (code[0] == zh[1] and code[2] == zh[0])):
                    continue
                ch = [s.upper() for s in JD6_S2K['ch']]
                if ((code[0] == ch[0] and code[2] == ch[1]) or (code[0] == ch[1] and code[2] == ch[0])):
                    continue
                uang = JD6_Y2K['uang']
                if ((code[1] == uang[0] and code[3] == uang[1]) or (code[1] == uang[1] and code[3] == uang[0])):
                    continue
                codes.add(code)

            if (len(codes) < 2):
                print(og_codes)
                print(codes)
    else:
        # 多字词
        codes = set("".join(wordpy) for wordpy in itertools.product(*[pinyin2s(py) for py in pys]))

        if len(codes) > 2:
            og_codes = codes
            codes = set()

            for code in og_codes:
                zh = [s.upper() for s in JD6_S2K['zh']]
                if (zh[0] in code and zh[1] in code):
                    continue
                ch = [s.upper() for s in JD6_S2K['ch']]
                if (ch[0] in code and ch[1] in code):
                    continue

                codes.add(code)
    
            if (len(codes) < 2):
                print(og_codes)
                print(codes)
    
    return set(code.lower() for code in codes)

def ci2codes(ci, short = True, full = False):
    """生成词6码"""
    weights = ci.weights()
    sound_chars = ci.sound_chars()
    codes = set()
    for data in weights:
        pinyin, shortcode_len, rank = data
        if len(pinyin) == 3:
            # 三字词需三码
            shape = ZiDB.get(sound_chars[0]).shape()[0] + ZiDB.get(sound_chars[1]).shape()[0] + ZiDB.get(sound_chars[2]).shape()[0]
        else:
            shape = ZiDB.get(sound_chars[0]).shape()[0] + ZiDB.get(sound_chars[1]).shape()[0]
        
        s_codes = word_pinyin2codes(pinyin)
        for code in s_codes:
            full_code = code + shape
            if (full):
                codes.add((ci.word(), full_code, len(s_codes), rank))
            if (short):
                short_code = full_code[:shortcode_len]
                codes.add((ci.word(), short_code, len(s_codes), rank))
            
    return codes

# ---------------------------------
#              主行为
# ---------------------------------
def traverse_danzi(build = False):
    """遍历单字码表"""
    entries, codes = get_danzi_codes() 
    entries.sort(key=lambda e: (e[1], e[2]))

    last_code = ''

    rank_check = [
        None,
        ('', '', -2),
        ('', '', -2),
    ]

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

        if (len(code) == 6 and rank_check[which][0] == code and rank_check[which][2] == rank):
            print('全码序冲突：%6s %s %s [%d] (%s)' % (code, char, rank_check[which][1], rank, ('通常' if which == ZiDB.GENERAL else '超级')))

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

        rank_check[which] = (code, char, rank)

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

def traverse_cizu(which, build = False, report = True):
    """遍历词组码表"""
    dup_code_check = {}
    last_rank = -1
    entries = []

    words = CiDB.all(which)
    for ci in words:
        codes = ci2codes(ci, True, False)
        entries += codes

    entries.sort(key=lambda e: (e[1], e[2]))

    if build:
        if which == CiDB.GENERAL:
            f = open('rime/xkjd6.cizu.yaml', mode='w', encoding='utf-8', newline='\n')
            f.write(RIME_HEADER % 'cizu')
        else:
            f = open('rime/xkjd6.chaojici.yaml', mode='w', encoding='utf-8', newline='\n')
            f.write(RIME_HEADER % 'chaojici')
    else:
        f = None

    for entry in entries:
        word, code, fly, rank = entry
        if f is not None:
            f.write(word+'\t'+code+'\n')
        
        if code in dup_code_check:
            dup_code_check[code].append((word, rank, fly))
        else:
            dup_code_check[code] = [(word, rank, fly)]

    if (f is not None):
        f.close()

    dup_count = [0,0,0,0]
    dup_word_count = 0
    for code in dup_code_check:
        if len(dup_code_check[code]) > 1:
            dup_count[len(code) - 3] += 1
            dup_word_count += len(dup_code_check[code])

    if report:
        if which == CiDB.GENERAL:
            filename = 'Report/cizu.txt'
        else:
            filename = 'Report/chaojici.txt'

        report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        report = open(report_path, mode='w', encoding='utf-8', newline='\n')
        code_total = len(dup_code_check)
        dup_total = sum(dup_count)
        report.write('总码量：%d\n' % code_total)
        report.write('重码量：%d\n' % dup_total)
        report.write('三码重码：%d\n' % dup_count[0])
        report.write('四码重码：%d\n' % dup_count[1])
        report.write('五码重码：%d\n' % dup_count[2])
        report.write('六码重码：%d\n' % dup_count[3])
        report.write('重码词数：%d\n' % dup_word_count)
        report.write('重码率：%.2f%%\n' % ((dup_total / code_total) * 100))
        report.write('---\n')

        records = list(dup_code_check.items())
        records.sort(key=lambda e: (len(e[0]), e[0]))
        
        for record in records:
            code = record[0]
            dups = record[1]
            if len(dups) <= 1:
                continue
                
            report.write('%s\n' % code)
            for word in dups:
                fly_name = '错'
                if word[2] == 2:
                    fly_name = '飞'
                elif word[2] == 1:
                    fly_name = '　'
                report.write('\t%d\t%s\t%s\n' % (word[1], fly_name, word[0]))
        
            report.write('\n')

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else None

    if action == "build_danzi":
        traverse_danzi(True)
    elif action == "danzi_change":
        pass
    elif action == "full_cizu_check":
        build_cizu()

    # traverse_danzi(True)
    # ZiDB.commit()
    # print(ci2codes(CiDB.get('这桩'), short = False, full = True))
    # print(ci2codes(CiDB.get('这这这'), short = False, full = True))
    # print(ci2codes(CiDB.get('骑着'), short = False, full = True))
    # print(ci2codes(CiDB.get('服装'), short = False, full = True))
    # print(ci2codes(CiDB.get('装装'), short = False, full = True))
    # print(ci2codes(CiDB.get('江面'), short = False, full = True))
    # print(ci2codes(CiDB.get('去装'), short = False, full = True))
    # print(ci2codes(CiDB.get('车车昭'), short = False, full = True))
    # print(ci2codes(CiDB.get('曲曲折折'), short = False, full = True))
    # CiDB.commit()
    # traverse_cizu(CiDB.GENERAL, True, True)
