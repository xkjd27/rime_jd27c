import sys
import os
import ZiDB
import CiDB
import itertools

# ---------------------------------
#             布局定义
# ---------------------------------

# 键道6 声母->键
JD_S2K = {
    'q': ['q'],
    'w': ['w'],
    'r': ['r'],
    't': ['t'],
    'y': ['r'],
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
    'zh': [';'],
    'ch': ['y'],
    'sh': ['e'],
    '~': ['x'],
}

# 键道6 韵母->键
JD_Y2K = {
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
    'v': [';'],
    'o': ['l'],
    'ao': ['z'],
    'iang': ['x'],
    'uang': ['x'],
    'iao': ['c'],
    'in': ['b'],
    'ui': ['b'],
    'en': ['n'],
    'ian': ['m'],
}

# ---------------------------------
#               常量
# ---------------------------------

RIME_HEADER = '# 由键道：涵自动生成\n---\nname: %s\nversion: "q2"\nsort: original\n...\n'

# 拼音变体转换表
PY_TRANSFORM = {
    'qve': 'que',
    'lve': 'lue',
    'jve': 'jue',
    'xve': 'xue',
    'yve': 'yue',
    'm': 'en',
    'ng': 'eng',
}

# 特殊声母表
PY_SHENG = {
    'a': '~',
    'ai': '~',
    'an': '~',
    'ang': '~',
    'ao': '~',
    'e': '~',
    'ei': '~',
    'en': '~',
    'eng': '~',
    'er': '~',
    'o': '~',
    'ou': '~',
}

# 特殊韵母表
PY_YUN = {
    'ya': 'ia', 
    'yan': 'ian', 
    'yang': 'iang',
    'yao': 'iao',
    'ye': 'ie',
    'yong': 'iong',
    'you': 'yiu',
    'ju': 'v',
    'qu': 'v',
    'xu': 'v',
    'yu': 'v',
    'a': 'a',
    'ai': 'ai',
    'an': 'an',
    'ang': 'ang',
    'ao': 'ao',
    'e': 'e',
    'ei': 'ei',
    'en': 'en',
    'eng': 'eng',
    'er': 'er',
    'o': 'o',
    'ou': 'ou',
}

# ---------------------------------
#             辅助函数
# ---------------------------------

def sheng(py):
    """取全拼声母"""
    if (py in PY_SHENG):
        return PY_SHENG[py]
    if py.startswith('zh'):
        return 'zh'
    if py.startswith('ch'):
        return 'ch'
    if py.startswith('sh'):
        return 'sh'
    return py[0]

def yun(py):
    """取全拼韵母"""
    if (py in PY_YUN):
        return PY_YUN[py]
    if py.startswith('zh') or py.startswith('ch') or py.startswith('sh'):
        return py[2:]
    return py[1:]

def pinyin2sy(py):
    """全拼转双拼"""
    if len(py) < 1:
        return []

    shengmu = sheng(py)
    yunmu = yun(py)

    if (shengmu not in JD_S2K or yunmu not in JD_Y2K):
        return []

    s = JD_S2K[shengmu]
    y = JD_Y2K[yunmu]

    sy = []
    for ss in s:
        for yy in y:
            sy.append(ss+yy)

    return sy

def pinyin2s(py):
    """全拼转声拼"""
    shengmu = sheng(py)
    
    s = JD_S2K[shengmu]

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

def char2codes(shape, pinyin, length, short = True, full = True):
    sy = [code for code in pinyin2sy(transform_py(pinyin))]
    if (len(sy) == 0):
        return set()

    codes = set()

    for sound in sy:
        full_code = sound+shape
    
        if (length < len(full_code)):
            if (length > 1 and short):
                codes.add(full_code[:length])
        
        if full:
            codes.add(full_code)
    
    return codes

