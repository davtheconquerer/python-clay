import ctypes
import os
import sys

_platform = sys.platform
_dir = os.path.dirname(__file__)

if _platform == "win32":
    _lib_name = "clay.dll"
elif _platform == "linux":
    _lib_name = "libclay.so"
elif _platform == "darwin":
    _lib_name = "libclay.dylib"
else:
    raise OSError(f"Unsupported platform: {_platform}")

_dll_path = os.path.join(_dir, _lib_name)
if not os.path.exists(_dll_path):
    raise OSError(
        f"Clay shared library not found: {_dll_path}\n"
        f"Run 'make' in the project root to build it."
    )

lib = ctypes.CDLL(_dll_path)

# ── Enums ──────────────────────────────────────────────────────────
CLAY_LEFT_TO_RIGHT = 0
CLAY_TOP_TO_BOTTOM = 1

CLAY_ALIGN_X_LEFT = 0
CLAY_ALIGN_X_RIGHT = 1
CLAY_ALIGN_X_CENTER = 2

CLAY_ALIGN_Y_TOP = 0
CLAY_ALIGN_Y_BOTTOM = 1
CLAY_ALIGN_Y_CENTER = 2

CLAY__SIZING_TYPE_FIT = 0
CLAY__SIZING_TYPE_GROW = 1
CLAY__SIZING_TYPE_PERCENT = 2
CLAY__SIZING_TYPE_FIXED = 3

CLAY_TEXT_WRAP_WORDS = 0
CLAY_TEXT_WRAP_NEWLINES = 1
CLAY_TEXT_WRAP_NONE = 2

CLAY_TEXT_ALIGN_LEFT = 0
CLAY_TEXT_ALIGN_CENTER = 1
CLAY_TEXT_ALIGN_RIGHT = 2

CLAY_ATTACH_TO_NONE = 0
CLAY_ATTACH_TO_PARENT = 1
CLAY_ATTACH_TO_ELEMENT_WITH_ID = 2
CLAY_ATTACH_TO_ROOT = 3

CLAY_RENDER_COMMAND_TYPE_NONE = 0
CLAY_RENDER_COMMAND_TYPE_RECTANGLE = 1
CLAY_RENDER_COMMAND_TYPE_BORDER = 2
CLAY_RENDER_COMMAND_TYPE_TEXT = 3
CLAY_RENDER_COMMAND_TYPE_IMAGE = 4
CLAY_RENDER_COMMAND_TYPE_SCISSOR_START = 5
CLAY_RENDER_COMMAND_TYPE_SCISSOR_END = 6
CLAY_RENDER_COMMAND_TYPE_OVERLAY_COLOR_START = 7
CLAY_RENDER_COMMAND_TYPE_OVERLAY_COLOR_END = 8
CLAY_RENDER_COMMAND_TYPE_CUSTOM = 9

CLAY_POINTER_DATA_PRESSED_THIS_FRAME = 0
CLAY_POINTER_DATA_PRESSED = 1
CLAY_POINTER_DATA_RELEASED_THIS_FRAME = 2
CLAY_POINTER_DATA_RELEASED = 3

# ── Structs ─────────────────────────────────────────────────────────

class Clay_String(ctypes.Structure):
    _fields_ = [
        ("isStaticallyAllocated", ctypes.c_bool),
        ("length", ctypes.c_int32),
        ("chars", ctypes.c_char_p),
    ]

class Clay_StringSlice(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_int32),
        ("chars", ctypes.c_char_p),
        ("baseChars", ctypes.c_char_p),
    ]

class Clay_Arena(ctypes.Structure):
    _fields_ = [
        ("nextAllocation", ctypes.c_size_t),
        ("capacity", ctypes.c_size_t),
        ("memory", ctypes.c_char_p),
    ]

class Clay_Dimensions(ctypes.Structure):
    _fields_ = [
        ("width", ctypes.c_float),
        ("height", ctypes.c_float),
    ]

class Clay_Vector2(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
    ]

