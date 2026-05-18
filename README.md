# python-clay

[![Clay version](https://img.shields.io/badge/clay-v0.14-blue)](https://github.com/nicbarker/clay)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://python.org)

**Python bindings for [Clay](https://github.com/nicbarker/clay)** — a high-performance, zero-dependency, single-header C flexbox layout engine. Uses pure `ctypes` — no C extensions to compile, no extra toolchain required for end users.

## Features

- **Pure Python bindings** — uses `ctypes` only, works on any standard CPython 3.8+
- **Pythonic API** — context managers, no raw pointers, no manual memory management
- **Flexbox-like layout** — `"grow"`, `"fit"`, fixed pixels, padding, child gaps, alignment
- **Render agnostic** — outputs sorted render commands (rectangles, text, borders, images, scissor clips)
- **Battle-tested struct mapping** — all 38 C structs verified against `sizeof()` at import time
- **Microsecond layout** — Clay benchmarks in microseconds for thousands of elements

## Install

```bash
git clone https://github.com/davtheconquerer/python-clay
cd python-clay
pip install .
```

> **Windows users:** A pre-built `clay.dll` is bundled — no compiler needed.  
> **Linux/macOS:** The installer runs `make` automatically. You'll need `gcc` / `clang` and `make` installed.

### Quick development install

```bash
pip install -e .
```

## Quick Start

```python
from python_clay import Clay, Layout

app = Clay(width=800, height=600)

with app:
    with app.box(
        layout=Layout(width="grow", height="grow", padding=16,
                      child_gap=16, direction="row"),
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
        ):
            pass

# app.render_commands contains sorted Clay_RenderCommand objects
```

## Rendering

Clay is renderer-agnostic. Here's a complete example that renders the layout above to a PNG using Pillow:

```python
from PIL import Image, ImageDraw
from python_clay import Clay, Layout, iter_commands
from python_clay.clay_ctypes import CLAY_RENDER_COMMAND_TYPE_RECTANGLE

app = Clay(800, 600)

with app:
    with app.box(
        layout=Layout(width="grow", height="grow", padding=16,
                      child_gap=16, direction="row"),
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
        ):
            pass

img = Image.new("RGBA", (800, 600), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

for cmd in iter_commands(app.render_commands):
    if cmd.commandType == CLAY_RENDER_COMMAND_TYPE_RECTANGLE:
        r = cmd.renderData.rectangle
        color = (int(r.r), int(r.g), int(r.b), int(r.a))
        x1, y1 = int(cmd.boundingBox.x), int(cmd.boundingBox.y)
        x2 = int(cmd.boundingBox.x + cmd.boundingBox.width) - 1
        y2 = int(cmd.boundingBox.y + cmd.boundingBox.height) - 1
        draw.rectangle([x1, y1, x2, y2], fill=color)

img.save("output.png")
```

Run the included demo:
```bash
pip install Pillow   # only needed once
python render_pillow.py
```

## API Reference

### `Clay(width, height)`

Creates a new Clay layout engine instance. Allocates the internal arena, initializes the error handler, and sets the layout dimensions.

```python
app = Clay(width=800, height=600)
```

### `with app: ...`

A context manager that wraps `Clay_BeginLayout()` / `Clay_EndLayout()`. All element declarations must happen inside this block. The render commands are available on `app.render_commands` after the block exits.

### `app.box(layout, background, corner_radius, id)`

A context manager that creates a UI element. Opens, configures, and later closes the element.

| Parameter | Type | Description |
|-----------|------|-------------|
| `layout` | `Layout` or `None` | Sizing, padding, direction, alignment |
| `background` | `(r,g,b,a)` tuple or `None` | Background color (values 0–255, stored as floats) |
| `corner_radius` | `(tl,tr,bl,br)` or `None` | Corner radius in pixels |
| `id` | `str` or `None` | Element ID for later queries; auto-generated if `None` |

### `Layout(**options)`

Declarative configuration for element sizing and layout.

| Option | Values | Description |
|--------|--------|-------------|
| `width` | `"grow"`, `"fit"`, pixel value, `(min,max)` tuple | Horizontal sizing |
| `height` | same as width | Vertical sizing |
| `padding` | int (all), 2-tuple `(x,y)`, 4-tuple `(l,r,t,b)` | Inner padding |
| `child_gap` | int | Gap in pixels between children |
| `direction` | `"row"` or `"column"` | Layout axis |
| `child_align_x` | `"left"`, `"center"`, `"right"` | Horizontal child alignment |
| `child_align_y` | `"top"`, `"center"`, `"bottom"` | Vertical child alignment |

### `iter_commands(render_commands)`

Generator that yields `Clay_RenderCommand` objects. Each command has:

| Field | Type | Description |
|-------|------|-------------|
| `commandType` | int | `CLAY_RENDER_COMMAND_TYPE_*` enum |
| `boundingBox` | `Clay_BoundingBox` | Position and size relative to layout root |
| `renderData` | `Clay_RenderData` | Union — access `.rectangle`, `.text`, `.border`, etc. |
| `id` | `uint32` | Element ID from declaration |
| `zIndex` | `int16` | Z-order for rendering |
| `userData` | pointer | Transparent user pointer |

### Enums

Access enum constants from the low-level module:

```python
from python_clay.clay_ctypes import (
    CLAY_RENDER_COMMAND_TYPE_RECTANGLE,
    CLAY_LEFT_TO_RIGHT, CLAY_TOP_TO_BOTTOM,
    CLAY__SIZING_TYPE_FIT, CLAY__SIZING_TYPE_GROW,
    CLAY__SIZING_TYPE_FIXED, CLAY__SIZING_TYPE_PERCENT,
)
```

### Low-level ctypes API

All 40+ Clay C functions are mapped in `python_clay/clay_ctypes.py`. Access them directly:

```python
from python_clay.clay_ctypes import lib, Clay_Dimensions
lib.Clay_SetLayoutDimensions(Clay_Dimensions(1024, 768))
```

## Project Structure

```
python-clay/
  python_clay/            # Python package
    __init__.py            # Public exports
    clay.py                # Pythonic API wrapper
    clay_ctypes.py         # Raw ctypes struct + function mappings
    clay.dll               # Pre-built for Windows
  clay_wrapper.c           # C bridge (CLAY_IMPLEMENTATION)
  clay.h                   # Clay v0.14 engine
  Makefile                 # Cross-platform build
  pyproject.toml           # Package metadata
  setup.py                 # Install script
  test_console.py          # Console verification
  render_pillow.py         # Pillow renderer example
  README.md
  .gitignore
```

## Building from Source

You shouldn't need to build unless you're on Linux/macOS (where `pip install .` handles it) or you want to modify the C code.

### Windows (MinGW-w64)

```bash
# Install MSYS2 from https://www.msys2.org/
# In the UCRT64 terminal:
pacman -S mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-make

# Build:
mingw32-make
```

### Linux

```bash
sudo apt install gcc make
make
```

### macOS

```bash
xcode-select --install
make
```

The Makefile detects your OS and outputs `clay.dll` (Windows), `libclay.so` (Linux), or `libclay.dylib` (macOS).

## How It Works

Clay is a pure-C flexbox layout engine that uses static arena allocation (no `malloc`/`free`). It outputs a sorted array of `Clay_RenderCommand` structs describing what to draw and where.

This binding layers three levels:

1. **`clay_wrapper.c`** — The bridge C file that compiles `clay.h` into a shared library
2. **`clay_ctypes.py`** — Exact `ctypes` mappings for all structs and functions, with runtime `sizeof()` verification
3. **`clay.py`** — Pythonic API using context managers that hide raw pointers, arena management, and ID hashing

## Credits

- [Clay](https://github.com/nicbarker/clay) by [Nic Barker](https://github.com/nicbarker) — the underlying C layout engine
- This binding is an independent project, not affiliated with the official Clay repository

## License

This binding is provided under the MIT license. Clay itself is [zlib/libpng licensed](https://github.com/nicbarker/clay/blob/main/LICENSE).
