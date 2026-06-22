"""Tests for the JDTools / ZiDB / CiDB in-memory mutation and query layer.

Run with:  python -m pytest Lambda/JDTools_test.py

These tests only mutate the in-memory databases and never call ``commit()``,
so the on-disk dictionary files are never modified. The autouse fixture calls
``JDTools.reset()`` before and after every test to keep them isolated.
"""
import pytest

from Lambda import JDTools, ZiDB, CiDB

# Placeholder characters that are not present in the shipped dictionaries.
CHAR_A = '△'
CHAR_B = '▽'
ABSENT = '▲'

# Shapes use the five JD stroke characters: 乛 丿 丨 丶 ㇐
SHAPE_A = '丶丶丶丶'
SHAPE_B = '㇐㇐㇐㇐'


@pytest.fixture(autouse=True)
def reset_dbs():
    JDTools.reset()
    yield
    JDTools.reset()


def _word_weight(word, pinyin):
    """Return (length, rank) for a word's pinyin tuple, order-independently."""
    pyt = tuple(pinyin.split(' '))
    for stored_pyt, length, rank in CiDB.get(word).weights():
        if stored_pyt == pyt:
            return length, rank
    raise AssertionError(f"{pinyin} not found for {word}")


def _setup_two_chars():
    JDTools.add_char(CHAR_A, SHAPE_A, 'shang', 4, 5)
    JDTools.add_char_pinyin(CHAR_A, 'sha', 4)
    JDTools.add_char(CHAR_B, SHAPE_B, 'xia', 4, 5)
    JDTools.add_char_pinyin(CHAR_B, 'sha', 4)


# --- single char happy paths ---

def test_add_char_and_query():
    JDTools.add_char(CHAR_A, SHAPE_A, 'shang', 4, 5)
    zi = ZiDB.get(CHAR_A)
    assert zi is not None
    assert zi.pinyins() == {'shang'}
    assert zi.weights()[0] == ('shang', 4)
    assert zi.rank() == 5
    assert zi.shape() == SHAPE_A


def test_add_and_remove_char_pinyin():
    JDTools.add_char(CHAR_A, SHAPE_A, 'shang', 4, 5)
    JDTools.add_char_pinyin(CHAR_A, 'sha', 5)
    assert ZiDB.get(CHAR_A).pinyins() == {'shang', 'sha'}
    JDTools.remove_char_pinyin(CHAR_A, {'sha'})
    assert ZiDB.get(CHAR_A).pinyins() == {'shang'}


def test_change_char_shape():
    JDTools.add_char(CHAR_A, SHAPE_A, 'shang', 4, 5)
    JDTools.change_char_shape(CHAR_A, SHAPE_B)
    assert ZiDB.get(CHAR_A).shape() == SHAPE_B


def test_change_char_shortcode_len():
    JDTools.add_char(CHAR_A, SHAPE_A, 'shang', 4, 5)
    JDTools.change_char_shortcode_len(CHAR_A, {'shang'}, 6)
    assert ZiDB.get(CHAR_A).weights()[0] == ('shang', 6)


def test_change_char_fullcode_weight():
    JDTools.add_char(CHAR_A, SHAPE_A, 'shang', 4, 5)
    JDTools.change_char_fullcode_weight(CHAR_A, 6)
    assert ZiDB.get(CHAR_A).rank() == 6


# --- word happy paths ---

def test_add_word_and_pinyin():
    _setup_two_chars()
    word = CHAR_A + CHAR_B
    JDTools.add_word(word, 'shang xia', 5, 3)
    assert CiDB.get(word).pinyins() == {('shang', 'xia')}
    assert _word_weight(word, 'shang xia') == (5, 3)
    JDTools.add_word_pinyin(word, 'shang sha', 5, 3)
    assert CiDB.get(word).pinyins() == {('shang', 'xia'), ('shang', 'sha')}


def test_remove_word_pinyin():
    _setup_two_chars()
    word = CHAR_A + CHAR_B
    JDTools.add_word(word, 'shang xia', 5, 3)
    JDTools.add_word_pinyin(word, 'shang sha', 5, 3)
    JDTools.remove_word_pinyin(word, {'shang sha'})
    assert CiDB.get(word).pinyins() == {('shang', 'xia')}


def test_change_word_shortcode_len_and_weight():
    _setup_two_chars()
    word = CHAR_A + CHAR_B
    JDTools.add_word(word, 'shang xia', 5, 3)
    JDTools.change_word_shortcode_len(word, {'shang xia'}, 6)
    assert _word_weight(word, 'shang xia') == (6, 3)
    JDTools.change_word_shortcode_weight(word, {'shang xia'}, 4)
    assert _word_weight(word, 'shang xia') == (6, 4)


# --- error / validation paths ---

def test_check_word_reports_missing_char_and_pinyin():
    JDTools.add_char(CHAR_A, SHAPE_A, 'shang', 4, 5)  # has 'shang', not 'sha'
    problems, _ = JDTools.check_word(CHAR_A + CHAR_B, 'sha xia')
    assert any(CHAR_B in p for p in problems)   # CHAR_B not in dictionary
    assert any('sha' in p for p in problems)    # CHAR_A lacks the 'sha' reading


def test_add_char_invalid_shape_raises():
    with pytest.raises(AssertionError):
        JDTools.add_char(ABSENT, 'zzzz', 'shang', 4, 5)


def test_add_char_pinyin_missing_char_raises():
    with pytest.raises(AssertionError):
        JDTools.add_char_pinyin(ABSENT, 'shang', 4)


def test_add_word_with_missing_chars_raises():
    with pytest.raises(AssertionError):
        JDTools.add_word(CHAR_A + CHAR_B, 'shang xia', 5, 3)  # chars not added
