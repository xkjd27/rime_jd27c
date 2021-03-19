import JDTools
import sys
import itertools

sys.stdout.reconfigure(encoding='utf-8')

cis = JDTools.get_all_ci()

sbb = {}

for ci in cis:
    if len(ci.word()) == 2:
        s = JDTools.pinyin2s(list(ci.pinyins())[0][0])
        b = JDTools.s(JDTools.get_char(ci.word()[1]).shape())[:2]
        code = s[0]+b
        if code in sbb:
            sbb[code].append(ci.word())
        else:
            sbb[code] = [ci.word()]

for code, value in sorted(sbb.items()):
    print(code)
    
    for i in range(0, len(value), 10):
        print("\t" + ",".join(value[i:i+10]))

    print()