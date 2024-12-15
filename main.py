import os
import shlex
from pathlib import Path
from beet import ProjectConfig, run_beet


def main(release: str, devmode: bool = False):
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
    if (
        os.system(f"git rev-parse --verify --quiet {release}-renders") == 0
        and not devmode
    ):
        print(f"Release {release} already exists!")
        return

    cwd = Path(os.getcwd())
    load_dir = cwd / "resourcepack"
    print(f"Running beet in {cwd}")
    os.system("rm -rf resourcepack")
    os.makedirs("resourcepack", exist_ok=True)
    config = ProjectConfig(
        pipeline=[
            "model_resolver.plugins.render_all_vanilla",
            "model_resolver.plugins.render_all_items",
        ],
        output=cwd,
        meta={"model_resolver": {"minecraft_version": release}},
        resource_pack={"load": load_dir, "name": load_dir.name},
    )
    with run_beet(config=config) as ctx:
        pass

    if not devmode:
        os.system("git add .")
        os.system(f"git commit -m '✨ Generate renders for {release}' --allow-empty")
        os.system(
            f"git tag -a '{release}-renders' -m '✨ Generate renders for {release}'"
        )

        if "GITHUB_TOKEN" in os.environ:
            token = os.environ["GITHUB_TOKEN"]
            os.system(
                f"git remote set-url origin https://github-actions:{token}@{git_url.replace('https://', '')}"
            )
        os.system("git push origin renders --tags")
        os.chdir("../..")
        os.system("rm poetry.lock")
        os.system("rm -rf branch")


if __name__ == "__main__":
    release = os.getenv("MC_VERSION", "1.21.4")
    if release is None or len(release) == 0:
        raise ValueError(f"MC_VERSION is not set, got {release}")
    if not "," in release:
        main(release)
    else:
        for r in release.split(","):
            main(r)
