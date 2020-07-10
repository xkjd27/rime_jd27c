import JD6Tools
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
        
        if (len(dups) == 2):
            if (dups[0][1] == '\u3000' and dups[1][1] == '\u3000'):
                if (len(dups[0][2]) != len(dups[1][2])):
                    dups.sort(key=lambda x: len(x[2]))
                    word = dups[1][2]
                    pinyin = set(JD6Tools.find_word_pinyin_of_code(word, code)).intersection(JD6Tools.get_word(word).pinyins())
                    
                    space = JD6Tools.find_space_for_word(word, list(pinyin)[0])
                    min_space = 6
                    for length in space[1]:
                        if length > 4:
                            min_space = min(min_space, length)

                    changes.append((word, pinyin, min_space))

    for change in changes:
        JD6Tools.change_word_shortcode_len(*change)
    
JD6Tools.commit()