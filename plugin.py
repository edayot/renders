from beet import ProjectConfig, run_beet, Context
from model_resolver.plugins import Render, get_default_components, resolve_key, Item


def beet_default(ctx: Context):
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