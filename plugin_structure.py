from beet import Context
from model_resolver.plugins import Render


def beet_default(ctx: Context):
    render = Render(ctx)
    for structure in render.getter._vanilla.data.structures:
        render.add_structure_task(structure, path_ctx=structure)
    render.run()