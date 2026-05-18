import os
import sys
import subprocess
import urllib.request
import json
from setuptools import setup, find_packages


def _library_name():
    return {"win32": "clay.dll", "linux": "libclay.so", "darwin": "libclay.dylib"}.get(sys.platform)


def _download_prebuilt(lib_name):
    """Try to download a pre-built library from the latest GitHub release."""
    url = (
        f"https://github.com/davtheconquerer/python-clay/releases/latest/download/{lib_name}"
    )
    dest = os.path.join("python_clay", lib_name)
    print(f"Downloading pre-built {lib_name}...")
    try:
        urllib.request.urlretrieve(url, dest)
        print("Done.")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False


def _build_locally():
    """Build the shared library from source via Makefile."""
    print("Building Clay shared library from source...")
    try:
        subprocess.check_call(
            ["make"], shell=(sys.platform == "win32")
        )
        return True
    except Exception as e:
        print(f"Build failed: {e}")
        return False


def _ensure_library():
    lib_name = _library_name()
    if not lib_name:
        print(f"Warning: unsupported platform {sys.platform!r}")
        return

    lib_path = os.path.join("python_clay", lib_name)
    if os.path.exists(lib_path):
        return  # already present

    # 1. Try downloading a pre-built binary from GitHub Releases
    if _download_prebuilt(lib_name):
        return

    # 2. Fall back to building from source
    if _build_locally():
        # Move into package directory
        import shutil
        shutil.move(lib_name, lib_path)
        return

    print(
        f"Could not obtain {lib_name}. "
        f"See README.md for build instructions.",
    )


_ensure_library()

setup(
    packages=find_packages(),
    package_data={"python_clay": ["*.dll", "*.so", "*.dylib"]},
    include_package_data=True,
)
