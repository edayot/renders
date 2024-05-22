import os
import shlex

def main(release: str):
    print(f"Release {release}!")
    release = shlex.quote(release)
    if os.path.exists("branch"):
        os.system("rm -rf branch")
    os.makedirs("branch", exist_ok=True)
    os.chdir("branch")
    cloned_branch = "renders"
    git_url = "https://github.com/edayot/renders.git"
    os.system(f"git clone -b {cloned_branch} {git_url}")
    os.chdir("renders")
    # check if the release tag already exists
    if os.system(f"git rev-parse --verify --quiet {release}-renders") == 0:
        print(f"Release {release} already exists!")
        return

    cwd = os.getcwd()
    os.makedirs("resourcepack", exist_ok=True)
    os.system(f"model_resolver --load-vanilla --minecraft-version {release} --output-dir {cwd} --load-dir {cwd}/resourcepack")
    os.system("git add .")
    os.system(f"git commit -m '✨ Generate renders for {release}' --allow-empty")
    os.system(f"git tag -a '{release}-renders' -m '✨ Generate renders for {release}'")

    if "GITHUB_TOKEN" in os.environ:
        token = os.environ["GITHUB_TOKEN"]
        os.system(f"git remote set-url origin https://github-actions:{token}@{git_url.replace('https://', '')}")
    os.system("git push origin renders --tags")
    os.chdir("../..")
    os.system("rm poetry.lock")
    # os.system("rm -rf branch")





if __name__ == "__main__":
    release = os.getenv("MC_VERSION", "24w19b")
    main(release)