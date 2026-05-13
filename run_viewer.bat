@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
set PATH=C:\Qt\6.8.3\msvc2022_64\bin;D:\Lcode\OSG\bin;%PATH%
set OSG_FILE_PATH=D:\Lcode\OSG\data
set OSG_LIBRARY_PATH=D:\Lcode\qt-autopilot\workspace\OsgViewer\build\Release\osgPlugins-3.6.5

echo === Launching OsgViewer ===
start "" "D:\Lcode\qt-autopilot\workspace\OsgViewer\build\Release\OsgViewer.exe"
