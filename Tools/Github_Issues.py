from github import Github
from git import Repo, Git

import os
import re
    
allowed_commands = {
    '添加': 1,
    '变码': 2,
    '删除': 3,
    '排序': 4,
}

def find_commands(content):
    sanitized = content.replace('\r\n', '\n')
    match = re.search('```(.*)```', sanitized, re.DOTALL)
    commands = []
    if match is None:
        return []
    
    lines = match[1].split('\n')
    for line in lines:
        line = line.strip()
        if (not line.startswith('#')) and '\t' in line:
            command = tuple(line.split('\t'))
            if (command[0] in allowed_commands):
                commands.append(command)

    return commands, sorted(commands, key=lambda c: (len(c[1]), allowed_commands[c[0]]))

def process_commands(commands):
    pass

# ----- ACTION -----

# GITHUB Auth
g = Github(os.environ['GITHUB_TOKEN'])

# GITHUB Repo
github_repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])
repo_path = os.path.join(os.environ['GITHUB_WORKSPACE'])

# GIT Repo
repo = Repo(repo_path)

# GITHUB Find Current Active PR
active_prs = github_repo.get_pulls(state='open', base='master', sort='created')
active_pr = None
for pr in active_prs:
    issue = pr.as_issue()
    if ("自动" in issue.get_labels()):
        active_pr = pr
        continue

# GITHUB No PR yet, create one now
if active_pr is None:
    pass

# Process Automation
open_issues = repo.get_issues(state='open', labels=['自动'])
for issue in open_issues:
    commands = find_commands(issue.body)
    print(commands)
    
    