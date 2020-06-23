import JD6Tools

COMMAND_TRANSCRIPT = []
GENERAL = 1
SUPER = 2

# 添加单字
def command_add_char(which, char, pinyin, code):
    short_len = 6
    if ('/' in code):
        data = code.split('/')
        code = data[0]
        short_len = len(data[1])
    
    before = set(c[1] for c in (JD6Tools.gen_char(char)))

    if (JD6Tools.exists_char(char)):
        existing = JD6Tools.solve_char_pinyin(char, pinyin)
        if (len(existing) > 0):
            COMMAND_TRANSCRIPT.append('* `%s`字已有同码读音`%s`，添加操作已忽略' % (char, list(existing)[0]))
            return
        else:
            COMMAND_TRANSCRIPT.append('* 为`%s`字添加读音`%s`' % (char, pinyin))
            JD6Tools.add_char_pinyin(char, pinyin, short_len)
    else:
        shape = code[2:]
        COMMAND_TRANSCRIPT.append('* 添加新字`%s (%s, %s)`' % (char, pinyin, shape))
        weight = JD6Tools.find_weight_for_char(shape, pinyin)
        JD6Tools.add_char(char, shape, pinyin, short_len, weight, which)

    # log codes
    new_codes = set(c[1] for c in (JD6Tools.gen_char(char))).difference(before)

    if code not in new_codes:
        COMMAND_TRANSCRIPT.append('  * __提交的编码`%s`可能有误__' % code)

    new_codes = sorted(list(new_codes))
    for c in new_codes:
        COMMAND_TRANSCRIPT.append('  * `%s`' % c)

# 添加词组
def command_add_word(which, word, pinyin, code):
    short_len = len(code)
    weight = JD6Tools.find_weight_for_word(word, pinyin, short_len)

    before = set(c[1] for c in (JD6Tools.gen_word(word)))

    if (JD6Tools.exists_word(word)):
        existing = JD6Tools.solve_word_pinyin(word, pinyin)
        if (len(existing) > 0):
            COMMAND_TRANSCRIPT.append('* `%s`词已有同码读音`%s`，添加操作已忽略' % (word, list(existing)[0]))
            return
        else:
            COMMAND_TRANSCRIPT.append('* 为`%s`词添加读音`%s`' % (word, pinyin))
            JD6Tools.add_word_pinyin(word, pinyin, short_len, weight)
    else:
        shape = code[2:]
        COMMAND_TRANSCRIPT.append('* 添加新词`%s (%s)`' % (word, pinyin))
        JD6Tools.add_word(word, pinyin, short_len, weight, which)

    # log codes
    new_codes = set(c[1] for c in (JD6Tools.gen_word(word))).difference(before)

    if code not in new_codes:
        COMMAND_TRANSCRIPT.append('  * __提交的编码`%s`可能有误__' % code)

    new_codes = sorted(list(new_codes))
    for c in new_codes:
        COMMAND_TRANSCRIPT.append('  * `%s`' % c)

# 删除单字
def command_delete_char(char, pinyin):
    before = set(c[1] for c in (JD6Tools.gen_char(char)))

    all_pinyin = JD6Tools.solve_char_pinyin(char, pinyin)
    COMMAND_TRANSCRIPT.append('* 删除单字`%s (%s)`' % (char, " ".join(all_pinyin)))
    JD6Tools.remove_char_pinyin(char, all_pinyin)

    # log codes
    removed_codes = sorted(list(before.difference(set(c[1] for c in (JD6Tools.gen_char(char))))))
    for c in removed_codes:
        COMMAND_TRANSCRIPT.append('  * ~`%s`~' % c)

# 删除词组
def command_delete_word(word, pinyin):
    before = set(c[1] for c in (JD6Tools.gen_word(word)))

    all_pinyin = set(" ".join(py) for py in JD6Tools.solve_word_pinyin(word, pinyin))
    COMMAND_TRANSCRIPT.append('* 删除词组`%s (%s)`' % (word, "/".join(all_pinyin)))
    JD6Tools.remove_word_pinyin(word, all_pinyin)

    # log codes
    removed_codes = sorted(list(before.difference(set(c[1] for c in (JD6Tools.gen_word(word))))))
    for c in removed_codes:
        COMMAND_TRANSCRIPT.append('  * ~`%s`~' % c)

