import os
import sys
import JDTools
import Layout

def check(word):
    if len(word) != 2:
        return
    
    sound = JDTools.sheng(list(JDTools.get_word(word).pinyins())[0][0])
    shape = JDTools.get_char(word[1]).shape()[:2]

    if sound in ['sh', 'ch', 'zh']:
        sound = '<' + sound + '>'
    elif sound == '~':
        sound = 'x'
    else:
        sound = Layout.JD_S2K[sound]

    code = sound + '<' + shape[0] + '><' + shape[1] + '>'
    print(code)


    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Static')
    with open(os.path.join(static_path, "声笔笔.txt"), mode='r', encoding='utf-8') as infile:
        for line in infile:
            data = line.strip().split('\t')
            if (len(data) > 1 and code.startswith(data[1])):
                print(line.strip())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        quit()

    word = sys.argv[1]
    check(word)