class Clay_Color(ctypes.Structure):
    _fields_ = [
        ("r", ctypes.c_float),
        ("g", ctypes.c_float),
        ("b", ctypes.c_float),
        ("a", ctypes.c_float),
    ]

class Clay_BoundingBox(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("width", ctypes.c_float),
        ("height", ctypes.c_float),
    ]

class Clay_ElementId(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("offset", ctypes.c_uint32),
        ("baseId", ctypes.c_uint32),
        ("stringId", Clay_String),
    ]

class Clay_ElementIdArray(ctypes.Structure):
    _fields_ = [
        ("capacity", ctypes.c_int32),
        ("length", ctypes.c_int32),
        ("internalArray", ctypes.POINTER(Clay_ElementId)),
    ]

class Clay_CornerRadius(ctypes.Structure):
    _fields_ = [
        ("topLeft", ctypes.c_float),
        ("topRight", ctypes.c_float),
        ("bottomLeft", ctypes.c_float),
        ("bottomRight", ctypes.c_float),
    ]

class Clay_SizingMinMax(ctypes.Structure):
    _fields_ = [
        ("min", ctypes.c_float),
        ("max", ctypes.c_float),
    ]

class Clay_SizingAxisUnion(ctypes.Union):
    _fields_ = [
        ("minMax", Clay_SizingMinMax),
        ("percent", ctypes.c_float),
    ]

class Clay_SizingAxis(ctypes.Structure):
    _fields_ = [
        ("size", Clay_SizingAxisUnion),
        ("type", ctypes.c_uint8),
    ]

class Clay_Sizing(ctypes.Structure):
    _fields_ = [
        ("width", Clay_SizingAxis),
        ("height", Clay_SizingAxis),
    ]

class Clay_Padding(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_uint16),
        ("right", ctypes.c_uint16),
        ("top", ctypes.c_uint16),
        ("bottom", ctypes.c_uint16),
    ]

class Clay_ChildAlignment(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_uint8),
        ("y", ctypes.c_uint8),
    ]

class Clay_LayoutConfig(ctypes.Structure):
    _fields_ = [
        ("sizing", Clay_Sizing),
        ("padding", Clay_Padding),
        ("childGap", ctypes.c_uint16),
        ("childAlignment", Clay_ChildAlignment),
        ("layoutDirection", ctypes.c_uint8),
    ]

class Clay_TextElementConfig(ctypes.Structure):
    _fields_ = [
        ("userData", ctypes.c_void_p),
        ("textColor", Clay_Color),
        ("fontId", ctypes.c_uint16),
        ("fontSize", ctypes.c_uint16),
        ("letterSpacing", ctypes.c_uint16),
        ("lineHeight", ctypes.c_uint16),
        ("wrapMode", ctypes.c_uint8),
        ("textAlignment", ctypes.c_uint8),
    ]

class Clay_AspectRatioElementConfig(ctypes.Structure):
    _fields_ = [
        ("aspectRatio", ctypes.c_float),
    ]

class Clay_ImageElementConfig(ctypes.Structure):
    _fields_ = [
        ("imageData", ctypes.c_void_p),
    ]

class Clay_FloatingAttachPoints(ctypes.Structure):
    _fields_ = [
        ("element", ctypes.c_uint8),
        ("parent", ctypes.c_uint8),
    ]

class Clay_FloatingElementConfig(ctypes.Structure):
    _fields_ = [
        ("offset", Clay_Vector2),
        ("expand", Clay_Dimensions),
        ("parentId", ctypes.c_uint32),
        ("zIndex", ctypes.c_int16),
        ("attachPoints", Clay_FloatingAttachPoints),
        ("pointerCaptureMode", ctypes.c_uint8),
        ("attachTo", ctypes.c_uint8),
        ("clipTo", ctypes.c_uint8),
    ]

class Clay_CustomElementConfig(ctypes.Structure):
    _fields_ = [
        ("customData", ctypes.c_void_p),
    ]

