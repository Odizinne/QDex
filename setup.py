from cx_Freeze import setup, Executable
import sys
import os

build_dir = "build/QDex"
base = None
system_icon = None
if sys.platform == "win32":
    base = "Win32GUI"
    system_icon = "icons/icon.ico"

build_exe_options = {
    "include_files": ["design.ui", "icons/", "sprites/", "font/", "types/", "abilities.json", "settings.json", "pokemon_details.json"],
    "build_exe": build_dir
}

executables = [
    Executable("qdex.py", base=base, icon=system_icon)
]

setup(
    name="QDex",
    version="0.1",
    description="QDex",
    options={"build_exe": build_exe_options},
    executables=executables
)