def zi2codes(zi, short = True, full = True):
    codes = []
    sy_codes = {}

    weights = zi.weights()
    for w in weights:
        sy = [code for code in pinyin2sy(w[0])]
        if (len(sy) == 0):
            continue

        sy = sy[0]
        if sy in sy_codes:
            sy_codes[sy] = (min(sy_codes[sy][0], w[1]), w[0])
        else:
            sy_codes[sy] = (w[1], w[0])

    b = zi.shape()
    char = zi.char()
    rank = zi.rank()
    which = zi.which()

    for sy in sy_codes:
        w, pinyin = sy_codes[sy]
        full_code = sy+b

        if (w <= 0):  # 忽略无理读音
            continue
    
        if (w < len(full_code)):
            has_short = True
            if (short):
                codes.append((char, full_code[:w], rank, which, True, pinyin))
        else:
            has_short = False
        
        if full:
            codes.append((char, full_code, rank, which, not has_short, pinyin))
    
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
        code = (entry[0], entry[1], -1, entry[2], None, '')
        _entries.append(code)
        if (code[1] in _entries_r):
            _entries_r[code[1]].append(code)
        else:
            _entries_r[code[1]] = [code]

    _entries.sort(key=lambda e: (e[1], e[2]))
    return _entries, _entries_r

def get_cizu_codes():
    """获取词组码表"""
    
    global _word_entries
    global _word_entries_r

    try:
        _word_entries
    except:
        _word_entries = None

    try:
        _word_entries_r
    except:
        _word_entries_r = None

    if (_word_entries == None or _word_entries_r == None):
        _word_entries = []
        _word_entries_r = {}
    else:
        return _word_entries, _word_entries_r

    words = CiDB.all(CiDB.GENERAL)
    for ci in words:
        codes = ci2codes(ci, True, False)
        if (codes is not None):
            _word_entries += codes
            for code in codes:
                if (code[1] in _word_entries_r):
                    _word_entries_r[code[1]].append(code)
                    _word_entries_r[code[1]].sort(key=lambda e: (e[1], e[2]))
                else:
                    _word_entries_r[code[1]] = [code]
        else:
            CiDB.remove(ci.word(), ci.pinyins())

    # 固定词组
    extra = 500
    for entry in CiDB.fixed(CiDB.GENERAL):
        code = (entry[0], entry[1], extra, '')
        _word_entries.append(code)
        if (code[1] in _word_entries_r):
            _word_entries_r[code[1]].append(code)
            _word_entries_r[code[1]].sort(key=lambda e: (e[1], e[2]))
        else:
            _word_entries_r[code[1]] = [code]

        extra += 1

    _word_entries.sort(key=lambda e: (e[1], e[2]))
    return _word_entries, _word_entries_r 

def clear_danzi_codes():
    """Dirtify单字码表"""
    global _entries
    global _entries_r

    try:
        del _entries
        _entries = None
    except:
        _entries = None

    try:
        del _entries_r
        _entries_r = None
    except:
        _entries_r = None

def clear_cizu_codes():
    """Dirtify词组码表"""
    global _word_entries
    global _word_entries_r

    try:
        del _word_entries
        _word_entries = None
    except:
        _word_entries = None

    try:
        del _word_entries_r
        _word_entries_r = None
    except:
        _word_entries_r = None

def word_pinyin2codes(pys):
    """词拼音转声码"""
    if len(pys) <= 2:
        # 二字词
        og_codes = set("".join(wordpy) for wordpy in itertools.product(*[pinyin2sy(py) for py in pys]))
        codes = set()

        for code in og_codes:
            codes.add(code)
    else:
        # 多字词
        og_codes = set("".join(wordpy) for wordpy in itertools.product(*[pinyin2s(py) for py in pys]))
        codes = set()

        for code in og_codes:
            codes.add(code)
    
    
    return set(code for code in codes)

def word2codes(word, pinyin, length, short = True, full = False):
    sound_chars = CiDB.sound_chars(word)

    if len(sound_chars) < 2: # 一字词（非法）无视
        return set()

    py_codes = word_pinyin2codes(tuple(transform_py(py) for py in pinyin.split(' ')))

    first_char = ZiDB.get(sound_chars[0])
    second_char = ZiDB.get(sound_chars[1])

    if (first_char is None or second_char is None):
        return set()

    shape = first_char.shape()[0] + second_char.shape()[0]
    if len(sound_chars) == 3: # 三字词需三码
        third_char = ZiDB.get(sound_chars[2])
        if (third_char is None):
            return set()
        shape += third_char.shape()[0]
            
    codes = set()
    for code in py_codes:
        full_code = code + shape
        if (full):
            codes.add(full_code)
        if (short):
            short_code = full_code[:length]
            codes.add(short_code)
            
    return codes