# 变码单字
def command_change_char(char, pinyin, code):
    short_len = 6
    change_len = False
    short_code = code
    if ('/' in code):
        data = code.split('/')
        code = data[0]
        short_code = data[1]
        short_len = len(short_code)
        change_len = True
    
    if (not JD6Tools.exists_char(char)):
         COMMAND_TRANSCRIPT.append('* 修改`%s`字' % char)
         COMMAND_TRANSCRIPT.append('  * __`%s`字不存在__' % char)
         return

    before = set(c[1] for c in (JD6Tools.gen_char(char)))

    shape = code[2:]
    if(shape != JD6Tools.get_char_shape(char)):
        if (change_len):
            COMMAND_TRANSCRIPT.append('* __无法判断`%s`字需要更改形码还是码长__' % (char))
            return
        COMMAND_TRANSCRIPT.append('* 修改`%s`字形码`(%s)`' % (char, shape))
        JD6Tools.change_char_shape(char, shape)
    else:
        change_len = True
        all_pinyin = JD6Tools.solve_char_pinyin(char, pinyin)
        COMMAND_TRANSCRIPT.append('* 修改`%s`字码长`(%s, %s)`' % (char, short_len, " ".join(all_pinyin)))
        JD6Tools.change_char_shortcode_len(char, all_pinyin, short_len)

    # log codes
    after = set(c[1] for c in (JD6Tools.gen_char(char)))
    
    minus = sorted(list(before.difference(after)))
    plus = after.difference(before)

    if (change_len and code not in before):
        COMMAND_TRANSCRIPT.append('  * __提交的编码`%s`可能有误__' % code)
    elif (len(plus) > 0 and short_code not in plus):
        COMMAND_TRANSCRIPT.append('  * __提交的编码`%s`可能有误__' % short_code)

    plus = sorted(list(plus))

    for c in minus:
        COMMAND_TRANSCRIPT.append('  * ~`%s`~' % c)
    for c in plus:
        COMMAND_TRANSCRIPT.append('  * `%s`' % c)

# 变码词组
def command_change_word(word, pinyin, code):
    short_len = len(code)

    before = set(c[1] for c in (JD6Tools.gen_word(word)))

    all_pinyin = set(" ".join(py) for py in JD6Tools.solve_word_pinyin(word, pinyin))
    COMMAND_TRANSCRIPT.append('* 修改`%s`词码长`(%s, %s)`' % (word, short_len, " ".join(all_pinyin)))
    JD6Tools.change_word_shortcode_len(word, all_pinyin, short_len)

    # log codes
    after = set(c[1] for c in (JD6Tools.gen_word(word)))
    
    minus = sorted(list(before.difference(after)))
    plus = after.difference(before)

    if (len(plus) > 0 and code not in plus):
        COMMAND_TRANSCRIPT.append('  * __提交的编码`%s`可能有误__' % code)

    plus = sorted(list(plus))

    for c in minus:
        COMMAND_TRANSCRIPT.append('  * ~`%s`~' % c)
    for c in plus:
        COMMAND_TRANSCRIPT.append('  * `%s`' % c)

# 添加指令
def command_add(which, command):
    if len(command) < 3:
        COMMAND_TRANSCRIPT.append('* __`添加 %s`指令不合法__' % ' '.join(command))
        return

    word = command[0].strip()
    pinyin = command[1].strip()
    code = command[2].strip()
    
    if (len(word) == 1):
        command_add_char(which, word, pinyin, code)
    else:
        command_add_word(which, word, pinyin, code)

# 删除指令
def command_delete(which, command):
    if len(command) < 2:
        COMMAND_TRANSCRIPT.append('* __`删除 %s`指令不合法__' % ' '.join(command))
        return

    word = command[0].strip()
    pinyin = command[1].strip()
    if (len(word) == 1):
        command_delete_char(word, pinyin)
    else:
        command_delete_word(word, pinyin)

