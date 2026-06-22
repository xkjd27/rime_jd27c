from . import JDTools
from . import paths
from .report_utils import iter_dup_report

changes = []

for code, dups in iter_dup_report(paths.REPORT_CIZU_DUP):
    if len(dups) == 2:
        if len(dups[0][1]) != len(dups[1][1]):
            dups.sort(key=lambda x: len(x[1]))
            word = dups[1][1]
            ci = JDTools.get_word(word)
            if ci is None:
                continue
            possible_py = set(JDTools.find_word_pinyin_of_code(word, code))
            real_py = {' '.join(pinyin) for pinyin in ci.pinyins()}
            pinyin = possible_py.intersection(real_py)
            if len(pinyin) == 0:
                continue
            space = JDTools.find_space_for_word(word, list(pinyin)[0])
            if space is None:
                continue
            min_space = 6
            for length in space[1]:
                if length > 4:
                    min_space = min(min_space, length)

            print('hit')
            changes.append((word, pinyin, min_space))
    else:
        max_len = 0
        multi = True
        target = None
        for word in dups:
            if len(word[1]) > max_len:
                max_len = len(word[1])
                multi = False
                target = word
            elif len(word[1]) == max_len:
                multi = True

        if not multi:
            print('hit 2')
            word = target[1]
            possible_py = set(JDTools.find_word_pinyin_of_code(word, code))
            ci = JDTools.get_word(word)
            if ci is None:
                print(word)
                continue
            real_py = {' '.join(pinyin) for pinyin in ci.pinyins()}
            pinyin = possible_py.intersection(real_py)
            if len(pinyin) == 0:
                continue
            space = JDTools.find_space_for_word(word, list(pinyin)[0])
            if space is None:
                continue
            min_space = 6
            for length in space[1]:
                if length > 4:
                    min_space = min(min_space, length)

            changes.append((word, pinyin, min_space))

for change in changes:
    JDTools.change_word_shortcode_len(*change)

JDTools.commit()