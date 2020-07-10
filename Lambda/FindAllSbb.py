import JDTools
import sys
import itertools

sys.stdout.reconfigure(encoding='utf-16')

cis = JDTools.get_all_ci()

sbb = {}

for ci in cis:
    if len(ci.word()) == 2:
        s = JDTools.pinyin2s(list(ci.pinyins())[0][0])
        b = JDTools.get_char(ci.word()[1]).shape()[:2].replace('e', 'u')
        code = JDTools.unmarkfly(s[0])+b
        if code in sbb:
            sbb[code].append(ci.word())
        else:
            sbb[code] = [ci.word()]

for code in sbb:
    print(code)
    
    for i in range(0, len(sbb[code]), 10):
        print("\t" + ",".join(sbb[code][i:i+10]))

    print()