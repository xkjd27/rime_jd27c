from dotenv import load_dotenv
import os
from . import JDTools
from . import Commands
import re
from bisect import bisect_left
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode
from typing import List, Dict
from git import Repo
import urllib.request
import time
from azure.core.credentials import AccessToken
from msal import ConfidentialClientApplication, SerializableTokenCache
from msgraph import GraphServiceClient

load_dotenv()

# Microsoft Graph API Setup
AZURE_TENANT_ID = "9188040d-6c67-4c5b-b112-36a304b66dad"
AZURE_CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
AZURE_CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]
AZURE_REDIRECT_URI = os.environ["AZURE_REDIRECT_URI"]
GRAPH_SCOPES = ['https://graph.microsoft.com/.default']

class MSALCredential:
    def __init__(self, session_name):
        self.session_name = session_name
        self.cache = SerializableTokenCache()
        cache_file = f"token_cache_{session_name}.bin"
        if os.path.exists(cache_file):
            self.cache.deserialize(open(cache_file, "r").read())
        self.app = ConfidentialClientApplication(
            client_id=AZURE_CLIENT_ID,
            client_credential=AZURE_CLIENT_SECRET,
            authority=f"https://login.microsoftonline.com/{AZURE_TENANT_ID}",
            token_cache=self.cache
        )

    def get_authorization_url(self, scopes):
        app = self.app
        result = app.acquire_token_for_client(scopes)
        if "error" in result:
            raise Exception(f"{result}")

        flow = app.initiate_auth_code_flow(scopes=scopes, redirect_uri=AZURE_REDIRECT_URI)

        if "error" in flow:
            raise Exception(f"{flow}")

        return flow["auth_uri"], flow
    
    def process_auth_response_url(self, auth_resp_url, flow):
        app = self.app
        # parse query string into dict
        auth_resp_url = auth_resp_url.split("?")[1]
        auth_resp = dict(q.split("=") for q in auth_resp_url.split("&"))

        try:
            result = app.acquire_token_by_auth_code_flow(flow, auth_resp)
            
            if "access_token" in result:
                return result
            else:
                raise Exception(f"{result}")
        except ValueError:  # Usually caused by CSRF
            pass  # Simply ignore them
    
    def get_token(
        self,
        *scopes: str,
        claims = None,
        tenant_id = None,
        enable_cae: bool = False,
        **kwargs
    ):
        result = None
        app = self.app

        scopes = list(scopes)

        accounts = app.get_accounts()
        if accounts:
            result = app.acquire_token_silent(scopes, account=accounts[0])

        if not result:
            _, flow = self.get_authorization_url(scopes)

            auth_resp_url = input("Redirect URL: ")
            result = self.process_auth_response_url(auth_resp_url, flow)
        
        if result:
            with open(f"token_cache_{self.session_name}.bin", "w") as f:
                f.write(self.cache.serialize())

        return AccessToken(result["access_token"], result["expires_in"] + time.time())

# Initialize Graph API clients
graph_sessions = {}
session_names = ["session"] # , "session.tsfreddie"]

for name in session_names:
    credential = MSALCredential(name)
    client = GraphServiceClient(credentials=credential, scopes=GRAPH_SCOPES)
    graph_sessions[name] = {
        "credential": credential,
        "client": client,
    }

ALLOWED_USER = set(os.environ['TELEGRAM_BOT_USER'].split(','))

LOG_STATUS: List[str] = []

def LOG(result: List[str]):
    global LOG_STATUS
    LOG_STATUS += result

def CLEAN(text: str) -> str:
    return (
        text.replace('*', r'')
            .replace('__', r'*')
            .replace('~`', r' =|=')
            .replace('`~', r'=|= ')
            .replace('~', r'')
            .replace('=|=', r'~')
            .replace('(', r'\(')
            .replace(')', r'\)')
            .replace('`', r' ')
            .replace('-', r'\-')
            .replace('>', r'\>')
            .replace('<', r'\<')
            .replace('.', r'\.')
    )

def MARK(result: List[str]) -> List[str]:
    res = []
    for line in result:
        res.append(CLEAN(line))

    return res

async def TYPING(update: Update):
    await update.message.chat.send_action(action=ChatAction.TYPING)

async def REPLY(update: Update, text: str, parse_mode=ParseMode.HTML):
    await update.message.reply_text(text=text, reply_markup=ReplyKeyboardRemove(), parse_mode=parse_mode)

async def CHOOSE(update: Update, text: str, choice: List[str], parse_mode=ParseMode.MARKDOWN_V2):
    await update.message.reply_text(text=text, reply_markup=ReplyKeyboardMarkup(
        [choice, ['/取消']], one_time_keyboard=True), parse_mode=parse_mode)

