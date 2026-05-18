"""Phase 3 test: initialize Clay, add a colored box, print render commands."""
import ctypes
from python_clay.clay_ctypes import *

box_id_bytes = b"MyBox"

def test_layout():
    # ── 1. Calculate arena size and allocate memory ──
    min_memory = lib.Clay_MinMemorySize()
    print(f"Clay_MinMemorySize() = {min_memory} bytes")
    memory = ctypes.create_string_buffer(min_memory)
    arena = lib.Clay_CreateArenaWithCapacityAndMemory(min_memory, memory)
    print(f"Arena: capacity={arena.capacity}, memory={ctypes.addressof(memory):#x}")

    # ── 2. Error handler ──
    @Clay_ErrorHandlerFunc
    def on_error(error_data):
        print(f"Clay error: type={error_data.errorType}")
    error_handler = Clay_ErrorHandler(on_error, None)

    # ── 3. Initialize ──
    layout_size = Clay_Dimensions(800.0, 600.0)
    ctx = lib.Clay_Initialize(arena, layout_size, error_handler)
    print(f"Clay_Initialize returned context: {ctx}")

    # ── 4. Set layout dimensions (should be called each frame) ──
    lib.Clay_SetLayoutDimensions(layout_size)

    # ── 5. Begin layout ──
    lib.Clay_BeginLayout()
    print("Clay_BeginLayout() OK")

    # ── 6. Declare a colored box element ──
    # Create element ID from string
    id_str = Clay_String()
    id_str.isStaticallyAllocated = True
    id_str.length = len(box_id_bytes)
    id_str.chars = box_id_bytes
    element_id = lib.Clay__HashString(id_str, 0)
    print(f"Element ID: hash={element_id.id}, offset={element_id.offset}")

    # Open element with ID
    lib.Clay__OpenElementWithId(element_id)

    # Configure element: fill the screen with a colored box
    decl = Clay_ElementDeclaration()
    decl.layout.sizing.width.type = CLAY__SIZING_TYPE_GROW
    decl.layout.sizing.height.type = CLAY__SIZING_TYPE_GROW
    decl.backgroundColor = Clay_Color(200.0, 50.0, 50.0, 255.0)

    lib.Clay__ConfigureOpenElementPtr(ctypes.byref(decl))
    lib.Clay__CloseElement()
    print("Element declared OK")

    # ── 7. End layout ──
    commands = lib.Clay_EndLayout(0.016)
    print(f"\nRender commands: count={commands.length}")
    for i in range(commands.length):
        cmd = commands.internalArray[i]
        r = cmd.renderData.rectangle
        print(f"  [{i}] type={cmd.commandType} "
              f"bbox=({cmd.boundingBox.x:.1f}, {cmd.boundingBox.y:.1f}, "
              f"{cmd.boundingBox.width:.1f}x{cmd.boundingBox.height:.1f}) "
              f"color=({r.backgroundColor.r:.0f},{r.backgroundColor.g:.0f},"
              f"{r.backgroundColor.b:.0f},{r.backgroundColor.a:.0f})")

    print("\n*** Test passed - no segfaults! ***")

if __name__ == "__main__":
    test_layout()
