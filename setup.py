from cx_Freeze import setup, Executable
import sys


build_exe_options = {"packages": ["pygame", 'sys', 'os', 'logging', 'random']}

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    
setup(
    name = "InfiniCube",
    version = "0.69",
    description = "A game by Bill Tyros. 2012",
    options = {"build_exe": build_exe_options},
    executables = [Executable(script = "saints.py", base = base)])