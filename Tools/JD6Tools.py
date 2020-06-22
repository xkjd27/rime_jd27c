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
    'qve': 'que',
    'lve': 'lue',
    'jve': 'jue',
    'xve': 'xue',
    'yve': 'yue',
    'ju': 'jv',
    'qu': 'qv',
    'xu': 'xv',
    'yu': 'yv',
    'ng': '~eng',
    'm': '~en',
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
        sy = [code.lower() for code in pinyin2sy(w[0])]
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
    else:
        return _entries, _entries_r

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
        code = (entry[0], entry[1], -1, entry[2], None)
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
        og_codes = set("".join(wordpy) for wordpy in itertools.product(*[pinyin2sy(py) for py in pys]))
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

    else:
        # 多字词
        og_codes = set("".join(wordpy) for wordpy in itertools.product(*[pinyin2s(py) for py in pys]))
        codes = set()

        for code in og_codes:
            zh = [s.upper() for s in JD6_S2K['zh']]
            if (zh[0] in code and zh[1] in code):
                continue
            ch = [s.upper() for s in JD6_S2K['ch']]
            if (ch[0] in code and ch[1] in code):
                continue

            codes.add(code)
    
    
    return set(code.lower() for code in codes)

def ci2codes(ci, short = True, full = False):
    """生成词6码"""
    sound_chars = ci.sound_chars()

    if len(sound_chars) == 1: # 一字词（非法）无视
        return None

    py_codes = {}
    weights = ci.weights()

    shape = ZiDB.get(sound_chars[0]).shape()[0] + ZiDB.get(sound_chars[1]).shape()[0]
    if len(sound_chars) == 3: # 三字词需三码
        shape += ZiDB.get(sound_chars[2]).shape()[0]
        

    for data in weights:
        pinyin, shortcode_len, rank = data
        s_codes = word_pinyin2codes(pinyin)

        for code in s_codes:
            if code in py_codes:
                py_codes[code] = (min(shortcode_len, py_codes[code][0]), max(rank, py_codes[code][1]), len(s_codes))
            else:
                py_codes[code] = (shortcode_len, rank, len(s_codes))
            
    codes = set()
    for code in py_codes:
        full_code = code + shape
        shortcode_len, rank, fly = py_codes[code]
        if (full):
            codes.add((ci.word(), full_code, rank, fly))
        if (short):
            short_code = full_code[:shortcode_len]
            codes.add((ci.word(), short_code, rank, fly))
            
    return codes

# ---------------------------------
#             码表生成
# ---------------------------------
def traverse_danzi(build = False, report = True):
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
        danzi.write(RIME_HEADER % 'danzi')
    else:
        danzi = None

    if report:
        report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Report/单字健康报告.txt')
        report = open(report_path, mode='w', encoding='utf-8', newline='\n')
    else:
        report = None

    for entry in entries:
        char, code, rank, which, full_code = entry

        if which == ZiDB.GENERAL:
            f = danzi
        elif which == ZiDB.SUPER:
            # 超级码依然进行重码判断
            f = None
        else:
            continue

        # 检查重码
        if (len(code) < 6 and len(code) > 1):
            if (code == last_code):
                dups.append(char)
            else:
                if (len(dups) > 1):
                    report.write('重码：%6s %s\n' % (last_code, str(dups)))
                dups = [char]
        else:
            if (len(dups) > 1):
                report.write('重码：%6s %s\n' % (last_code, str(dups)))
            dups.clear()

        if (len(code) == 6 and rank_check[which][0] == code and rank_check[which][2] == rank):
            report.write('全码序冲突：%6s %s %s [%d] (%s)\n' % (code, char, rank_check[which][1], rank, ('通常' if which == ZiDB.GENERAL else '超级')))

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
                            report.write('可替换："%s" %6s -> %6s (替换超级字 "%s")\n' % (char, code, avaliable_short, substitute))
                        else:
                            report.write('可缩码："%s" %6s -> %6s (%s)\n' % (char, code, avaliable_short, ('通常' if which == ZiDB.GENERAL else '超级')))
                    break

                avaliable_short = tmp_codes[0]
                tmp_codes = [sc[:-1] for sc in tmp_codes]

        last_code = code

        rank_check[which] = (code, char, rank)

        if f is not None:
            f.write(char+'\t'+code+'\n')
    
    if (len(dups) > 1):
        report.write('重码：%6s %s\n' % (last_code, str(dups)))

    if (danzi is not None):
        danzi.close()

    if report:
        report.write('检查完毕\n')
    else:
        report.close()

