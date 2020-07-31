import JDTools
import os

from git import Repo

# Commit Changes
JDTools.commit()

# GITHUB Repo
repo_path = os.path.join(os.environ['GITHUB_WORKSPACE'])

repo = Repo(repo_path).git

changes = repo.status('--porcelain').strip()
if (len(changes) > 0):
    repo.add('-A')
    repo.commit(m="构建码表")
    repo.push()
