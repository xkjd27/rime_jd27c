import CiDB
import ZiDB
from JD6Tools import *

add_char('△', 'aaaa', 'shang', 4, 5, ZiDB.GENERAL)
assert ZiDB.get('△').pinyins() == {'shang'}
assert ZiDB.get('△').weights()[0][1] == 4
assert ZiDB.get('△').rank() == 5
assert ZiDB.get('△').shape() == 'aaaa'

add_char_pinyin('△', 'sha', 5)
assert ZiDB.get('△').pinyins() == {'shang', 'sha'}
assert ZiDB.get('△').weights()[1][1] == 5

remove_char_pinyin('△', {'sha'})
assert ZiDB.get('△').pinyins() == {'shang'}

change_char_shape('△', 'uuuu')
assert ZiDB.get('△').shape() == 'uuuu'

change_char_shortcode_len('△', {'shang'}, 6)
assert ZiDB.get('△').weights()[0][1] == 6

change_char_fullcode_weight('△', 6)
assert ZiDB.get('△').rank() == 6

p, _ = check_word('△▽', 'sha xia')
assert p[1] == '"△▽" 词中 "▽" 字不在字库中（请检查字型或考虑先添加此字）'
assert p[0] == '"△▽" 词中 "△" 字没有 "sha" 音（请检查全拼或考虑先添加此音）'

add_char('▽', 'vvvv', 'xia', 4, 5, ZiDB.GENERAL)
add_char_pinyin('▽', 'sha', 4)

add_word('△▽', 'shang xia', 5, 3, CiDB.GENERAL)
assert CiDB.get('△▽').pinyins() == {('shang', 'xia')}
assert CiDB.get('△▽').weights()[0][1] == 5
assert CiDB.get('△▽').weights()[0][2] == 3

add_word_pinyin('△▽', 'shang sha', 5, 3)
assert CiDB.get('△▽').pinyins() == {('shang', 'xia'), ('shang', 'sha')}
assert CiDB.get('△▽').weights()[1][1] == 5
assert CiDB.get('△▽').weights()[1][2] == 3

remove_word_pinyin('△▽', { 'shang sha' })
assert CiDB.get('△▽').pinyins() == {('shang', 'xia')}

change_word_shortcode_len('△▽', { 'shang xia' }, 6)
assert CiDB.get('△▽').weights()[0][1] == 6, CiDB.get('△▽').weights()

change_word_shortcode_weight('△▽', { 'shang xia' }, 4)
assert CiDB.get('△▽').weights()[0][2] == 4, CiDB.get('△▽').weights()

print(gen_char('△', True, True))
print(gen_word('△▽', True, False))