class Clay_ClipElementConfig(ctypes.Structure):
    _fields_ = [
        ("horizontal", ctypes.c_bool),
        ("vertical", ctypes.c_bool),
        ("childOffset", Clay_Vector2),
    ]

class Clay_BorderWidth(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_uint16),
        ("right", ctypes.c_uint16),
        ("top", ctypes.c_uint16),
        ("bottom", ctypes.c_uint16),
        ("betweenChildren", ctypes.c_uint16),
    ]

class Clay_BorderElementConfig(ctypes.Structure):
    _fields_ = [
        ("color", Clay_Color),
        ("width", Clay_BorderWidth),
    ]

class Clay_ErrorData(ctypes.Structure):
    _fields_ = [
        ("errorType", ctypes.c_uint8),
        ("errorText", Clay_String),
        ("userData", ctypes.c_void_p),
    ]

Clay_ErrorHandlerFunc = ctypes.CFUNCTYPE(None, Clay_ErrorData)

class Clay_ErrorHandler(ctypes.Structure):
    _fields_ = [
        ("errorHandlerFunction", Clay_ErrorHandlerFunc),
        ("userData", ctypes.c_void_p),
    ]

class Clay_PointerData(ctypes.Structure):
    _fields_ = [
        ("position", Clay_Vector2),
        ("state", ctypes.c_uint8),
    ]

class Clay_ScrollContainerData(ctypes.Structure):
    _fields_ = [
        ("scrollPosition", ctypes.POINTER(Clay_Vector2)),
        ("scrollContainerDimensions", Clay_Dimensions),
        ("contentDimensions", Clay_Dimensions),
        ("config", Clay_ClipElementConfig),
        ("found", ctypes.c_bool),
    ]

class Clay_ElementData(ctypes.Structure):
    _fields_ = [
        ("boundingBox", Clay_BoundingBox),
        ("found", ctypes.c_bool),
    ]

# ── Render data structs ──────────────────────────────────────────────

class Clay_TextRenderData(ctypes.Structure):
    _fields_ = [
        ("stringContents", Clay_StringSlice),
        ("textColor", Clay_Color),
        ("fontId", ctypes.c_uint16),
        ("fontSize", ctypes.c_uint16),
        ("letterSpacing", ctypes.c_uint16),
        ("lineHeight", ctypes.c_uint16),
    ]

class Clay_RectangleRenderData(ctypes.Structure):
    _fields_ = [
        ("backgroundColor", Clay_Color),
        ("cornerRadius", Clay_CornerRadius),
    ]

class Clay_ImageRenderData(ctypes.Structure):
    _fields_ = [
        ("backgroundColor", Clay_Color),
        ("cornerRadius", Clay_CornerRadius),
        ("imageData", ctypes.c_void_p),
    ]

class Clay_CustomRenderData(ctypes.Structure):
    _fields_ = [
        ("backgroundColor", Clay_Color),
        ("cornerRadius", Clay_CornerRadius),
        ("customData", ctypes.c_void_p),
    ]

class Clay_ClipRenderData(ctypes.Structure):
    _fields_ = [
        ("horizontal", ctypes.c_bool),
        ("vertical", ctypes.c_bool),
    ]

class Clay_OverlayColorRenderData(ctypes.Structure):
    _fields_ = [
        ("color", Clay_Color),
    ]

class Clay_BorderRenderData(ctypes.Structure):
    _fields_ = [
        ("color", Clay_Color),
        ("cornerRadius", Clay_CornerRadius),
        ("width", Clay_BorderWidth),
    ]

class Clay_RenderData(ctypes.Union):
    _fields_ = [
        ("rectangle", Clay_RectangleRenderData),
        ("text", Clay_TextRenderData),
        ("image", Clay_ImageRenderData),
        ("custom", Clay_CustomRenderData),
        ("border", Clay_BorderRenderData),
        ("clip", Clay_ClipRenderData),
        ("overlayColor", Clay_OverlayColorRenderData),
    ]