# Help
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username not in ALLOWED_USER:
        return
    
    await update.message.reply_text(text="""指令列表:
/add - 添加字词
/delete - 删除字词
/change - 修改字词
/rank - 字词排序
/list - 查看字词在码表的位置
/status - 查看当前修改
/drop - 放弃当前的修改
/pull - 从 Github 同步更新
/push - 保存并上传
/getjd - 获取键道6的新词
/user_add - 添加用户词
/user_delete - 删除用户词
""")

# Fallback
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await REPLY(update, "操作已取消")
    return -1

# Commands
CUSTOM_DICT = {}
CUSTOM_DICT_R = {}
def load_custom():
    CUSTOM_DICT.clear()
    if os.path.isfile('./rime/.xkjd27c.user.dict.yaml'):
        with open('./rime/.xkjd27c.user.dict.yaml', mode='r', encoding='utf-8') as infile:
            for line in infile:
                if (line.strip().startswith('#')):
                    continue
                data = line.strip().split('\t')
                if (len(data) != 2):
                    continue
                CUSTOM_DICT[data[0]] = data[1]
                CUSTOM_DICT_R[data[1]] = data[0]

load_custom()

def add_custom(word, code):
    if word in CUSTOM_DICT:
        del CUSTOM_DICT_R[CUSTOM_DICT[word]]
        del CUSTOM_DICT[word]

    if code in CUSTOM_DICT_R:
        return f"{CLEAN(code)} 编码已经存在（{CLEAN(CUSTOM_DICT_R[code])}）"
    
    CUSTOM_DICT[word] = code
    CUSTOM_DICT_R[code] = word

def save_custom():
    with open('./rime/.xkjd27c.user.dict.yaml', mode='w', encoding='utf-8', newline='\n') as outfile:
        data = sorted(list(CUSTOM_DICT_R.items()))
        outfile.write('# coding: utf-8\n---\nname: xkjd27c.user\nversion: "q2"\nsort: original\n...\n')
        for line in data:
            outfile.write(f"{line[1]}\t{line[0]}\n")

def remove_custom(info):
    try:
        if info in CUSTOM_DICT:
            del CUSTOM_DICT_R[CUSTOM_DICT[info]]
            del CUSTOM_DICT[info]
        elif info in CUSTOM_DICT_R:
            del CUSTOM_DICT[CUSTOM_DICT_R[info]]
            del CUSTOM_DICT_R[info]
        else:
            return f"{info} 词条不存在"
    except:
        return None

async def save_user_dict_to_onedrive(update) -> int:
    """Return -1 when failed, None when success.
    """
    for session_name, session in graph_sessions.items():
        client = session["client"]
        try:
            # Read the file content
            with open('./rime/.xkjd27c.user.dict.yaml', 'rb') as upload_file:
                file_content = upload_file.read()

            # Upload file using Graph API
            drive_item = client.me.drive.root.item_by_path(os.environ['ONEDRIVE_PATH'] + '/xkjd27c.user.dict.yaml').content.upload(file_content)
            await REPLY(update, f"成功添加并更新到 OneDrive @ {session_name}", parse_mode=None)
        except Exception as e:
            import traceback
            await REPLY(update, f"OneDrive @ {session_name} 上传失败: \n{e}\n{traceback.format_exc()}", ParseMode.HTML)
            return -1

async def user_add(update, context):
    if update.effective_user.username not in ALLOWED_USER:
        return -1

    data = update.message.text

    if (data.startswith('/')):
        data = update.message.text.strip().split(' ')
        if len(data) > 1:
            word = ' '.join(data[1:])
            with update.message._unfrozen():
                update.message.text = word
            return await user_add(update, context)
        else:
            await REPLY(update, "请输入要添加的词条")
            return 13
    elif 'adding_custom' not in context.user_data:
        context.user_data['adding_custom'] = data
        await REPLY(update, "正在添加自定词条词：%s，请提供编码" % data)
        return 13
    else:
        result = add_custom(context.user_data['adding_custom'], data)
        if result is not None:
            await REPLY(update, result)
            return -1
        else:
            save_custom()
            upload_outcome = await save_user_dict_to_onedrive(update)
            if upload_outcome is not None:
                return upload_outcome
            
            context.user_data.clear()
            return -1

    await REPLY(update, "未知错误")
    context.user_data.clear()
    return -1

async def user_delete(update, context):
    if update.effective_user.username not in ALLOWED_USER:
        return -1

    data = update.message.text

    if (data.startswith('/')):
        data = update.message.text.strip().split(' ')
        if len(data) > 1:
            word = ' '.join(data[1:])
            with update.message._unfrozen():
                update.message.text = word
            return await user_delete(update, context)
        else:
            await REPLY(update, "请输入要删除的词条/编码")
            return 14
    else:
        result = remove_custom(data)
        if result is not None:
            await REPLY(update, result)
            return -1
        else:
            save_custom()

            upload_outcome = save_user_dict_to_onedrive(update)
            if upload_outcome is not None:
                return upload_outcome

            context.user_data.clear()
            return -1

    await REPLY(update, "未知错误")
    context.user_data.clear()
    return -1

