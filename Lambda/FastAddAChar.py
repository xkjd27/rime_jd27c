import JDTools
import Commands
import sys

char = "觍" # sys.argv[1]
shape = "iaia" # sys.argv[2]
pinyin = "tian" # sys.argv[3]

space_data = JDTools.find_space_for_char(shape, pinyin)
codes, spaces, weight = space_data
length = min(spaces)
print(length, spaces)
zi = JDTools.get_char(char)

if zi is not None:
    shape = zi.shape()
    JDTools.add_char_pinyin(char, pinyin, length)
else:
    shape = ''.join([JDTools.JD_B_R[s] for s in shape])
    JDTools.add_char(char, shape, pinyin, length, weight)

JDTools.commit()