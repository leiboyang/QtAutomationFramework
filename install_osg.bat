@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
set PATH=D:\APPAz\git\Git\bin;D:\APPAz\git\Git\cmd;%PATH%
D:\Lcode\vcpkg\vcpkg.exe install osg:x64-windows --clean-after-build

