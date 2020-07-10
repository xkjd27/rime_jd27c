from github import Github
from git import Repo

import os
import re

import GithubCommands

COMMAND_TRANSCRIPT = ''
ALL_COMMANDS = []

GENERAL = 1
SUPER = 2

allowed_commands = {
    '添加': 1,
    '变码': 2,
    '删除': 3,
    '排序': 4,
}

def find_commands_issue(content, which):
    sanitized = content.replace('\r\n', '\n')
    match = re.search('%s\n```\n((?:[^`]*\n)+)```' % ('通常字词' if which == GENERAL else '超级字词'), sanitized)

    if match is None:
        return []
    
    commands = []

    lines = match[1].split('\n')
    for line in lines:
        line = line.strip()
        if (not line.startswith('#')):
            if ('\t' in line):
                command = tuple(['通常' if which == GENERAL else '超级'] + [data.strip() for data in line.split('\t')])
            elif ('|' in line):
                command = tuple(['通常' if which == GENERAL else '超级'] + [data.strip() for data in line.split('|')])
            else:
                command = None
            if (command is not None and len(command) > 2 and command[1] in allowed_commands):
                commands.append(command)

    return sorted(commands, key=lambda c: (len(c[2]), allowed_commands[c[1]]))
    
def find_commands_pr(content):
    sanitized = content.replace('\r\n', '\n')
    match = re.search('```\n((?:[^`]*\n)+)```', sanitized)

    if match is None:
        return []
    
    commands = []

    lines = match[1].split('\n')
    for line in lines:
        line = line.strip()
        if (not line.startswith('#')) and '\t' in line:
            command = tuple(line.split('\t'))
            if (len(command) > 1 and command[1] in allowed_commands):
                commands.append(command)

    return commands

def find_comments(content):
    sanitized = content.replace('\r\n', '\n')
    match = re.search('---\n(.*)', sanitized, re.DOTALL)
    if match is None:
        return ''
    
    return match[1]

# ----- ACTION -----

# GITHUB Auth
g = Github(os.environ['GITHUB_TOKEN'])

# GITHUB Repo
github_repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])
repo_path = os.path.join(os.environ['GITHUB_WORKSPACE'])

# GIT Repo
print("Setting up Git")
repo = Repo(repo_path).git
repo.config('user.name', '小涵')
repo.config('user.email', 'octocat@github.com')

# GITHUB Find Current Active PR
print("Finding Active PR")
active_prs = github_repo.get_pulls(state='open', base='master', sort='created')
active_pr = None
pr_comment = ''
for pr in active_prs:
    issue = pr.as_issue()
    for label in issue.get_labels():
        if label.name == '自动':
            active_pr = pr
            ALL_COMMANDS = find_commands_pr(active_pr.body)
            pr_comment = find_comments(active_pr.body).strip()
            pr_comment += "\n"
            break
    
    if (active_pr is not None):
        break

working_branch = 'bot'
if active_pr is not None:
    working_branch = active_pr.head.ref

# switch to bot branch
print("Checking out working branch")
repo.checkout(B=working_branch)

# Check issues
print("Reading issues")
open_issues = github_repo.get_issues(state='open', labels=['自动'])
for issue in open_issues:

    # ignore pr
    if issue.pull_request is not None:
        continue

    super_commands = find_commands_issue(issue.body, SUPER)
    genreal_commands = find_commands_issue(issue.body, GENERAL)

    ALL_COMMANDS += super_commands
    ALL_COMMANDS += genreal_commands

    pr_comment += 'Closes #%d\n' % issue.number

    # remove labels
    issue.edit(labels=[])

if (len(ALL_COMMANDS) < 0):
    print('No Commands')
    exit(0)

print("Start command processing")
GithubCommands.process_commands(ALL_COMMANDS)

current_branch = repo.rev_parse('--abbrev-ref', 'HEAD')
if current_branch == 'master':
    print('Wrong branch')
    exit(0)

changes = repo.status('--porcelain').strip()
if (len(changes) <= 0):
    print('No changes')
    exit(0)

print("Commiting branch %s" % current_branch)
repo.add('-A')
repo.commit(m="自动合并码表")
repo.push('-u', 'origin', current_branch, '--force')

SHA = repo.rev_parse('HEAD').strip()

PR_BODY = '''
**该PR为自动生成**

全部指令：
```
%s
```

[查看报告文件](https://github.com/%s/blob/%s/Tools/Lambda/Report/)

码表操作记录：
%s

---
%s
''' % ('\n'.join(['\t'.join(command) for command in ALL_COMMANDS]), os.environ['GITHUB_REPOSITORY'], SHA, "\n".join(GithubCommands.COMMAND_TRANSCRIPT), pr_comment)

# GITHUB No PR yet, create one now
if active_pr is None:
    print("Creating PR")
    active_pr = github_repo.create_pull(title='自动码表合并', body=PR_BODY, head=working_branch, base='master')
    # add auto_label
    active_pr.as_issue().add_to_labels('自动')
else:
    print("Updating PR")
    active_pr.edit(body=PR_BODY)
    active_pr.update_branch()