def traverse_cizu(build = False, report = True):
    """遍历词组码表"""
    dup_code_check = {}
    last_rank = -1
    entries = []

    words = CiDB.all(CiDB.GENERAL)
    for ci in words:
        codes = ci2codes(ci, True, False)
        if (codes is not None):
            entries += codes

    extra = 100
    for entry in CiDB.fixed(CiDB.GENERAL):
        code = (entry[0], entry[1], extra, 1)
        entries.append(code)
        extra += 1

    entries.sort(key=lambda e: (e[1], e[2]))

    if build:
        f = open('rime/xkjd6.cizu.yaml', mode='w', encoding='utf-8', newline='\n')
        f.write(RIME_HEADER % 'cizu')
    else:
        f = None

    for entry in entries:
        word, code, rank, fly = entry
        if f is not None:
            f.write(word+'\t'+code+'\n')
        
        if code in dup_code_check:
            dup_code_check[code].append((word, rank, fly))
        else:
            dup_code_check[code] = [(word, rank, fly)]

    if (f is not None):
        f.close()

    # 所有重码数量
    dup_count = [0,0,0,0]

    # 不包括飞键重码的重码数量
    lose_dup_count = [0,0,0,0]

    # 允许飞键重码的宽容码
    code_dup_lose_flag = set()

    # 飞键重码多于两重的
    word_dup_strict_flag = {}

    dup_word_count = 0
    for code in dup_code_check:
        code_dups = len(dup_code_check[code])
        
        if (len(code) == 6 and code_dups > 1):
            dup_count[len(code) - 3] += 1
            dup_word_count += len(dup_code_check[code])
            code_dup_lose_flag.add(code)
            continue

        # 如果只有二重
        if code_dups == 2:
            # 如果强制允许了重码
            if dup_code_check[code][1][1] >= 10 and dup_code_check[code][0][1] != dup_code_check[code][1][1]:
                code_dup_lose_flag.add(code)
            # 如果已经设置好了权值
            elif dup_code_check[code][0][1] != dup_code_check[code][1][1]:
                fly_word = None
                # 如果第一个词是飞键
                if (dup_code_check[code][0][2] > 1):
                    fly_word = dup_code_check[code][0][0]
                # 如果第二个词是飞键
                elif (dup_code_check[code][1][2] > 1):
                    fly_word = dup_code_check[code][1][0]

                if (fly_word is not None):
                    code_dup_lose_flag.add(code)
                    if fly_word in word_dup_strict_flag:
                        word_dup_strict_flag[fly_word] += 1
                    else:
                        word_dup_strict_flag[fly_word] = 1
                else:
                    lose_dup_count[len(code) - 3] += 1
            else:
                lose_dup_count[len(code) - 3] += 1

        if code_dups > 1:
            dup_count[len(code) - 3] += 1
            dup_word_count += len(dup_code_check[code])

    if report:
        report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Report/词组重码报告.txt')
        report_path_2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Report/容许重码记录.txt')
        report = open(report_path, mode='w', encoding='utf-8', newline='\n')
        report_allowed = open(report_path_2, mode='w', encoding='utf-8', newline='\n')

        code_total = len(dup_code_check)
        dup_total = sum(dup_count)
        lose_dup_total = sum(lose_dup_count)

        report.write('总码量：%d\n' % code_total)
        report.write('严格重码量：%d\n' % dup_total)
        report.write('严格重码率：%.2f%%\n' % ((dup_total / code_total) * 100))
        report.write('宽容重码量：%d\n' % lose_dup_total)
        report.write('宽容重码率：%.2f%%\n' % ((lose_dup_total / code_total) * 100))
        report.write('三码重码：%d\n' % dup_count[0])
        report.write('四码重码：%d\n' % dup_count[1])
        report.write('五码重码：%d\n' % dup_count[2])
        report.write('六码重码：%d\n' % dup_count[3])
        report.write('重码词数：%d\n' % dup_word_count)

        report.write('---\n')

        records = list(dup_code_check.items())
        records.sort(key=lambda e: (len(e[0]), e[0]))
        
        for record in records:
            code = record[0]
            dups = record[1]
            if len(dups) <= 1:
                continue
                
            if (code in code_dup_lose_flag):
                f = report_allowed
            else:
                f = report

            f.write('%s\n' % code)
            fly_name = "　双三四"
            
            for word in dups:
                f.write('\t%d\t%s\t%s\n' % (word[1], fly_name[word[2]-1], word[0]))
        
            f.write('\n')

        report.write('\n---\n\n')
        report.write('可能异常的飞键词：\n')

        for word in word_dup_strict_flag:
            if word_dup_strict_flag[word] > 1:
                f.write('\t%s\n' % (word))

        report.close()
        report_allowed.close()