# Commands
async def add(update, context):
    if update.effective_user.username not in ALLOWED_USER:
        return -1

    data = update.message.text.strip().split(' ')
    if len(data) > 1:
        word = ' '.join(data[1:])
        with update.message._unfrozen():
            update.message.text = word
        if (len(word) > 1):
            return await add_word(update, context)
        else:
            return await add_char(update, context)

    await REPLY(update, "请输入要添加的字/词")
    return 0

async def delete(update, context):
    if update.effective_user.username not in ALLOWED_USER:
        return -1

    data = update.message.text.strip().split(' ')
    if len(data) > 1:
        word = ' '.join(data[1:])
        with update.message._unfrozen():
            update.message.text = word
        if (len(word) > 1):
            return await delete_word(update, context)
        else:
            return await delete_char(update, context)

    await REPLY(update, "请输入要删除的字/词")
    return 3

async def change(update, context):
    if update.effective_user.username not in ALLOWED_USER:
        return -1

    data = update.message.text.strip().split(' ')
    if len(data) > 1:
        word = ' '.join(data[1:])
        with update.message._unfrozen():
            update.message.text = word
        if (len(word) > 1):
            return await change_word(update, context)
        else:
            return await change_char(update, context)
        
    await REPLY(update, "请输入要修改的字/词")
    return 6

async def rank(update, context):
    if update.effective_user.username not in ALLOWED_USER:
        return -1

    data = update.message.text

    if 'rank_requested' not in context.user_data:
        context.user_data['rank_requested'] = True
        data = data.strip().split(' ')
        if (len(data) <= 1):
            await REPLY(update, "请输入要排序的编码")
            return 9
        data = ' '.join(data[1:])
    
    if 'rank_code' not in context.user_data:
        context.user_data['rank_code'] = data

        await TYPING(update)

        zis = JDTools.get_zi_of_code(data)
        if len(zis) == 0:
            cis = JDTools.get_ci_of_code(data)
            if (len(cis) == 0):
                await REPLY(update, "没有该编码")
                context.user_data.clear()
                return -1
            elif len(cis) == 1:
                await REPLY(update, "编码无重码")
                context.user_data.clear()
                return -1
            else:
                context.user_data['rank_type'] = 'word'
                await CHOOSE(update, "请选择需要提权的词", [ci.word() for ci in cis])
        elif len(zis) == 1:
            await REPLY(update, "编码无重码")
            context.user_data.clear()
            return -1
        else:
            context.user_data['rank_type'] = 'char'
            await CHOOSE(update, "请选择需要提权的字", [zi.char() for zi in zis])
    elif 'rank_word' not in context.user_data:
        context.user_data['rank_word'] = data
        code = context.user_data['rank_code']
        rank_type = context.user_data['rank_type']

        await TYPING(update)

        if (rank_type == 'word'):
            ci = JDTools.get_word(data)
            if ci is None:
                await REPLY(update, "未知错误")
                context.user_data.clear()
                return -1

            codes = list(filter(lambda c : c[1] == code, JDTools.ci2codes(ci)))
            if (len(codes) == 0):
                await REPLY(update, "未知错误")
                context.user_data.clear()
                return -1

            context.user_data['rank_pinyin'] = codes[0][-2]
            await CHOOSE(update, "确定要提升 %s 词 (%s) 至首位吗" % (data, code), ['是的'])
        else:
            zi = JDTools.get_char(data)
            if zi is None:
                await REPLY(update, "未知错误")
                context.user_data.clear()
                return -1

            codes = list(filter(lambda c : c[1] == code, JDTools.zi2codes(zi)))
            if (len(codes) == 0):
                await REPLY(update, "未知错误")
                context.user_data.clear()
                return -1

            context.user_data['rank_pinyin'] = codes[0][-1]
            await CHOOSE(update, "确定要提升 %s 字全码（%s）至首位吗" % (data, code), ['是的'])
    else:
        word = context.user_data['rank_word']
        pinyin = context.user_data['rank_pinyin']
        code = context.user_data['rank_code']
        rank_type = context.user_data['rank_type']

        await TYPING(update)

        if (rank_type == 'word'):
            result = Commands.safe_rank_word(word, pinyin, code, 1)
        else:
            result = Commands.safe_rank_char(word, pinyin, code, 1)

        await REPLY(update, "\n".join(MARK(result)))
        context.user_data.clear()

        LOG(result)

        return -1

    return 9

async def status(update, context):
    if update.effective_user.username not in ALLOWED_USER:
        return -1

    if (len(LOG_STATUS) == 0):
        await REPLY(update, "无变化")
        return -1
    await REPLY(update, "\n".join(MARK(LOG_STATUS)))
    return -1

async def pull(update, context):
    if update.effective_user.username not in ALLOWED_USER:
        return -1

    if (len(LOG_STATUS) > 0):
        await REPLY(update, "\n".join(MARK(LOG_STATUS)))
        await REPLY(update, '有未提交修改，请先 push 或 drop 当前修改')
        return -1

    await TYPING(update)
    repo = Repo('.').git
    await REPLY(update, 'pull 完成 %s' % repo.pull(), ParseMode.HTML)
    JDTools.reset()
    return -1
    
