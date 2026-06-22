from . import JDTools
import sys

char = sys.argv[1]
shape = sys.argv[2]
pinyin = sys.argv[3]

space_data = JDTools.find_space_for_char(shape, pinyin)
if space_data is None:
    print("添加失败:", char, pinyin)
    quit()

codes, spaces, weight = space_data
length = min(spaces)
print(length, spaces)
zi = JDTools.get_char(char)

if zi is not None:
    JDTools.add_char_pinyin(char, pinyin, length)
else:
    shape = ''.join([JDTools.JD_B_R[s] for s in shape])
    JDTools.add_char(char, shape, pinyin, length, weight)

JDTools.commit()