# 变码指令
def command_change(which, command):
    if len(command) < 3:
        COMMAND_TRANSCRIPT.append('* __`变码 %s`指令不合法__' % ' '.join(command))
        return

    word = command[0].strip()
    pinyin = command[1].strip()
    code = command[2].strip()
    
    if (len(word) == 1):
        command_change_char(word, pinyin, code)
    else:
        command_change_word(word, pinyin, code)

# 排序单字
def command_rank_char(char, pinyin, code, rank):
    COMMAND_TRANSCRIPT.append('* 更改`%s`字候选序`(%s)`' % (char, code))
    codes = set(c[1] for c in (JD6Tools.gen_char(char)))
    if (code not in codes):
        COMMAND_TRANSCRIPT.append('  * __`%s %s`码不存在__' % (char, code))
        return

    target = JD6Tools.get_char(char)
    involved = JD6Tools.get_zi_of_code(code)
    involved.remove(target)

    if (len(involved) == 0):
        return
    
    involved = [(e.rank(), e) for e in involved]
    involved.sort(key=lambda e: e[0])

    moveUpFrom = None

    if (rank > len(involved)):
        weight = involved[-1][1].rank() + 1
        COMMAND_TRANSCRIPT.append('  * `%s`字权值 -> %d' % (char, weight))
        JD6Tools.change_char_fullcode_weight(char, weight)
        return
    if (rank <= 1):
        weight = involved[0][1].rank() - 1
        if (weight >= 0):
            COMMAND_TRANSCRIPT.append('  * `%s`字权值 -> %d' % (char, weight))
            JD6Tools.change_char_fullcode_weight(char, weight)
            return
        else:
            weight = 0
            COMMAND_TRANSCRIPT.append('  * `%s`字权值 -> %d' % (char, weight))
            JD6Tools.change_char_fullcode_weight(char, weight)
            moveUpFrom = 0
    else:
        index = rank - 1
        weight_after = involved[index][1].rank()
        weight_before = involved[index-1][1].rank()
        weight = weight_before + 1
        COMMAND_TRANSCRIPT.append('  * `%s`字权值 -> %d' % (char, weight))
        JD6Tools.change_char_fullcode_weight(char, weight)
        if (weight < weight_after):
            return
        else:
            moveUpFrom = index

    weight += 1
    if (moveUpFrom is not None):
        for i in range(moveUpFrom, len(involved)):
            char = involved[i][1].char()
            weight_char = involved[i][1].rank()
            if (weight_char > weight):
                break
            COMMAND_TRANSCRIPT.append('  * `%s`字权值 -> %d' % (char, weight))
            JD6Tools.change_char_fullcode_weight(char, weight)
            weight += 1

# 排序词组
def command_rank_word(word, pinyin, code, rank):
    COMMAND_TRANSCRIPT.append('* 更改`%s`词候选序`(%s)`' % (word, code))
    codes = set(c[1] for c in (JD6Tools.gen_word(word)))
    if (code not in codes):
        COMMAND_TRANSCRIPT.append('  * __`%s`码不存在__' % (word))
        return

    all_pinyins = set(" ".join(py) for py in JD6Tools.solve_word_pinyin(word, pinyin))
    target = JD6Tools.get_word(word)
    involved = JD6Tools.get_ci_of_code(code)
    involved.remove(target)

    if (len(involved) == 0):
        return
    
    involved = [(e.get_rank_of(all_pinyins), e) for e in involved]
    involved.sort(key=lambda e: e[0])

    moveUpFrom = None

    if (rank > len(involved)):
        weight = involved[-1][0] + 1
        COMMAND_TRANSCRIPT.append('  * `%s`词权值 -> %d' % (word, weight))
        JD6Tools.change_word_shortcode_weight(word, all_pinyins, weight)
        return
    if (rank <= 1):
        weight = involved[0][0] - 1
        if (weight >= 0):
            COMMAND_TRANSCRIPT.append('  * `%s`词权值 -> %d' % (word, weight))
            JD6Tools.change_word_shortcode_weight(word, all_pinyins, weight)
            return
        else:
            weight = 0
            COMMAND_TRANSCRIPT.append('  * `%s`词权值 -> %d' % (word, weight))
            JD6Tools.change_word_shortcode_weight(word, all_pinyins, weight)
            moveUpFrom = 0
    else:
        index = rank - 1
        weight_after = involved[index][0]
        weight_before = involved[index-1][0]
        weight = weight_before + 1
        COMMAND_TRANSCRIPT.append('  * `%s`词权值 -> %d' % (word, weight))
        JD6Tools.change_word_shortcode_weight(word, all_pinyins, weight)
        if (weight < weight_after):
            return
        else:
            moveUpFrom = index

    weight += 1
    if (moveUpFrom is not None):
        for i in range(moveUpFrom, len(involved)):
            word = involved[i][1].word()
            weight_word = involved[i][0]
            if (weight_word > weight):
                break
            all_pinyins = set(" ".join(py) for py in JD6Tools.solve_word_pinyin(word, pinyin))
            COMMAND_TRANSCRIPT.append('  * `%s`词权值 -> %d' % (word, weight))
            JD6Tools.change_word_shortcode_weight(word, all_pinyins, weight)
            weight += 1

