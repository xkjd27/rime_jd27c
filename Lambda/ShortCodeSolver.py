import JDTools
import os
import re

def solve_cizu():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Report/词组优化报告.txt')

    short_space = {}
    with open(file_path, mode='r', encoding='utf-8') as f:
        for line in f:
            match = re.search('可缩码："(.*)" (.*) -> (.*) \((.*)\)', line)
            word = match[1]
            code = match[2].strip()
            short = match[3].strip()
            pinyin = match[4]

            if (short in short_space):
                short_space[short].append((word, pinyin))
            else:
                short_space[short] = [(word, pinyin)]

    for short in short_space:
        data = short_space[short]
        if len(data) == 1:
            if (JDTools.get_word(data[0][0]) is not None):
                print('hit')
                JDTools.change_word_shortcode_len(data[0][0], { data[0][1] }, len(short))
        # else:
        #     min_len = 99
        #     multi = True
        #     target = None
        #     for word in data:
        #         if len(word[0]) < min_len:
        #             min_len = len(word[0])
        #             multi = False
        #             target = word
        #         elif len(word[0]) == min_len:
        #             multi = True

        #     if (not multi):
        #         print('hit 2')
        #         JDTools.change_word_shortcode_len(target[0], { target[1] }, len(short))
        else:
            print(short)
            i = 1
            for word in data:
                print("%d. %s" % (i, word))
                i += 1

            sel = input("choose: ")
            if (sel.isdigit() and int(sel) <= len(data) and int(sel) > 0):
                sel = int(sel) - 1
                JDTools.change_word_shortcode_len(data[sel][0], { data[sel][1] }, len(short))
            else:
                break

def solve_danzi():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Report/单字健康报告.txt')

    short_space = {}
    with open(file_path, mode='r', encoding='utf-8') as f:
        for line in f:
            match = re.search('可缩码："(.*)" (.*) -> (.*) \((.*)\)', line)
            if match is None:
                continue
            
            word = match[1]
            code = match[2].strip()
            short = match[3].strip()
            pinyin = match[4]

            if (short in short_space):
                short_space[short].append((word, pinyin))
            else:
                short_space[short] = [(word, pinyin)]

    for short in short_space:
        data = short_space[short]
        if len(data) == 1:
            print('hit')
            JDTools.change_char_shortcode_len(data[0][0], { data[0][1] }, len(short))
        else:
            print(short)
            i = 1
            for word in data:
                print("%d. %s" % (i, word))
                i += 1

            sel = input("choose: ")
            if (sel.isdigit() and int(sel) <= len(data) and int(sel) > 0):
                sel = int(sel) - 1
                JDTools.change_char_shortcode_len(data[sel][0], { data[sel][1] }, len(short))
            else:
                break

solve_cizu()
JDTools.commit()