class Clay_RenderCommand(ctypes.Structure):
    _fields_ = [
        ("boundingBox", Clay_BoundingBox),
        ("renderData", Clay_RenderData),
        ("userData", ctypes.c_void_p),
        ("id", ctypes.c_uint32),
        ("zIndex", ctypes.c_int16),
        ("commandType", ctypes.c_uint8),
    ]

class Clay_RenderCommandArray(ctypes.Structure):
    _fields_ = [
        ("capacity", ctypes.c_int32),
        ("length", ctypes.c_int32),
        ("internalArray", ctypes.POINTER(Clay_RenderCommand)),
    ]

# ── Transition ──────────────────────────────────────────────────────
class _Clay_TransitionEnter(ctypes.Structure):
    _fields_ = [
        ("setInitialState", ctypes.c_void_p),
        ("trigger", ctypes.c_uint8),
    ]

class _Clay_TransitionExit(ctypes.Structure):
    _fields_ = [
        ("setFinalState", ctypes.c_void_p),
        ("trigger", ctypes.c_uint8),
        ("siblingOrdering", ctypes.c_uint8),
    ]

class Clay_TransitionElementConfig(ctypes.Structure):
    _fields_ = [
        ("handler", ctypes.c_void_p),
        ("duration", ctypes.c_float),
        ("properties", ctypes.c_int32),
        ("interactionHandling", ctypes.c_uint8),
        ("enter", _Clay_TransitionEnter),
        ("exit", _Clay_TransitionExit),
    ]

class Clay_ElementDeclaration(ctypes.Structure):
    _fields_ = [
        ("layout", Clay_LayoutConfig),
        ("backgroundColor", Clay_Color),
        ("overlayColor", Clay_Color),
        ("cornerRadius", Clay_CornerRadius),
        ("aspectRatio", Clay_AspectRatioElementConfig),
        ("image", Clay_ImageElementConfig),
        ("floating", Clay_FloatingElementConfig),
        ("custom", Clay_CustomElementConfig),
        ("clip", Clay_ClipElementConfig),
        ("border", Clay_BorderElementConfig),
        ("transition", Clay_TransitionElementConfig),
        ("userData", ctypes.c_void_p),
    ]

# ── Verify struct sizes match C ─────────────────────────────────────
_expected_sizes = {
    Clay_String: 16,
    Clay_StringSlice: 24,
    Clay_Arena: 24,
    Clay_Dimensions: 8,
    Clay_Vector2: 8,
    Clay_Color: 16,
    Clay_BoundingBox: 16,
    Clay_ElementId: 32,
    Clay_ElementIdArray: 16,
    Clay_CornerRadius: 16,
    Clay_SizingMinMax: 8,
    Clay_SizingAxis: 12,
    Clay_Sizing: 24,
    Clay_Padding: 8,
    Clay_ChildAlignment: 2,
    Clay_LayoutConfig: 40,
    Clay_TextElementConfig: 40,
    Clay_AspectRatioElementConfig: 4,
    Clay_ImageElementConfig: 8,
    Clay_FloatingAttachPoints: 2,
    Clay_FloatingElementConfig: 28,
    Clay_CustomElementConfig: 8,
    Clay_ClipElementConfig: 12,
    Clay_BorderWidth: 10,
    Clay_BorderElementConfig: 28,
    Clay_ErrorData: 32,
    Clay_ErrorHandler: 16,
    Clay_PointerData: 12,
    Clay_RenderCommand: 80,
    Clay_RenderCommandArray: 16,
    Clay_ElementDeclaration: 248,
    Clay_TextRenderData: 48,
    Clay_RectangleRenderData: 32,
    Clay_ImageRenderData: 40,
    Clay_CustomRenderData: 40,
    Clay_ClipRenderData: 2,
    Clay_OverlayColorRenderData: 16,
    Clay_BorderRenderData: 44,
    Clay_RenderData: 48,
}