async def push(update, context):
    if update.effective_user.username not in ALLOWED_USER:
        return -1

    if 'requested_code' not in context.user_data:
        await REPLY(update, '正在构建，请稍候...')

        await TYPING(update)
        
        try:
            JDTools.commit()

            repo = Repo('.').git

            changes = repo.status('--porcelain').strip()
            if (len(changes) > 0):
                repo.add('-A')
                repo.commit(m=f"更新码表\n{'\n'.join(LOG_STATUS)}")
                repo.push()

                await REPLY(update, '构建完毕，push 成功')
            else:
                await REPLY(update, '构建完毕，码表无改动')

            LOG_STATUS.clear()
        except Exception as e:
            await REPLY(update, '构建失败')
            raise e
            return -1

        await TYPING(update)
        
        for session_name, session in graph_sessions.items():
            client = session["client"]
            try:
                # Upload files using Graph API
                for filename in ['xkjd27c.cizu.dict.yaml', 'xkjd27c.danzi.dict.yaml', 'xkjd27c.chaojizici.dict.yaml', 'xkjd27c.txt']:
                    file_path = './rime/' + filename if not filename.endswith('.txt') else './log_input/' + filename
                    with open(file_path, 'rb') as upload_file:
                        file_content = upload_file.read()
                    drive_item = client.me.drive.items.item_by_path(os.environ['ONEDRIVE_PATH'] + '/' + filename).content.upload(file_content)
                await REPLY(update, f"OneDrive @ {session_name} 上传成功", parse_mode=None)
            except Exception as e:
                import traceback
                await REPLY(update, f"OneDrive @ {session_name} 上传失败: \n{e}\n{traceback.format_exc()}", ParseMode.HTML)

    return -1

def binary_search(arr, low, high, x): 
    if high >= low: 
        mid = (high + low) // 2
        if arr[mid][1] == x: 
            return mid 
        elif arr[mid][1] > x: 
            return binary_search(arr, low, mid - 1, x) 
        else: 
            return binary_search(arr, mid + 1, high, x) 
    else: 
        return -1

async def list_code(data, code, update):
    index = binary_search(data, 0, len(data), code)
    if (index > 0):
        start = min(len(data) - 5, max(index - 2, 0))
        result = []
        for i in range(max(start, 0), min(start + 5, len(data))):
            if i == index:
                result.append(f"->{data[i][1].ljust(8)}{data[i][0]}")
            else:
                result.append(f"  {data[i][1].ljust(8)}{data[i][0]}")
        await REPLY(update, f"```\n{'\n'.join(result)}\n```")
        return True
    return False

async def list_command(update, context):
    if update.effective_user.username not in ALLOWED_USER:
        return -1

    if 'list_requested' not in context.user_data:
        data = update.message.text.split(' ')
        context.user_data['list_requested'] = True

        if len(data) > 1:
            word = ' '.join(data[1:])
            with update.message._unfrozen():
                update.message.text = word
            return await list_command(update, context)

        await REPLY(update, "请输入要查找的字/词/编码")
    else:
        await TYPING(update)
        data = update.message.text
        printed = False
        if re.search('^[a-z;]{1,6}$', data):
            zi_entries, _ = JDTools.get_current_danzi_codes()
            ci_entries, _ = JDTools.get_current_cizu_codes()
            printed = await list_code(zi_entries, data, update) or await list_code(ci_entries, data, update) or printed
        else:
            if len(data) == 1:
                codes = JDTools.gen_char(data)
                for code in codes:
                    zi_entries, _ = JDTools.get_current_danzi_codes()
                    printed = await list_code(zi_entries, code[1], update) or printed
            else:
                codes = JDTools.gen_word(data)
                for code in codes:
                    ci_entries, _ = JDTools.get_current_cizu_codes()
                    printed = await list_code(ci_entries, code[1], update) or printed
        
        if not printed:
            await REPLY(update, '找不到编码')
        context.user_data.clear()
        return -1
    
    return 10

async def drop(update, context):
    if update.effective_user.username not in ALLOWED_USER:
        return -1

    if 'drop_requested' not in context.user_data:
        context.user_data['drop_requested'] = True

        if (len(LOG_STATUS) == 0):
            await REPLY(update, "无变化")
            return -1
        
        await REPLY(update, "\n".join(MARK(LOG_STATUS)))

        await CHOOSE(update, "确定要放弃所有修改吗", ['是的'])
        return 11
    else:
        context.user_data.clear()
        LOG_STATUS.clear()
        JDTools.reset()
        await REPLY(update, "所有修改已还原")
        return -1