def build_chaoji():
    entries, _ = get_danzi_codes()
    
    chaoji = list(filter(lambda e: e[3] == ZiDB.SUPER, entries))

    words = CiDB.all(CiDB.SUPER)
    for ci in words:
        codes = ci2codes(ci, True, False)
        if (codes is not None):
            chaoji += codes

    extra = 100
    for entry in CiDB.fixed(CiDB.SUPER):
        code = (entry[0], entry[1], extra, 1)
        chaoji.append(code)
        extra += 1

    chaoji.sort(key=lambda e: (e[1], e[2]))

    f = open('rime/xkjd6.chaojizici.yaml', mode='w', encoding='utf-8', newline='\n')
    f.write(RIME_HEADER % 'chaojizici')

    for entry in chaoji:
        word, code, rank = entry[:3]
        if f is not None:
            f.write(word+'\t'+code+'\n')

    f.close()


# ---------------------------------
#               指令
# ---------------------------------
#
#   Human Commands
#       添加        通常/超级   字/词    全拼   编码
#       修改        通常/超级   字/词    全拼   编码
#       删除        通常/超级   字/词    全拼   编码
#       排序        通常/超级   字/词    全拼   编码
#
#   Detailed Commands
#       add_char                        char    shape   pinyin  length  weight  which
#       add_char_pinyin                 char    pinyin  length
#       remove_char_pinyin              char    set(pinyin)
#       change_char_shape               char    shape
#       change_char_shortcode_len       char    set(pinyin)  length
#       change_char_fullcode_weight     char    weight
#       add_word                        word    pinyin  length  weight  which
#       add_word_pinyin                 word    pinyin  length  weight
#       remove_word_pinyin              word    set(pinyin)
#       change_word_shortcode_len       word    set(pinyin)  length
#       change_word_shortcode_weight    word    set(pinyin)  weight
#       gen_char                        char    short   full
#       gen_word                        word    short   full
#
# ---------------------------------

def solve_char_pinyin(char, pinyin):
    zi = ZiDB.get(char)
    if zi is None:
        return set()

    sy = pinyin2sy(transform_py(pinyin))

    solved = set()

    pinyins = zi.pinyins()
    for py in pinyins:
        sy2 = pinyin2sy(py)
        if sy2 == sy:
            solved.add(py)
    
    return solved

def solve_word_pinyin(word, pinyin):
    ci = CiDB.get(word)
    if ci is None:
        return set()

    code = word_pinyin2codes(tuple(transform_py(py) for py in pinyin.split(' ')))

    solved = set()

    pinyins = ci.pinyins()
    for py in pinyins:
        code2 = word_pinyin2codes(py)
        if code2 == code:
            solved.add(py)
    
    return solved

def add_char(char, shape, pinyin, length, weight, which):
    py = transform_py(pinyin)
    ZiDB.add(char, shape, [(py, length)], weight, which)

def add_char_pinyin(char, pinyin, length):
    zi = ZiDB.get(char)
    py = transform_py(pinyin)
    assert zi is not None, '"%s" 字不存在' % char
    zi.add_pinyins([(pinyin, length)])

def remove_char_pinyin(char, pinyins):
    zi = ZiDB.get(char)
    if zi is None:
        return
    pys = set(transform_py(py) for py in pinyins)
    ZiDB.remove(char, pys)

def change_char_shape(char, shape):
    zi = ZiDB.get(char)
    assert zi is not None, '"%s" 字不存在' % char
    zi.change_shape(shape)

