from . import JDTools
import sys

words = []
can_add = True

with open(sys.argv[1], mode='r', encoding='utf8') as f:
    for line in f:
        if len(line.strip()) > 0:
            data = [entry.strip() for entry in line.strip().split(',')]
            if len(data) == 1:
                word = data[0]
                pinyins = JDTools.find_all_pinyin_of_word(word)
                if len(pinyins) == 1:
                    pinyin = list(pinyins)[0]
                    data.append(pinyin)
                else:
                    print("请补充拼音:", word)
                    can_add = False
            words.append(data)

if can_add:
    for word, pinyin in words:
        space_data = JDTools.find_space_for_word(word, pinyin, False)
        if space_data is None:
            print("添加失败:", word, pinyin)
            quit()

        codes, spaces, weight = JDTools.find_space_for_word(word, pinyin, False)
        length = 6
        for l in spaces:
            if len(word) == 3 and l >= 3:
                length = min(l, length)
            elif l >= 4:
                length = min(l, length)

        print("添加: %s %s (%s)" % (word, pinyin, list(codes)[0][:length]))
        if JDTools.get_word(word) is not None:
            JDTools.add_word_pinyin(word, pinyin, length, weight if length == 6 else 0)
        else:
            JDTools.add_word(word, pinyin, length, weight if length == 6 else 0)
    
    JDTools.commit()

with open(sys.argv[1], mode='w', encoding='utf8') as f:
    f.write('\n'.join([', '.join(word) for word in words]))