async def add_word(update, context):
    data = update.message.text

    if 'adding_word' not in context.user_data:
        context.user_data['adding_word'] = data
        await REPLY(update, f"正在添加词：{data}，请提供编码")
        return 1

    elif 'adding_word_wanted' not in context.user_data:
        word = context.user_data['adding_word']
        code = data.strip()
        context.user_data['adding_word_wanted'] = code

        pinyins = JDTools.find_word_pinyin_of_code(word, code)
        if (len(pinyins) == 0):
            await REPLY(update, "无法添加，可能音码有误")
            context.user_data.clear()
            return -1

        if (len(pinyins) == 1):
            with update.message._unfrozen():
                update.message.text = pinyins[0]
            return await add_word(update, context)
        
        if (len(pinyins) > 4):
            await REPLY(update, "无法确定读音，请提供全拼读音")
        else:
            await CHOOSE(update, "请选择一个拼音", pinyins)

    elif 'adding_word_pinyin' not in context.user_data:
        pinyin = data.strip()
        word = context.user_data['adding_word']
        wanted_code = context.user_data['adding_word_wanted']
        context.user_data['adding_word_pinyin'] = pinyin

        await TYPING(update)

        ci = JDTools.get_word(word)
        if (ci is not None and tuple(pinyin.split(' ')) in ci.pinyins()):
            await REPLY(update, "该词已有拼音（%s），已取消操作。" % pinyin)
            context.user_data.clear()
            return -1

        space_data = JDTools.find_space_for_word(word, pinyin)
        if space_data is None:
            await REPLY(update, "未知错误")
            context.user_data.clear()
            return -1

        codes, spaces, dup = space_data
        
        wanted_correct = False
        for code in codes:
            if code.startswith(wanted_code):
                wanted_correct = True
        
        if not wanted_correct:
            fix_code = codes[0][:len(wanted_code)]
            await REPLY(update, "提供的编码笔码（%s）可能有误\n已自动修正为: %s" % (wanted_code, fix_code))
            wanted_code = fix_code
        
        min_recommend = 6
        for space in spaces:
            if len(word) == 3 or space > 3:
                min_recommend = min(min_recommend, space)

        if min_recommend > len(wanted_code) and min_recommend == 6:
            await REPLY(update, "您提供的编码可能有重码，只有6码空间可用，6 码有 %d 重码。" % (dup))
        elif min_recommend > len(wanted_code):
            await REPLY(update, "您提供的编码可能有重码，推荐使用 %d 码。" % (min_recommend))
        elif min_recommend < len(wanted_code):
            await REPLY(update, "该词可以使用更短的 %d 码。" % (min_recommend))
        else:
            with update.message._unfrozen():
                update.message.text = wanted_code
            return await add_word(update, context)

        await CHOOSE(update, "请确认想要的码长", [wanted_code, codes[0][:min_recommend]])

    elif 'adding_word_code' not in context.user_data:
        context.user_data['adding_word_code'] = data.strip('*')
        word = context.user_data['adding_word']
        pinyin = context.user_data['adding_word_pinyin']
        code = context.user_data['adding_word_code']

        await REPLY(update, "添加 %s 词\n拼音：%s\n编码：%s" % (word, pinyin, code))
        await CHOOSE(update, "确定要添加吗", ['是的'])
    else:
        word = context.user_data['adding_word']
        pinyin = context.user_data['adding_word_pinyin']
        code = context.user_data['adding_word_code']

        await TYPING(update)

        continue_change = JDTools.get_ci_of_code(code)

        result = Commands.safe_add_word(word, pinyin, code)
        await REPLY(update, "\n".join(MARK(result)))
        context.user_data.clear()

        LOG(result)

        if continue_change is not None and len(continue_change) > 0:
            await CHOOSE(update, "是否要修改 %s 码词？" % code, ["/change " + ci.word() for ci in continue_change])

        return -1

    return 1

async def add_char(update, context):
    data = update.message.text

    if 'adding_char' not in context.user_data:
        context.user_data['adding_char'] = data
        await REPLY(update, f"正在添加字：{data}，请提供拆字")
        return 2

    elif 'adding_char_shape' not in context.user_data:
        context.user_data['adding_char_shape'] = JDTools.code2shape(data)
        await REPLY(update, "请提供拼音")

    elif 'adding_char_pinyin' not in context.user_data:
        context.user_data['adding_char_pinyin'] = data
        shape = context.user_data['adding_char_shape']
        
        await TYPING(update)
        
        space_data = JDTools.find_space_for_char(JDTools.s(shape), data)
        if space_data is None:
            await REPLY(update, "无法添加")
            context.user_data.clear()
            return -1
    
        codes, spaces, dup = space_data
        context.user_data['adding_char_fullcode'] = codes[0]

        await REPLY(update, f"全码：{str(codes)}\n可用码长：{str(spaces)}\n全码重码：{dup}")
        await CHOOSE(update, "请选择一个码长（推荐\\*）", [f"{codes[0][:i]}{'*' if i in spaces else ''}" for i in range(2, 7)])
    
    elif 'adding_char_code' not in context.user_data:
        context.user_data['adding_char_code'] = data.strip('*')
        
        char = context.user_data['adding_char']
        pinyin = context.user_data['adding_char_pinyin']
        code = context.user_data['adding_char_code']
        fullcode = context.user_data['adding_char_fullcode']

        await REPLY(update, f"添加 {char} 字（{fullcode if fullcode != code else f'{fullcode}/{code}'}）")
        await CHOOSE(update, "确定要添加吗", ['是的'])

    else:
        char = context.user_data['adding_char']
        pinyin = context.user_data['adding_char_pinyin']
        code = context.user_data['adding_char_code']
        fullcode = context.user_data['adding_char_fullcode']

        await TYPING(update)

        result = Commands.safe_add_char(char, pinyin, "%s/%s" % (fullcode, code) if fullcode != code else fullcode)
        await REPLY(update, "\n".join(MARK(result)))
        context.user_data.clear()

        LOG(result)
        return -1

    return 2