def ci2codes(ci, short = True, full = False):
    """生成词6码"""
    sound_chars = ci.sound_chars()

    if len(sound_chars) == 1: # 一字词（非法）无视
        return None

    py_codes = {}
    weights = ci.weights()

    first_char = ZiDB.get(sound_chars[0])
    second_char = ZiDB.get(sound_chars[1])

    if (first_char is None or second_char is None):
        return None

    shape = first_char.shape()[0] + second_char.shape()[0]
    if len(sound_chars) == 3: # 三字词需三码
        third_char = ZiDB.get(sound_chars[2])
        if (third_char is None):
            return set()
        shape += third_char.shape()[0]

    for data in weights:
        pinyin, shortcode_len, rank = data
        s_codes = word_pinyin2codes(pinyin)

        for code in s_codes:
            if code in py_codes:
                py_codes[code] = (min(shortcode_len, py_codes[code][0]), max(rank, py_codes[code][1]), " ".join(pinyin))
            else:
                py_codes[code] = (shortcode_len, rank, " ".join(pinyin))
            
    codes = set()
    for code in py_codes:
        full_code = code + shape
        shortcode_len, rank, pinyin = py_codes[code]
        if (full):
            codes.add((ci.word(), full_code, rank, pinyin))
        if (short):
            short_code = full_code[:shortcode_len]
            codes.add((ci.word(), short_code, rank, pinyin))
            
    return codes

# ---------------------------------
#             码表生成
# ---------------------------------
def traverse_danzi(build = False, report = True):
    """遍历单字码表"""
    entries, codes = get_danzi_codes() 

    last_code = ''

    rank_check = [
        None,
        ('', '', -2),
        ('', '', -2),
    ]

    dups = []

    if build:
        danzi = open('rime/xkjd27.danzi.dict.yaml', mode='w', encoding='utf-8', newline='\n')
        danzi.write(RIME_HEADER % 'xkjd27.danzi')
    else:
        danzi = None

    if report:
        report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Report/单字健康报告.txt')
        report = open(report_path, mode='w', encoding='utf-8', newline='\n')
    else:
        report = None

    for entry in entries:
        char, code, rank, which, is_shortest, pinyin = entry

        if which != ZiDB.GENERAL and which != ZiDB.SUPER:
            continue

        if report:
            # 检查重码
            if (len(code) < 6):
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
            if (is_shortest):
                sc = code[:-1]

                avaliable_short = None
                substitute = None
                while True:
                    if (len(sc) < 1):
                        break
                
                    if sc in codes:
                        if (codes[sc][0][3] == ZiDB.SUPER and which == ZiDB.GENERAL):
                            substitute = codes[sc][0][0]
                            avaliable_short = sc
                    else:
                        substitute = None
                        avaliable_short = sc

                    sc = sc[:-1]

                if (avaliable_short is not None):
                    if (substitute is not None):
                        report.write('可替换："%s" %6s -> %6s (替换超级字 "%s")\n' % (char, code, avaliable_short, substitute))
                    else:
                        report.write('可缩码："%s" %6s -> %6s (%s) | %s\n' % (char, code, avaliable_short, pinyin, ('通常' if which == ZiDB.GENERAL else '超级')))

        last_code = code

        rank_check[which] = (code, char, rank)

        if danzi is not None and which == ZiDB.GENERAL:
            danzi.write(char+'\t'+code+'\n')
    
    if (report and len(dups) > 1):
        report.write('重码：%6s %s\n' % (last_code, str(dups)))

    if (danzi is not None):
        danzi.close()

    if report is not None:
        report.write('检查完毕\n')
        report.close()

