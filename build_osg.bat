@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
set PATH=D:\APPAz\git\Git\bin;D:\APPAz\git\Git\cmd;C:\Qt\Tools\CMake_64\bin;C:\Qt\Tools\Ninja;%PATH%
set CMAKE_PREFIX_PATH=C:\Qt\6.8.3\msvc2022_64

echo === Configuring OSG with Visual Studio ===
cmake -G "Visual Studio 17 2022" -A x64 -S "D:\Lcode\OpenSceneGraph-OpenSceneGraph-3.6.5" -B "D:\Lcode\OpenSceneGraph-OpenSceneGraph-3.6.5\build" -DCMAKE_INSTALL_PREFIX="D:\Lcode\OSG" -DCMAKE_PREFIX_PATH="C:\Qt\6.8.3\msvc2022_64" -DOSG_USE_FLOAT_MATRIX=ON -DOSG_USE_FLOAT_PLANE=ON -DOSG_USE_FLOAT_QUAT=ON -DOSG_USE_FLOAT_VEC=ON -DOPENGL_PROFILE=GL2 -DBUILD_OSG_APPLICATIONS=OFF -DBUILD_OSG_EXAMPLES=OFF

echo === Building OSG (Release) ===
cmake --build "D:\Lcode\OpenSceneGraph-OpenSceneGraph-3.6.5\build" --config Release --parallel

echo === Installing OSG ===
cmake --install "D:\Lcode\OpenSceneGraph-OpenSceneGraph-3.6.5\build" --config Release

echo === OSG Build Complete ===