async def delete_word(update, context):
    data = update.message.text
    if 'deleteing_word' not in context.user_data:
        context.user_data['deleteing_word'] = data
        await TYPING(update)

        ci = JDTools.get_word(data)
        if (ci is None):
            await REPLY(update, f'{data} 词不存在')
            context.user_data.clear()
            return -1
        
        pinyins = list(ci.pinyins())
        if len(pinyins) == 1:
            context.user_data['deleteing_word_pinyin'] = " ".join(pinyins[0])
            await REPLY(update, f"彻底删除 {context.user_data['deleteing_word']} 词")
            await CHOOSE(update, '确定要删除吗', ['是的'])
        else:
            await CHOOSE(update, '请选择要删除的读音', [" ".join(pinyin) for pinyin in pinyins])

    elif 'deleteing_word_pinyin' not in context.user_data:
        context.user_data['deleteing_word_pinyin'] = data
        await REPLY(update, f"删除 {context.user_data['deleteing_word']} 词读音 {data}")
        await CHOOSE(update, '确定要删除吗', ['是的'])

    else:
        word = context.user_data['deleteing_word']
        pinyin = context.user_data['deleteing_word_pinyin']

        await TYPING(update)

        result = Commands.safe_delete_word(word, pinyin)
        await REPLY(update, "\n".join(MARK(result)))
        context.user_data.clear()

        LOG(result)
        return -1

    return 4

async def delete_char(update, context):
    data = update.message.text
    if 'deleteing_char' not in context.user_data:
        context.user_data['deleteing_char'] = data
        await TYPING(update)

        zi = JDTools.get_char(data)
        if (zi is None):
            await REPLY(update, f'{data} 字不存在')
            context.user_data.clear()
            return -1
        
        pinyins = list(zi.pinyins())
        if len(pinyins) == 1:
            context.user_data['deleteing_char_pinyin'] = pinyins[0]
            await REPLY(update, f"彻底删除 {context.user_data['deleteing_char']} 字")
            await CHOOSE(update, '确定要删除吗', ['是的'])
        else:
            await CHOOSE(update, '请选择要删除的读音', pinyins)

    elif 'deleteing_char_pinyin' not in context.user_data:
        context.user_data['deleteing_char_pinyin'] = data
        await REPLY(update, f"删除 {context.user_data['deleteing_char']} 字读音 {data}")
        await CHOOSE(update, '确定要删除吗', ['是的'])

    else:
        char = context.user_data['deleteing_char']
        pinyin = context.user_data['deleteing_char_pinyin']

        await TYPING(update)

        result = Commands.safe_delete_char(char, pinyin)
        await REPLY(update, "\n".join(MARK(result)))
        context.user_data.clear()

        LOG(result)
        return -1
        
    return 5

