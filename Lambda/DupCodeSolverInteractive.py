from . import JDTools
import os
import sys
import re
import readline
from typing import List, Tuple, Set

"""
Interactive duplicate code solver

Usage:
    python3 -m Lambda.DupCodeSolverInteractive [code_to_solve]

    code_to_solve: str, optional
        specify the code to solve, the code must be found in 词组重码报告.txt
        default to solving all codes
"""

readline.set_auto_history(True)


# read report
report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Report')
command = ""
with open(os.path.join(report_path, "词组重码报告.txt"), mode='r', encoding='utf-8') as infile:
    for line in infile:
        if line.strip() == '---':
            break

    changes: List[Tuple[str, List[str], int]] = []
    # List of args for JDTools.change_word_shortcode_len

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

        if len(sys.argv) > 1 and sys.argv[1] != code:
            continue
        
        print("Code:", code)

        dup_zh_pinyin: List[Tuple[str, List[str], str]] = []
        # [(zh word, [pinyins], full code)] for each word
        # e.g. [("拼音", ["pinyin"], "pbfbio")]
        
        for idx, word in enumerate(dups):
            priority, zh = word
            print(f"    #{idx}: {zh} ({priority})")

            possible_py: Set[str] = set(JDTools.find_word_pinyin_of_code(zh, code))
            real_py: Set[str] = {' '.join(pinyin) for pinyin in JDTools.get_word(zh).pinyins()}
            pinyins: List[str] = list(possible_py.intersection(real_py))
            # e.g. ["pin yin"]

            print(f"        working on pinyin {pinyins}[0]")
            full_codes, avail_space, full_dup = JDTools.find_space_for_word(zh, pinyins[0])
            print("       ", full_codes, "w/ avail len", avail_space)
            dup_zh_pinyin.append((zh, pinyins, full_codes[0]))
    
        # Commands
        while True:
            print("Map #x to length y: `x.y x.y x.y...`, or `save`")
            command = input(">>> ")
            if not command or command == "save":
                break
            else:
                if re.match(r"^\d\.\d( \d\.\d)*$", command):
                    steps = command.split()
                    for step in steps:
                        word_idx, target_length = map(int, step.split("."))
                        if word_idx >= len(dup_zh_pinyin) or target_length > 6 or target_length < min(4, len(dup_zh_pinyin[word_idx][0])):
                            print(f"input invalid ({step})")
                        else:
                            changes.append((dup_zh_pinyin[word_idx][0], dup_zh_pinyin[word_idx][1], target_length))
                            print("!", dup_zh_pinyin[word_idx][0], dup_zh_pinyin[word_idx][1], "->", dup_zh_pinyin[word_idx][2][:target_length])
                else:
                    print("invalid input format")                
        if command == "save":
            break

    for change in changes:
        JDTools.change_word_shortcode_len(*change)
    
JDTools.commit()