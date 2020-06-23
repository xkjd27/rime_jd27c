import JD6Tools
import os

from git import Repo

# # Commit Changes
# JD6Tools.commit()

# GITHUB Repo
repo_path = os.path.join(os.environ['GITHUB_WORKSPACE'])

repo = Repo(repo_path).git
repo.config('user.name', '小涵')
repo.config('user.email', 'octocat@github.com')

changes = repo.diff_index('HEAD' ,'--name-only').strip()
if (len(changes) > 0):
    repo.add('-A')
    repo.commit(m="自动更新码表")
    repo.push()
