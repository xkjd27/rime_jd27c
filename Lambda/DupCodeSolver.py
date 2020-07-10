import JDTools
import os
import re

# read report
report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Report')
with open(os.path.join(report_path, "词组重码报告.txt"), mode='r', encoding='utf-8') as infile:
    for line in infile:
        if line.strip() == '---':
            break

    changes = []

    while True:
        line = infile.readline()
        if len(line.strip()) == 0 or line.strip() == '---':
            break
        
        code = line.strip()
        dups = []
        data = infile.readline().strip()
        while len(data) > 0:
            dups.append(data.split('\t'))
            data = infile.readline().strip()
        
        # if (len(dups) == 2):
        #     if (len(dups[0][1]) != len(dups[1][1])):
        #         dups.sort(key=lambda x: len(x[1]))
        #         word = dups[1][1]
        #         pinyin = set(JDTools.find_word_pinyin_of_code(word, code)).intersection({' '.join(pinyin) for pinyin in JDTools.get_word(word).pinyins()})
        #         space = JDTools.find_space_for_word(word, list(pinyin)[0])
        #         min_space = 6
        #         for length in space[1]:
        #             if length > 4:
        #                 min_space = min(min_space, length)

        #         changes.append((word, pinyin, min_space))
            # else:
            #     print(code)
            #     i = 1
            #     for word in dups:
            #         print("%d. %s" % (i, word[1]))
            #         i += 1

            #     sel = input("choose: ")
            #     if (sel.isdigit() and int(sel) <= len(dups) and int(sel) > 0):
            #         sel = int(sel) - 1
            #         word = dups[sel][1]
            #         pinyin = set(JDTools.find_word_pinyin_of_code(word, code)).intersection({' '.join(pinyin) for pinyin in JDTools.get_word(word).pinyins()})
            #         space = JDTools.find_space_for_word(word, list(pinyin)[0])
            #         min_space = 6
            #         for length in space[1]:
            #             if length > 4:
            #                 min_space = min(min_space, length)

            #         changes.append((word, pinyin, min_space))
            #     else:
            #         break
        for dup in dups:
            word = dup[1]
            pinyin = set(JDTools.find_word_pinyin_of_code(word, code)).intersection({' '.join(pinyin) for pinyin in JDTools.get_word(word).pinyins()})
            changes.append((word, pinyin, 6))

    for change in changes:
        JDTools.change_word_shortcode_len(*change)
    
JDTools.commit()