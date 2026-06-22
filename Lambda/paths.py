"""Centralized filesystem paths for the Lambda dictionary build tool.

Two anchors are used, matching the historical behaviour of the code base:

- ``PACKAGE_DIR`` anchors data that ships with the package (``Report/``,
  ``Static/``, ``ZiDB/``, ``CiDB/``). These were previously resolved with
  ``os.path.dirname(os.path.abspath(__file__))``.
- Generated outputs (``rime/``, ``log_input/``, ``fcitx5/``) are resolved
  relative to the current working directory, i.e. the repository root the
  build/bot is launched from.
"""
import os

from .Layout import RIME_SCHEMA

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Bundled data directories (package-relative) ---
REPORT_DIR = os.path.join(PACKAGE_DIR, 'Report')
STATIC_DIR = os.path.join(PACKAGE_DIR, 'Static')
ZIDB_DIR = os.path.join(PACKAGE_DIR, 'ZiDB')
CIDB_DIR = os.path.join(PACKAGE_DIR, 'CiDB')

# Report files
REPORT_DANZI = os.path.join(REPORT_DIR, '单字健康报告.txt')
REPORT_CIZU_OPTIMIZE = os.path.join(REPORT_DIR, '词组优化报告.txt')
REPORT_CIZU_DUP = os.path.join(REPORT_DIR, '词组重码报告.txt')
REPORT_CIZU_ALLOWED = os.path.join(REPORT_DIR, '容许重码记录.txt')

# Bundled data files
REFUSE_FILE = os.path.join(CIDB_DIR, '拒绝.txt')
SBB_FILE = os.path.join(STATIC_DIR, '声笔笔.txt')

# --- Generated output locations (CWD / repo-root relative) ---
RIME_DIR = 'rime'
LOG_INPUT_DIR = 'log_input'
FCITX5_DIR = 'fcitx5'

# User dictionary (lives under rime/, dot-prefixed)
USER_DICT_NAME = 'xkjd27c.user.dict.yaml'
USER_DICT_FILE = os.path.join(RIME_DIR, '.' + USER_DICT_NAME)

# Generated table outputs
RIME_DICT_PATH = os.path.join(RIME_DIR, RIME_SCHEMA + '.%s.dict.yaml')
LOG_INPUT_FILE = os.path.join(LOG_INPUT_DIR, RIME_SCHEMA + '.txt')
FCITX5_TXT = os.path.join(FCITX5_DIR, RIME_SCHEMA + '.txt')
FCITX5_DICT = os.path.join(FCITX5_DIR, RIME_SCHEMA + '.dict')