for struct_cls, expected in _expected_sizes.items():
    actual = ctypes.sizeof(struct_cls)
    if actual != expected:
        raise AssertionError(
            f"Size mismatch for {struct_cls.__name__}: expected {expected}, got {actual}"
        )

# ── Function signatures ─────────────────────────────────────────────

# Clay_MinMemorySize
lib.Clay_MinMemorySize.argtypes = []
lib.Clay_MinMemorySize.restype = ctypes.c_uint32

# Clay_CreateArenaWithCapacityAndMemory
lib.Clay_CreateArenaWithCapacityAndMemory.argtypes = [ctypes.c_size_t, ctypes.c_void_p]
lib.Clay_CreateArenaWithCapacityAndMemory.restype = Clay_Arena

# Clay_Initialize
lib.Clay_Initialize.argtypes = [Clay_Arena, Clay_Dimensions, Clay_ErrorHandler]
lib.Clay_Initialize.restype = ctypes.c_void_p

# Clay_SetLayoutDimensions
lib.Clay_SetLayoutDimensions.argtypes = [Clay_Dimensions]
lib.Clay_SetLayoutDimensions.restype = None

# Clay_SetPointerState
lib.Clay_SetPointerState.argtypes = [Clay_Vector2, ctypes.c_bool]
lib.Clay_SetPointerState.restype = None

# Clay_BeginLayout
lib.Clay_BeginLayout.argtypes = []
lib.Clay_BeginLayout.restype = None

# Clay_EndLayout
lib.Clay_EndLayout.argtypes = [ctypes.c_float]
lib.Clay_EndLayout.restype = Clay_RenderCommandArray

# Clay_GetElementId
lib.Clay_GetElementId.argtypes = [Clay_String]
lib.Clay_GetElementId.restype = Clay_ElementId

# Clay_Hovered
lib.Clay_Hovered.argtypes = []
lib.Clay_Hovered.restype = ctypes.c_bool

# Clay_PointerOver
lib.Clay_PointerOver.argtypes = [Clay_ElementId]
lib.Clay_PointerOver.restype = ctypes.c_bool

# Clay_UpdateScrollContainers
lib.Clay_UpdateScrollContainers.argtypes = [ctypes.c_bool, Clay_Vector2, ctypes.c_float]
lib.Clay_UpdateScrollContainers.restype = None

# Clay_GetScrollOffset
lib.Clay_GetScrollOffset.argtypes = []
lib.Clay_GetScrollOffset.restype = Clay_Vector2

# Clay_GetCurrentContext
lib.Clay_GetCurrentContext.argtypes = []
lib.Clay_GetCurrentContext.restype = ctypes.c_void_p

# Clay_SetCurrentContext
lib.Clay_SetCurrentContext.argtypes = [ctypes.c_void_p]
lib.Clay_SetCurrentContext.restype = None

# Clay_GetElementData
lib.Clay_GetElementData.argtypes = [Clay_ElementId]
lib.Clay_GetElementData.restype = Clay_ElementData

# Internal functions (needed for layout declaration)

# Clay__HashString
lib.Clay__HashString.argtypes = [Clay_String, ctypes.c_uint32]
lib.Clay__HashString.restype = Clay_ElementId

# Clay__OpenElement
lib.Clay__OpenElement.argtypes = []
lib.Clay__OpenElement.restype = None

# Clay__OpenElementWithId
lib.Clay__OpenElementWithId.argtypes = [Clay_ElementId]
lib.Clay__OpenElementWithId.restype = None

# Clay__ConfigureOpenElementPtr
lib.Clay__ConfigureOpenElementPtr.argtypes = [ctypes.POINTER(Clay_ElementDeclaration)]
lib.Clay__ConfigureOpenElementPtr.restype = None

# Clay__CloseElement
lib.Clay__CloseElement.argtypes = []
lib.Clay__CloseElement.restype = None

# Clay__OpenTextElement
lib.Clay__OpenTextElement.argtypes = [Clay_String, Clay_TextElementConfig]
lib.Clay__OpenTextElement.restype = None
