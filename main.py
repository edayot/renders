import os
import shlex
from pathlib import Path
from beet import ProjectConfig, run_beet, Context
from contextlib import contextmanager
from model_resolver.plugins import Render, get_default_components, resolve_key, Item

devmode = False


class AlreadyExists(Exception):
    pass


@contextmanager
def checkout_and_publish(branch: str, tag: str, release: str):
    os.makedirs(f"branch/{branch}", exist_ok=True)
    os.chdir(f"branch/{branch}")
    git_url = "https://github.com/edayot/renders.git"
    os.system(f"git clone -b {branch} {git_url} {branch}")
    os.chdir(branch)
    if os.system(f"git rev-parse --verify --quiet {tag}") == 0 and not devmode:
        print(f"Tag {tag} already exists, skipping")
        raise AlreadyExists(f"Tag {tag} already exists, skipping")
    yield
    if not devmode:
        os.system("git add .")
        os.system(f"git commit -m '✨ Generate renders for {release}' --allow-empty")
        os.system(f"git tag -a '{tag}' -m '✨ Generate renders for {release}'")
        if "GITHUB_TOKEN" in os.environ:
            token = os.environ["GITHUB_TOKEN"]
            os.system(
                f"git remote set-url origin https://github-actions:{token}@{git_url.replace('https://', '')}"
            )
        os.system(f"git push origin {branch} --tags")
    os.chdir("../../..")
    if not devmode:
        os.system(f"rm -rf branch/{branch}")


def main(release: str):
    print(f"Release {release}!")
    release = shlex.quote(release)
    if os.path.exists("branch"):
        os.system("rm -rf branch")
    os.makedirs("branch", exist_ok=True)

    try:
        with checkout_and_publish("renders", f"{release}-renders", release):
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
                meta={
                    "model_resolver": {
                        "minecraft_version": release,
                        "preferred_minecraft_generated": "java",
                    }
                },
                resource_pack={"load": load_dir, "name": load_dir.name},
            )
            with run_beet(config=config) as ctx:
                pass
    except AlreadyExists:
        pass

    try:
        with checkout_and_publish(
            "renders-special", f"{release}-renders-special", release
        ):
            cwd = Path(os.getcwd())
            load_dir = cwd / "resourcepack"
            print(f"Running beet in {cwd}")
            os.system("rm -rf resourcepack")
            os.makedirs("resourcepack", exist_ok=True)
            config = ProjectConfig(
                pipeline=[
                    "model_resolver.plugins.render_all_items",
                ],
                output=cwd,
                meta={
                    "model_resolver": {
                        "minecraft_version": release,
                        "special_rendering": True,
                        "preferred_minecraft_generated": "java",
                    }
                },
                resource_pack={"load": load_dir, "name": load_dir.name},
            )
            with run_beet(config=config) as ctx:
                pass
    except AlreadyExists:
        pass

    try:
        with checkout_and_publish(
            "renders-webp", f"{release}-renders-webp", release
        ):
            cwd = Path(os.getcwd())
            load_dir = cwd / "resourcepack"
            print(f"Running beet in {cwd}")
            os.system("rm -rf resourcepack")
            os.makedirs("resourcepack", exist_ok=True)
            config = ProjectConfig(
                pipeline=[
                    render_webp,
                ],
                output=cwd,
                meta={
                    "model_resolver": {
                        "minecraft_version": release,
                        "special_rendering": True,
                        "preferred_minecraft_generated": "java",
                    }
                },
                resource_pack={"load": load_dir, "name": load_dir.name},
            )
            with run_beet(config=config) as ctx:
                pass
    except AlreadyExists:
        pass

def render_webp(ctx: Context):
    render = Render(ctx)
    for model in render.getter._vanilla.assets.models:
        namespace, path = model.split(":")
        render.add_model_task(
            model,
            path_ctx=f"{namespace}:render/{path}",
            animation_mode="webp",
            animation_framerate=60,
        )
    components = get_default_components(ctx)
    for item in components:
        namespace, path = resolve_key(item).split(":")
        render.add_item_task(
            Item(id=f"{namespace}:{path}"),
            path_ctx=f"{namespace}:render/items/{path}",
            animation_mode="webp",
            animation_framerate=60,
        )
    render.run()



if __name__ == "__main__":
    release = os.getenv("MC_VERSION", "1.21.4")
    if release is None or len(release) == 0:
        raise ValueError(f"MC_VERSION is not set, got {release}")
    if not "," in release:
        main(release)
    else:
        for r in release.split(","):
            main(r)
