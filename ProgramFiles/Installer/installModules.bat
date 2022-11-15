@echo off

runas /user:Administrator
net use S: \\john\student
pip install pillow
pip install docutils pygments pypiwin32 kivy_deps.sdl2 kivy_deps.glew
pip install kivy_deps.angle
pip install kivy
xcopy /s "S:\Typing\PythonTyping\ProgramFiles" "C:\ProgramFiles\"
xcopy "S:\Typing\PythonTyping\Version.txt" "C:\ProgramFiles"