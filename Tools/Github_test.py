from github import Github

# GITHUB Repo
g = Github(os.environ['GITHUB_TOKEN'])

github_repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])

pr = github_repo.create_pull(title="Test PR", body="Test", head="test", base="master")

print(pr.head.etag)
print(pr.head.label)
print(pr.head.last_modified)
print(pr.head.ref)
print(pr.head.repo)
print(pr.head.sha)
print(pr.head.user)