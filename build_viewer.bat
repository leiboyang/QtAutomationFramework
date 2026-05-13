@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
set PATH=C:\Qt\Tools\CMake_64\bin;C:\Qt\Tools\Ninja;D:\APPAz\git\Git\bin;D:\APPAz\git\Git\cmd;%PATH%
set CMAKE_PREFIX_PATH=C:\Qt\6.8.3\msvc2022_64;D:\Lcode\OSG
set OSG_DIR=D:\Lcode\OSG

echo === Configuring OsgViewer ===
cmake -G "Visual Studio 17 2022" -A x64 -S "D:\Lcode\qt-autopilot\workspace\OsgViewer" -B "D:\Lcode\qt-autopilot\workspace\OsgViewer\build" -DCMAKE_PREFIX_PATH="C:/Qt/6.8.3/msvc2022_64;D:/Lcode/OSG"

echo === Building OsgViewer (Release) ===
cmake --build "D:\Lcode\qt-autopilot\workspace\OsgViewer\build" --config Release --parallel

echo === OsgViewer Build Complete ===