def change_char_shortcode_len(char, pinyins, length):
    zi = ZiDB.get(char)
    assert zi is not None, '"%s" 字不存在' % char
    pys = set(transform_py(py) for py in pinyins)
    zi.change_code_length(pys, length)

def change_char_fullcode_weight(char, weight):
    zi = ZiDB.get(char)
    assert zi is not None, '"%s" 字不存在' % char
    zi.change_rank(weight)

def check_word(word, pinyin):
    problems = []
    
    pys = tuple(transform_py(py) for py in pinyin.split(' '))
    sound = CiDB.sound_chars(word)
    if len(sound) != len(pys):
        problems.append('"%s" 词拼音 "%s" 不合法（长度不符）' % (word, " ".join(pinyin[0])))
        return problems, pys

    # check each char
    for char, pinyin in zip(word, pys):
        zi = ZiDB.get(char)
        if (zi is None):
            problems.append('"%s" 词中 "%s" 字不在字库中（请检查字型或考虑先添加此字）' % (word, char))
            continue
            
        if (pinyin not in zi.pinyins()):
            problems.append('"%s" 词中 "%s" 字没有 "%s" 音（请检查全拼或考虑先添加此音）' % (word, char, pinyin))
            continue
       
    return problems, pys

def add_word(word, pinyin, length, weight, which):
    problems, pys = check_word(word, pinyin)
    assert len(problems) == 0, "\n".join(problems)

    CiDB.add(word, [(pys, length, weight)], which)

def add_word_pinyin(word, pinyin, length, weight):
    ci = CiDB.get(word)
    assert ci is not None, '"%s" 词不存在' % word

    problems, pys = check_word(word, pinyin)
    assert len(problems) == 0, "\n".join(problems)

    ci.add_pinyins([(pys, length, weight)])

def remove_word_pinyin(word, pinyins):
    ci = CiDB.get(word)
    if ci is None:
        return
    pys = set(tuple(transform_py(py) for py in qpy.split(' ')) for qpy in pinyins)
    CiDB.remove(word, pys)

def change_word_shortcode_len(word, pinyins, length):
    ci = CiDB.get(word)
    assert ci is not None, '"%s" 词不存在' % word
    pys = set(tuple(transform_py(py) for py in qpy.split(' ')) for qpy in pinyins)
    ci.change_code_length(pys, length)

def change_word_shortcode_weight(word, pinyins, weight):
    ci = CiDB.get(word)
    assert ci is not None, '"%s" 词不存在' % word
    pys = set(tuple(transform_py(py) for py in qpy.split(' ')) for qpy in pinyins)
    ci.change_code_rank(pys, weight)

def gen_char(char, short, full):
    zi = ZiDB.get(char)
    if zi is None:
        return set()
    
    return zi2codes(zi, short, full)

def gen_word(word, short, full):
    ci = CiDB.get(word)
    if ci is None:
        return set()
    
    return ci2codes(ci, short, full)

# print(ci2codes(CiDB.get('这桩'), short = False, full = True))
# print(ci2codes(CiDB.get('这这这'), short = False, full = True))
# print(ci2codes(CiDB.get('骑着'), short = False, full = True))
# print(ci2codes(CiDB.get('服装'), short = False, full = True))
# print(ci2codes(CiDB.get('装装'), short = False, full = True))
# print(ci2codes(CiDB.get('江面'), short = False, full = True))
# print(ci2codes(CiDB.get('去装'), short = False, full = True))
# print(ci2codes(CiDB.get('车车昭'), short = False, full = True))
# print(ci2codes(CiDB.get('曲曲折折'), short = False, full = True))
# print(ci2codes(CiDB.get('转折处'), short = False, full = True))

# ZiDB.get('折').add_pinyins([("zheng", 5)])
# ZiDB.get('折').add_pinyins([("zhe", 5)])
# CiDB.get('曲曲折折').add_pinyins([(("qv","qv","she","zhe"), 100, 100)])
# print(CiDB.get('曲曲折折').weights())
# print(ZiDB.get('折').weights())

# ZiDB.commit()
# CiDB.commit()

# traverse_danzi(True)
# traverse_cizu(True, True)
# build_chaoji()

# print(ci2codes(CiDB.get('不要这样'), short = True, full = False))
# remove_word_pinyin('不要这样', {'bu yao zhe yang'})
# print(CiDB.get('不要这样'))