def traverse_cizu(build = False, report = True):
    """遍历词组码表"""
    # dup_code_check = {}
    last_rank = -1
    entries, dup_code_check = get_cizu_codes()

    if build:
        f = open('rime/xkjd27.cizu.dict.yaml', mode='w', encoding='utf-8', newline='\n')
        f.write(RIME_HEADER % 'xkjd27.cizu')
    else:
        f = None

    if report:
        report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Report/词组优化报告.txt')
        optimize = open(report_path, mode='w', encoding='utf-8', newline='\n')
    else:
        optimize = None

    for entry in entries:
        word, code, rank, pinyin = entry
        word_len = len(CiDB.sound_chars(word))

        if f is not None:
            f.write(word+'\t'+code+'\n')

        if report:
            # 简码空间检查
            sc = code[:-1]

            avaliable_short = None
            while True:
                continue_next = True
                if sc in dup_code_check:
                    continue_next = False
                elif word_len == 3 and len(sc) < 3:
                    # 3字词不能短于3码
                    continue_next = False
                elif word_len != 3 and len(sc) < 4:
                    # 其他词不能短于4码
                    continue_next = False
            
                if not continue_next:
                    if (avaliable_short is not None):
                        optimize.write('可缩码："%s" %6s -> %6s (%s)\n' % (word, code, avaliable_short, pinyin))
                    break
                
                avaliable_short = sc
                sc = sc[:-1]

    # 所有重码数量
    dup_count = [0,0,0,0]

    # 不包括6重码的重码数量
    lose_dup_count = [0,0,0,0]

    # 允许重码的宽容码
    code_dup_lose_flag = set()

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
            if dup_code_check[code][1][2] >= 100 and dup_code_check[code][0][2] != dup_code_check[code][1][2]:
                code_dup_lose_flag.add(code)
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
            
            for word in dups:
                f.write('\t%d\t%s\n' % (word[2], word[0]))
        
            f.write('\n')

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
        else:
            CiDB.remove(ci.word(), ci.pinyins())

    extra = 500
    for entry in CiDB.fixed(CiDB.SUPER):
        code = (entry[0], entry[1], extra, 1, '')
        chaoji.append(code)
        extra += 1

    chaoji.sort(key=lambda e: (e[1], e[2]))

    f = open('rime/xkjd27.chaojizici.dict.yaml', mode='w', encoding='utf-8', newline='\n')
    f.write(RIME_HEADER % 'xkjd27.chaojizici')

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

def exists_char(char):
    return ZiDB.get(char) is not None

def exists_word(word):
    return CiDB.get(word) is not None

def get_char_shape(char):
    zi = ZiDB.get(char)
    if zi is None:
        return ""
    
    return ZiDB.get(char).shape()

def get_char(char):
    return ZiDB.get(char)

def get_word(word):
    return CiDB.get(word)

def get_zi_of_code(code):
    _, lookup = get_current_danzi_codes()
    result = set()
    if code in lookup:
        for parts in lookup[code]:
            zi = ZiDB.get(parts[0])
            if (zi is not None):
                result.add(zi)

    return result

def get_ci_of_code(code):
    _, lookup = get_current_cizu_codes()
    result = set()
    if code in lookup:
        for parts in lookup[code]:
            ci = CiDB.get(parts[0])
            if (ci is not None):
                result.add(ci)
        
    return result

danzi_dirty = False
cizu_dirty = False

def cizu_mark_dirty():
    global cizu_dirty
    cizu_dirty = True

def danzi_mark_dirty():
    global danzi_dirty
    danzi_dirty = True

def get_current_danzi_codes():
    global danzi_dirty
    if danzi_dirty:
        clear_danzi_codes()
        clear_cizu_codes()
        danzi_dirty = False
        cizu_dirty = False

    entries, lookup = get_danzi_codes()
    return entries, lookup

def get_current_cizu_codes():
    global cizu_dirty
    if cizu_dirty:
        clear_cizu_codes()
        cizu_dirty = False

    entries, lookup = get_cizu_codes()
    return entries, lookup

def solve_char_pinyin(char, pinyin):
    zi = ZiDB.get(char)
    if zi is None:
        return set()

    sy = set(pinyin2sy(transform_py(pinyin)))

    solved = set()

    pinyins = zi.pinyins()
    for py in pinyins:
        sy2 = set(pinyin2sy(py))
        if len(sy2.intersection(sy)) > 0:
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
        if len(code2.intersection(code)) > 0:
            solved.add(py)
    
    return solved

