"""Render Clay layout using the Pythonic API."""
from PIL import Image, ImageDraw
from python_clay import Clay, Layout, iter_commands
from python_clay.clay_ctypes import CLAY_RENDER_COMMAND_TYPE_RECTANGLE

# ── Build layout with the Pythonic API ──
app = Clay(width=800, height=600)

with app:
    with app.box(
        layout=Layout(width="grow", height="grow", padding=16, child_gap=16, direction="row"),
        background=(20, 20, 25, 255),
    ):
        with app.box(
            layout=Layout(width=200, height="grow"),
            background=(220, 80, 80, 255),
            corner_radius=(8, 8, 8, 8),
        ):
            pass

        with app.box(
            layout=Layout(width="grow", height="grow"),
            background=(60, 160, 200, 255),
            corner_radius=(8, 8, 8, 8),
        ):
            pass

commands = app.render_commands

# ── Render to PNG ──
img = Image.new("RGBA", (800, 600), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

for cmd in iter_commands(commands):
    if cmd.commandType == CLAY_RENDER_COMMAND_TYPE_RECTANGLE:
        r = cmd.renderData.rectangle
        color = (
            int(r.backgroundColor.r),
            int(r.backgroundColor.g),
            int(r.backgroundColor.b),
            int(r.backgroundColor.a),
        )
        x1 = int(cmd.boundingBox.x)
        y1 = int(cmd.boundingBox.y)
        x2 = int(cmd.boundingBox.x + cmd.boundingBox.width) - 1
        y2 = int(cmd.boundingBox.y + cmd.boundingBox.height) - 1
        draw.rectangle([x1, y1, x2, y2], fill=color)

img.save("clay_render.png")
print(f"Saved clay_render.png ({commands.length} commands)")
