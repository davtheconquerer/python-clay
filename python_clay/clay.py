import ctypes
from .clay_ctypes import *


# ── Layout sizing helper ──────────────────────────────────────────

def _parse_sizing(value):
    """Convert a Python-friendly sizing value to a Clay_SizingAxis."""
    axis = Clay_SizingAxis()
    if value is None:
        axis.type = CLAY__SIZING_TYPE_FIT
    elif isinstance(value, str):
        value = value.lower()
        if value == "fit":
            axis.type = CLAY__SIZING_TYPE_FIT
        elif value == "grow":
            axis.type = CLAY__SIZING_TYPE_GROW
        else:
            raise ValueError(f"Unknown sizing: {value!r}")
    elif isinstance(value, (int, float)):
        axis.type = CLAY__SIZING_TYPE_FIXED
        axis.size.minMax.min = float(value)
        axis.size.minMax.max = float(value)
    elif isinstance(value, tuple) and len(value) == 2:
        axis.type = CLAY__SIZING_TYPE_FIT
        axis.size.minMax.min = float(value[0])
        axis.size.minMax.max = float(value[1])
    else:
        raise ValueError(f"Invalid sizing value: {value!r}")
    return axis


# ── Layout config helper ──────────────────────────────────────────

class Layout:
    """Declarative layout configuration.

    Args:
        width:  "fit"|"grow"|pixels|(min,max) or None (default: "fit")
        height: same as width
        padding: int (all sides) or (left,right,top,bottom) tuple
        child_gap: gap in pixels between children
        direction: "row" (left-to-right) or "column" (top-to-bottom)
        child_align_x: "left"|"center"|"right"
        child_align_y: "top"|"center"|"bottom"
    """
    def __init__(self, *, width=None, height=None, padding=None,
                 child_gap=None, direction=None,
                 child_align_x=None, child_align_y=None):
        self._width = width
        self._height = height
        self._padding = padding
        self._child_gap = child_gap
        self._direction = direction
        self._child_align_x = child_align_x
        self._child_align_y = child_align_y

    def _apply(self, cfg: Clay_LayoutConfig):
        cfg.sizing.width = _parse_sizing(self._width)
        cfg.sizing.height = _parse_sizing(self._height)
        if self._padding is not None:
            _apply_padding(cfg.padding, self._padding)
        if self._child_gap is not None:
            cfg.childGap = self._child_gap
        if self._direction is not None:
            cfg.layoutDirection = (
                CLAY_LEFT_TO_RIGHT if self._direction == "row"
                else CLAY_TOP_TO_BOTTOM
            )
        if self._child_align_x is not None:
            cfg.childAlignment.x = _parse_align_x(self._child_align_x)
        if self._child_align_y is not None:
            cfg.childAlignment.y = _parse_align_y(self._child_align_y)


def _apply_padding(pad: Clay_Padding, value):
    if isinstance(value, (int, float)):
        v = int(value)
        pad.left = pad.right = pad.top = pad.bottom = v
    elif isinstance(value, tuple) and len(value) == 4:
        pad.left, pad.right, pad.top, pad.bottom = map(int, value)
    elif isinstance(value, tuple) and len(value) == 2:
        pad.left = pad.right = int(value[0])
        pad.top = pad.bottom = int(value[1])
    else:
        raise ValueError(f"Invalid padding: {value!r}")


def _parse_align_x(v):
    return {"left": CLAY_ALIGN_X_LEFT, "center": CLAY_ALIGN_X_CENTER,
            "right": CLAY_ALIGN_X_RIGHT}[v]


def _parse_align_y(v):
    return {"top": CLAY_ALIGN_Y_TOP, "center": CLAY_ALIGN_Y_CENTER,
            "bottom": CLAY_ALIGN_Y_BOTTOM}[v]


# ── Main Clay class ────────────────────────────────────────────────

class Clay:
    """Pythonic wrapper around the Clay layout engine.

    Usage:
        app = Clay(width=800, height=600)

        with app:
            with app.box(layout=Layout(width="grow", height="grow"),
                         background=(220, 80, 80, 255)):
                pass

        commands = app.render_commands
    """

    def __init__(self, width=800, height=600):
        min_memory = lib.Clay_MinMemorySize()
        self._memory = ctypes.create_string_buffer(min_memory)
        arena = lib.Clay_CreateArenaWithCapacityAndMemory(min_memory, self._memory)

        @Clay_ErrorHandlerFunc
        def _on_error(error_data):
            msg = ""
            if error_data.errorText.chars:
                msg = error_data.errorText.chars.decode(errors="replace")
            print(f"[Clay Error #{error_data.errorType}] {msg}")
        self._error_handler = Clay_ErrorHandler(_on_error, None)

        self._ctx = lib.Clay_Initialize(
            arena, Clay_Dimensions(width, height), self._error_handler
        )
        self._width = width
        self._height = height
        self._id_counter = 0
        self._held_bytes: list[bytes] = []
        self._render_commands: Clay_RenderCommandArray | None = None

    # ── Context manager for a layout frame ────────────────────────

    def __enter__(self):
        lib.Clay_SetLayoutDimensions(Clay_Dimensions(self._width, self._height))
        lib.Clay_BeginLayout()
        return self

    def __exit__(self, *args):
        self._render_commands = lib.Clay_EndLayout(0.016)
        self._held_bytes.clear()
        return False

    @property
    def render_commands(self):
        if self._render_commands is None:
            raise RuntimeError("No render commands yet — use inside `with app:` block")
        return self._render_commands

    # ── Element creation ──────────────────────────────────────────

    def box(self, *, layout: Layout | None = None,
            background: tuple[float, float, float, float] | None = None,
            corner_radius: tuple[float, float, float, float] | None = None,
            id: str | None = None):
        """Open a box (container / rectangle) element."""
        return _BoxContext(self, layout, background, corner_radius, id)

    def _make_element_id(self, label: str | None) -> Clay_ElementId:
        if label is None:
            self._id_counter += 1
            label = f"__clay_{self._id_counter}"
        raw = label.encode()
        self._held_bytes.append(raw)
        c_str = Clay_String()
        c_str.isStaticallyAllocated = True
        c_str.length = len(raw)
        c_str.chars = raw
        return lib.Clay__HashString(c_str, 0)


class _BoxContext:
    def __init__(self, clay: Clay, layout, background, corner_radius, id):
        self._clay = clay
        self._layout = layout
        self._background = background
        self._corner_radius = corner_radius
        self._id = id

    def __enter__(self):
        elem_id = self._clay._make_element_id(self._id)
        lib.Clay__OpenElementWithId(elem_id)

        decl = Clay_ElementDeclaration()
        if self._layout is not None:
            self._layout._apply(decl.layout)
        if self._background is not None:
            decl.backgroundColor = Clay_Color(*map(float, self._background))
        if self._corner_radius is not None:
            decl.cornerRadius = Clay_CornerRadius(*map(float, self._corner_radius))

        lib.Clay__ConfigureOpenElementPtr(ctypes.byref(decl))
        return self

    def __exit__(self, *args):
        lib.Clay__CloseElement()
        return False


# ── Render command helpers ─────────────────────────────────────────

def iter_commands(render_commands: Clay_RenderCommandArray):
    """Yield render commands from a Clay_RenderCommandArray."""
    for i in range(render_commands.length):
        yield render_commands.internalArray[i]
