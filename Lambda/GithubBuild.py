import JDTools
import os

from git import Repo

# Commit Changes
JDTools.commit()

# GITHUB Repo
repo_path = os.path.join(os.environ['GITHUB_WORKSPACE'])

repo = Repo(repo_path).git
repo.config('user.name', '小涵')
repo.config('user.email', 'octocat@github.com')

changes = repo.status('--porcelain').strip()
if (len(changes) > 0):
    repo.add('-A')
    repo.commit(m="自动更新码表")
    repo.push()