# 排序指令
def command_rank(which, command):
    code_part = command[2].split('#')

    if len(command) < 3 or len(code_part) < 2 or not code_part[1].isdigit():
        COMMAND_TRANSCRIPT.append('* __`排序 %s`指令不合法__' % ' '.join(command))
        return

    word = command[0].strip()
    pinyin = command[1].strip()
    code = code_part[0]
    rank = int(code_part[1])
    
    if (len(word) == 1):
        command_rank_char(word, pinyin, code, rank)
    else:
        command_rank_word(word, pinyin, code, rank)

def process_commands(commands):
    for command in commands:
        if (len(command) < 2):
            continue
        
        which = GENERAL if command[0] == '通常' else SUPER
        cmd_name = command[1]
        print(" - Processing: %s" % str(command))
        try:
            if cmd_name == '添加':
                command_add(which, command[2:])
            elif cmd_name == '删除':
                command_delete(which, command[2:])
            elif cmd_name == '变码':
                command_change(which, command[2:])
            elif cmd_name == '排序':
                command_rank(which, command[2:])
            else:
                COMMAND_TRANSCRIPT.append('* __`%s`指令不合法__' % ' '.join(command[1:]))
                return
        except AssertionError as e:
            COMMAND_TRANSCRIPT.append('  * __%s__' % str(e))
    
    JD6Tools.commit()

# command_add(1, ('正', 'zheng', 'srimwov'))
# command_add(1, ('正', 'zhe', 'srimwov'))
# command_add(1, ('A', 'zheng', 'srooiv'))

# command_add(1, ('执着', 'zhi zhuo', 'fkfw'))
# command_add(1, ('执着', 'zhi zhe', 'fkfw'))
# command_add(1, ('AA', 'zheng zheng', 'fkfw'))

# command_delete(1, ('AA', 'zheng zheng'))
# command_delete(1, ('A', 'zheng'))

# command_change(1, ('籽', 'zi', 'zkouai/zkab'))
# command_change(1, ('籽', 'zi', 'zkouai/zkou'))
# command_change(1, ('籽', 'zi', 'zkouai/zkoua'))
# command_change(1, ('籽', 'zi', 'zkouau'))
# command_change(1, ('籽', 'zi', 'zkouai/zkou'))

# command_add(1, ('反选', 'fan xuan', 'ffxt'))
# command_change(1, ('反旋', 'fan xuan', 'ffxtu'))

# command_change(1, ('方方正正', 'fang fang zheng zheng', 'ffqq'))

# command_rank(1, ('籽', 'zi', 'zkouai#2'))
# command_rank(1, ('籽', 'zi', 'zkouai#1'))

# command_rank(1, ('郑板桥', 'zhun bei zhe', 'qbqo#2'))

# command_rank(1, ('找删', 'zhao shan', 'fzef#2'))
# command_rank(1, ('初试', 'chu shi', 'jjekoo#1'))

# process_commands([])
# print(COMMAND_TRANSCRIPT)