def add_char(char, shape, pinyin, length, weight, which):
    py = transform_py(pinyin)
    zi = ZiDB.add(char, shape, [(py, length)], weight, which)

    codes = gen_char(char)

    danzi_mark_dirty()

def add_char_pinyin(char, pinyin, length):
    zi = ZiDB.get(char)
    py = transform_py(pinyin)
    assert zi is not None, '`%s`字不存在' % char
    zi.add_pinyins([(pinyin, length)])
    danzi_mark_dirty()

def remove_char_pinyin(char, pinyins):
    zi = ZiDB.get(char)
    if zi is None:
        return
    pys = set(transform_py(py) for py in pinyins)
    ZiDB.remove(char, pys)
    danzi_mark_dirty()

def change_char_shape(char, shape):
    zi = ZiDB.get(char)
    assert zi is not None, '`%s`字不存在' % char
    zi.change_shape(shape)
    danzi_mark_dirty()

def change_char_shortcode_len(char, pinyins, length):
    zi = ZiDB.get(char)
    assert zi is not None, '`%s`字不存在' % char
    pys = set(transform_py(py) for py in pinyins)
    zi.change_code_length(pys, length)
    danzi_mark_dirty()

def change_char_fullcode_weight(char, weight):
    zi = ZiDB.get(char)
    assert zi is not None, '`%s`字不存在' % char
    zi.change_rank(weight)
    danzi_mark_dirty()

def check_word(word, pinyin):
    problems = []
    
    pys = tuple(transform_py(py) for py in pinyin.split(' '))
    sound = CiDB.sound_chars(word)
    if len(sound) != len(pys):
        problems.append('`%s`词拼音`%s`不合法(长度不符)' % (word, pinyin))
        return problems, pys

    # check each char
    for char, pinyin in zip(sound, pys):
        zi = ZiDB.get(char)
        if (zi is None):
            problems.append('`%s`词中`%s`字不在字库中(请检查字型或考虑先添加此字)' % (word, char))
            continue
            
        if (pinyin not in zi.pinyins()):
            problems.append('`%s`词中`%s`字没有`%s`音(请检查全拼或考虑先添加此读音)' % (word, char, pinyin))
            continue
       
    return problems, pys

def add_word(word, pinyin, length, weight, which):
    problems, pys = check_word(word, pinyin)
    assert len(problems) == 0, "\n".join(problems)

    ci = CiDB.add(word, [(pys, length, weight)], which)

    codes = gen_word(word)

    cizu_mark_dirty()

def add_word_pinyin(word, pinyin, length, weight):
    ci = CiDB.get(word)
    assert ci is not None, '`%s`词不存在' % word

    problems, pys = check_word(word, pinyin)
    assert len(problems) == 0, "\n".join(problems)

    ci.add_pinyins([(pys, length, weight)])
    cizu_mark_dirty()

def remove_word_pinyin(word, pinyins):
    ci = CiDB.get(word)
    if ci is None:
        return
    pys = set(tuple(transform_py(py) for py in qpy.split(' ')) for qpy in pinyins)
    CiDB.remove(word, pys)
    cizu_mark_dirty()

def change_word_shortcode_len(word, pinyins, length):
    ci = CiDB.get(word)
    assert ci is not None, '`%s`词不存在' % word
    pys = set(tuple(transform_py(py) for py in qpy.split(' ')) for qpy in pinyins)
    ci.change_code_length(pys, length)
    cizu_mark_dirty()

def change_word_shortcode_weight(word, pinyins, weight):
    ci = CiDB.get(word)
    assert ci is not None, '`%s`词不存在' % word
    pys = set(tuple(transform_py(py) for py in qpy.split(' ')) for qpy in pinyins)
    ci.change_code_rank(pys, weight)
    cizu_mark_dirty()

def find_word_shortcode_weight(word, pinyins):
    ci = CiDB.get(word)
    assert ci is not None, '`%s`词不存在' % word
    pys = set(tuple(transform_py(py) for py in qpy.split(' ')) for qpy in pinyins)
    ci.change_code_rank(pys, weight)

def gen_char(char, short = True, full = True):
    zi = ZiDB.get(char)
    if zi is None:
        return set()
    
    return zi2codes(zi, short, full)

