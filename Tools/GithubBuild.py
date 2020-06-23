import JD6Tools
import os

from git import Repo

# # Commit Changes
# JD6Tools.commit()

# GITHUB Repo
repo_path = os.path.join(os.environ['GITHUB_WORKSPACE'])

print("Setting up Git")
repo = Repo(repo_path).git
# repo.config('user.name', '小涵')
# repo.config('user.email', 'octocat@github.com')

repo.add('-A')
repo.commit(m="自动更新码表")
repo.push()