from github import Github

g = Github("473458c28b34f3432b72d888e54d2348e356b3e4")
repo = g.get_repo("TsFreddie/much-programming-core")

open_issues = repo.get_issues(state='open')
for issue in open_issues:
    print(issue)