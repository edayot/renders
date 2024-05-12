import os

def main(release: str):
    print(f"Release {release}!")
    if os.path.exists("branch"):
        os.system("rm -rf branch")
    os.makedirs("branch", exist_ok=True)
    os.chdir("branch")
    cloned_branch = "renders"
    git_url = "https://github.com/edayot/renders.git"
    os.system(f"git clone -b {cloned_branch} {git_url}")
    os.chdir("renders")
    cwd = os.getcwd()
    os.makedirs("resourcepack", exist_ok=True)
    os.system(f"model_resolver --load-vanilla --minecraft-version {release} --output-dir {cwd} --load-dir {cwd}/resourcepack")
    os.system("git add .")
    os.system(f"git commit -m '✨ Generate renders for {release}'")
    os.system(f"git tag -a f'{release}-renders' -m '✨ Generate renders for {release}'")
    os.system("git push origin renders --tags")
    os.chdir("../..")
    # os.system("rm -rf branch")





if __name__ == "__main__":
    release = os.getenv("MC_VERSION", "1.20.6")
    main(release)