async def change_word(update, context):
    data = update.message.text

    async def choose_length():
        word = context.user_data['changing_word']
        pinyin = context.user_data['changing_word_pinyin']
        
        space_data = JDTools.find_space_for_word(word, pinyin)
        if space_data is None:
            await REPLY(update, "无法添加")
            context.user_data.clear()
            return -1

        codes, spaces, dup = space_data

        await REPLY(update, f"全码：{str(codes)}\n可用码长：{str(spaces)}\n全码重码：{dup}")
        await CHOOSE(update, "请选择一个码长（推荐\\*）", [f"{codes[0][:i]}{'*' if i in spaces else ''}" for i in range(3, 7)])
        return 7

    if 'changing_word' not in context.user_data:
        context.user_data['changing_word'] = data
        await TYPING(update)

        ci = JDTools.get_word(data)
        if (ci is None):
            await REPLY(update, f'{data} 词不存在')
            context.user_data.clear()
            return -1

        pinyins = {}
        for code in JDTools.ci2codes(ci):
            ma = code[1]
            py = code[-2]
            if (py in pinyins):
                pinyins[py].append(ma)
            else:
                pinyins[py] = [ma]

        pinyins = list(pinyins.items())
        if len(pinyins) == 1:
            context.user_data['changing_word_pinyin'] = pinyins[0][0]
            return await choose_length()
        else:
            await CHOOSE(update, '请选择要更改长度的编码', [("%s\n%s" % ("/".join(pinyin[1]), pinyin[0])) for pinyin in pinyins])
    elif 'changing_word_pinyin' not in context.user_data:
        data = data.split('\n')
        if (len(data) < 2):
            await REPLY(update, '操作已取消')
            context.user_data.clear()
            return -1
        
        context.user_data['changing_word_pinyin'] = data[1]
        return await choose_length()
    elif 'changing_word_code' not in context.user_data:
        data = data.strip('*')
        context.user_data['changing_word_code'] = data
        await REPLY(update, f"变更 {context.user_data['changing_word']} 词码长 -> {data}")
        await CHOOSE(update, '确定要修改吗', ['是的'])
    else:
        word = context.user_data['changing_word']
        pinyin = context.user_data['changing_word_pinyin']
        code = context.user_data['changing_word_code']

        await TYPING(update)
        
        continue_change = JDTools.get_ci_of_code(code)

        result = Commands.safe_change_word(word, pinyin, code)

        await REPLY(update, "\n".join(MARK(result)))
        context.user_data.clear()

        LOG(result)

        if continue_change is not None and len(continue_change) > 0:
            await CHOOSE(update, "是否要修改 %s 码词？" % code, ["/change " + ci.word() for ci in continue_change])

        return -1
    
    return 7

async def change_char(update, context):
    data = update.message.text

    async def choose_length():
        char = context.user_data['changing_char']
        pinyin = context.user_data['changing_char_pinyin']
        zi = JDTools.get_char(char)
        if (zi is None):
            await REPLY(update, f'{char} 字不存在')
            context.user_data.clear()
            return -1

        space_data = JDTools.find_space_for_char(JDTools.s(zi.shape()), pinyin)
        if space_data is None:
            await REPLY(update, "无法添加")
            context.user_data.clear()
            return -1
    
        codes, spaces, dup = space_data
        context.user_data['changing_char_fullcode'] = codes[0]

        await REPLY(update, f"全码：{str(codes)}\n可用码长：{str(spaces)}\n全码重码：{dup}")
        await CHOOSE(update, "请选择一个码长（推荐\\*）", [f"{codes[0][:i]}{'*' if i in spaces else ''}" for i in range(2, 7)])
        return 8

    if 'changing_char' not in context.user_data:
        context.user_data['changing_char'] = data
        await CHOOSE(update, "需要修改什么", ['笔码', '码长'])
    
    elif 'changing_char_type' not in context.user_data:
        context.user_data['changing_char_type'] = data
        char = context.user_data['changing_char']
        if (data == '笔码'):
            zi = JDTools.get_char(char)
            if (zi is None):
                await REPLY(update, f'{char} 字不存在')
                context.user_data.clear()
                return -1
            await REPLY(update, "请输入 %s 字笔码，当前：%s" % (char, JDTools.s(zi.shape())))
        elif (data == '码长'):
            zi = JDTools.get_char(char)
            if (zi is None):
                await REPLY(update, f'{char} 字不存在')
                context.user_data.clear()
                return -1

            pinyins = {}
            for code in JDTools.zi2codes(zi):
                ma = code[1]
                py = code[-1]
                if (py in pinyins):
                    pinyins[py].append(ma)
                else:
                    pinyins[py] = [ma]

            pinyins = list(pinyins.items())
            if len(pinyins) == 1:
                context.user_data['changing_char_pinyin'] = pinyins[0][0]
                return await choose_length()
            else:
                await CHOOSE(update, '请选择要更改长度的编码', [("%s\n%s" % ("/".join(pinyin[1]), pinyin[0])) for pinyin in pinyins])
        else:
            await REPLY(update, '操作已取消')
            context.user_data.clear()
            return -1
    elif context.user_data['changing_char_type'] == '笔码':
        if 'changing_char_shape' not in context.user_data:
            context.user_data['changing_char_shape'] = JDTools.code2shape(data)
            char = context.user_data['changing_char']
            zi = JDTools.get_char(char)
            if (zi is None):
                await REPLY(update, f'{char} 字不存在')
                context.user_data.clear()
                return -1

            pinyin = list(zi.pinyins())[0]
            context.user_data['changing_char_pinyin'] = pinyin
            codes = list(JDTools.char2codes(data, pinyin, 6, False, True))
            if (len(codes) == 0):
                await REPLY(update, "无法添加")
                context.user_data.clear()
                return -1
            context.user_data['changing_char_code'] = codes[0]
            await REPLY(update, f"变更 {context.user_data['changing_char']} 字笔码 {JDTools.s(zi.shape())} -> {data}")
            await CHOOSE(update, '确定要修改吗', ['是的'])

        else:
            char = context.user_data['changing_char']
            pinyin = context.user_data['changing_char_pinyin']
            code = context.user_data['changing_char_code']

            await TYPING(update)

            result = Commands.safe_change_char(char, pinyin, code)
            await REPLY(update, "\n".join(MARK(result)))
            context.user_data.clear()

            LOG(result)
            return -1
        
    elif context.user_data['changing_char_type'] == '码长':
        if 'changing_char_pinyin' not in context.user_data:
            data = data.split('\n')
            if (len(data) < 2):
                await REPLY(update, '操作已取消')
                context.user_data.clear()
                return -1
            
            context.user_data['changing_char_pinyin'] = data[1]
            return await choose_length()
        elif 'changing_char_code' not in context.user_data:
            data = data.strip('*')
            context.user_data['changing_char_code'] = data
            await REPLY(update, f"变更 {context.user_data['changing_char']} 字码长 -> {data}")
            await CHOOSE(update, '确定要修改吗', ['是的'])
        else:
            char = context.user_data['changing_char']
            pinyin = context.user_data['changing_char_pinyin']
            code = context.user_data['changing_char_code']
            fullcode = context.user_data['changing_char_fullcode']

            await TYPING(update)

            result = Commands.safe_change_char(char, pinyin, "%s/%s" % (fullcode, code) if fullcode != code else fullcode)
            await REPLY(update, "\n".join(MARK(result)))
            context.user_data.clear()

            LOG(result)
            return -1
    else:
        await REPLY(update, '操作已取消')
        context.user_data.clear()
        return -1
    
    return 8

