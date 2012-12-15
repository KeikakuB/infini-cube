from cx_Freeze import setup, Executable
import sys



base = None
if sys.platform == "win32":
    base = "Win32GUI"
    
setup(
    name = "InfiniCube",
    version = "0.3",
    description = "InfiniCube, a next-generation game experience brought to you by Bill Tyros. 2012",
    executables = [Executable(script = "infinicube.py", base = base)])