def gen_word(word, short = True, full = False):
    ci = CiDB.get(word)
    if ci is None:
        return set()
    
    result = ci2codes(ci, short, full)
    if (result is None):
        return set()
    return result

def find_weight_for_char(shape, pinyin):
    codes = char2codes(shape, pinyin, 6, False, True)
    _, lookup = get_danzi_codes()
    weight = 0
    for code in codes:
        if code in lookup:
            for char in lookup[code]:
                weight = max(weight, char[2] + 1)

    return weight

def find_weight_for_word(word, pinyin, length):
    codes = word2codes(word, pinyin, length, True, False)
    _, lookup = get_cizu_codes()
    weight = 0
    for code in codes:
        if code in lookup:
            for word in lookup[code]:
                weight = max(weight, word[2] + 1)
                
    return weight

def find_space_for_word(word, pinyin):
    codes = list(word2codes(word, pinyin, 6, False, True))
    if len(codes) == 0:
        return None
    
    short = [code[:-1] for code in codes]
    _, lookup = get_current_cizu_codes()

    full_dup = 0
    for code in codes:
        full_dup = max(len(lookup[code]) if code in lookup else 0, full_dup)

    avaliable_spaces = [6]
    for i in range(5, 2, -1):
        avaliable = True
        for code in short:
            if code in lookup:
                avaliable = False
                break
        
        if (avaliable):
            avaliable_spaces.append(i)
        short = [code[:-1] for code in short]

    return (codes, avaliable_spaces, full_dup)

def find_space_for_char(shape, pinyin):
    codes = list(char2codes(shape, pinyin, 6, False, True))
    if len(codes) == 0:
        return None

    full_code_len = max(len(codes[0]), 6)
    
    short = [code[:-1] for code in codes]
    _, lookup = get_current_danzi_codes()

    full_dup = 0
    for code in codes:
        full_dup = max(len(lookup[code]) if code in lookup else 0, full_dup)

    avaliable_spaces = [full_code_len]
    for i in range(full_code_len-1, 1, -1):
        avaliable = True
        for code in short:
            if code in lookup:
                avaliable = False
                break
        
        if (avaliable):
            avaliable_spaces.append(i)
        short = [code[:-1] for code in short]

    return (codes, avaliable_spaces, full_dup)

def sound_chars(word):
    return CiDB.sound_chars(word)

def build_static():
    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Static')

    STAITC_MAP = {
        '声笔笔.txt': 'xkjd27.sbb',
        '补充.txt': 'xkjd27.buchong',
    }

    for static in STAITC_MAP:
        with open("rime/%s.dict.yaml" % STAITC_MAP[static], mode='w', encoding='utf-8', newline='\n') as outfile:
            outfile.write(RIME_HEADER % STAITC_MAP[static])
            with open(os.path.join(static_path, static), mode='r', encoding='utf-8') as infile:
                outfile.write('\n'.join(line.strip() for line in infile.readlines()))

def find_all_pinyin_of_word(word):
    sound = sound_chars(word)
    parts = []
    for char in sound:
        zi = ZiDB.get(char)
        if zi is None:
            return []
        parts.append(list(zi.pinyins()))
    
    return [" ".join(pinyin) for pinyin in itertools.product(*parts)]

def find_word_pinyin_of_code(word, code):
    sound = CiDB.sound_chars(word)
    is_sy = len(sound) == 2
    sound_code = code[:3] if len(sound) == 3 else code[:4]

    pinyins = find_all_pinyin_of_word(word)

    possible = []
    for pinyin in pinyins:
        codes = word_pinyin2codes(pinyin.split(' '))
        if sound_code in codes:
            possible.append(pinyin)

    return possible

def get_all_zi():
    return ZiDB.all()

def get_all_ci():
    return CiDB.all(CiDB.GENERAL)

def commit():
    """提交所有更改并生成新码表"""
    clear_danzi_codes()
    clear_cizu_codes()
    ZiDB.commit()
    CiDB.commit()
    traverse_danzi(True, True)
    traverse_cizu(True, True)
    build_chaoji()
    build_static()

def reset():

    ZiDB.reset()
    CiDB.reset()
    clear_danzi_codes()
    clear_cizu_codes()

if __name__ == '__main__':
    commit()