async def getjd(update, context):
    await TYPING(update)

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

    with urllib.request.urlopen('https://raw.githubusercontent.com/xkinput/Rime_JD/master/Tools/TermsTools/chaojizici.txt') as f:
        data = f.read().decode('utf-8')
        lines = data.split('\n')
        for line in lines:
            line = line.strip()
            if '\t' in line:
                word = line.split('\t')[0]
                if len(word) > 1:
                    jd6_words.add(word)

    jd6_diff = jd6_words.difference(jdc_words).difference(refuse_list)

    await REPLY(update, ("键道6新词：\n" + CLEAN("\n".join(sorted(jd6_diff)))) if len(jd6_diff) > 0 else "无新词")

async def default_message(update, context):
    data = update.message.text
    if data.startswith('/'):
        await REPLY(update, '未进行操作')
        return -1

    if (re.match('^[a-z;]{1,6}$', data)) or JDTools.get_char(data) is not None or JDTools.get_word(data) is not None:
        with update.message._unfrozen():
            update.message.text = "/list " + data
        return await list_command(update, context)
    else:
        with update.message._unfrozen():
            update.message.text = "/add " + data
        return await add(update, context)

def main():
    # Initialize bot
    application = Application.builder().token(os.environ['TELEGRAM_BOT_TOKEN']).build()

    # Add handlers
    cancel_handler = MessageHandler(filters.Regex('^(/取消|/cancel)$'), cancel)

    add_convers = ConversationHandler(
        entry_points=[
            CommandHandler('add', add),
            CommandHandler('delete', delete),
            CommandHandler('change', change),
            CommandHandler('rank', rank),
            CommandHandler('list', list_command),
            CommandHandler('drop', drop),
            CommandHandler('push', push),
            CommandHandler('status', status),
            CommandHandler('pull', pull),
            CommandHandler('getjd', getjd),
            CommandHandler('start', start),
            CommandHandler('user_add', user_add),
            CommandHandler('user_delete', user_delete),
            MessageHandler(filters.ALL, default_message)
        ],
        states={
            0: [cancel_handler, MessageHandler(filters.Regex('^.$'), add_char), MessageHandler(filters.ALL, add_word)],
            1: [cancel_handler, MessageHandler(filters.ALL, add_word)],
            2: [cancel_handler, MessageHandler(filters.ALL, add_char)],
            3: [cancel_handler, MessageHandler(filters.Regex('^.$'), delete_char), MessageHandler(filters.ALL, delete_word)],
            4: [cancel_handler, MessageHandler(filters.ALL, delete_word)],
            5: [cancel_handler, MessageHandler(filters.ALL, delete_char)],
            6: [cancel_handler, MessageHandler(filters.Regex('^.$'), change_char), MessageHandler(filters.ALL, change_word)],
            7: [cancel_handler, MessageHandler(filters.ALL, change_word)],
            8: [cancel_handler, MessageHandler(filters.ALL, change_char)],
            9: [cancel_handler, MessageHandler(filters.ALL, rank)],
            10: [cancel_handler, MessageHandler(filters.ALL, list_command)],
            11: [cancel_handler, MessageHandler(filters.ALL, drop)],
            12: [cancel_handler, MessageHandler(filters.ALL, push)],
            13: [cancel_handler, MessageHandler(filters.ALL, user_add)],
            14: [cancel_handler, MessageHandler(filters.ALL, user_delete)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(add_convers)

    # Start bot
    application.run_polling()

if __name__ == '__main__':
    main()
