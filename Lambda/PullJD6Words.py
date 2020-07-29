import JDTools
import urllib.request
import sys
import os

refuse_list = set()

static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CiDB')
with open(os.path.join(static_path, "拒绝.txt"), mode='r', encoding='utf-8') as infile:
    for line in infile:
        refuse_list.add(line.strip())

jd6_words = set()
jdc_words = set(ci.word() for ci in JDTools.get_all_ci())

with urllib.request.urlopen('https://raw.githubusercontent.com/xkinput/Rime_JD/master/Tools/TermsTools/cizu.txt') as f:
    data = f.read().decode('utf-8')
    lines = data.split('\n')
    for line in lines:
        line = line.strip()
        if '\t' in line:
            word = line.split('\t')[0]
            jd6_words.add(word)

jd6_diff = jd6_words.difference(jdc_words).difference(refuse_list)


print("键道6多出来的词：")
print("\n".join(sorted(jd6_diff)))

if len(sys.argv) > 1:
    jdc_diff = jdc_words.difference(jd6_words).difference(refuse_list)
    print()
    print("键道C多出来的词：")
    print("\n".join(sorted(jdc_diff)))