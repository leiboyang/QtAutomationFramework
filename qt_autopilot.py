import json
import os
import sys
import subprocess
import shutil
import re
from pathlib import Path
from datetime import datetime


class QtAutopilot:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.qt_dir = Path(self.config["qt_dir"])
        self.cmake_path = Path(self.config["cmake_path"])
        self.ninja_path = Path(self.config["ninja_path"])
        self.vcvarsall_path = Path(self.config["vcvarsall_path"])
        self.python_path = Path(self.config["python_path"])
        self.workspace_dir = Path(self.config["workspace_dir"])
        self.build_type = self.config.get("build_type", "Release")
        self.generator = self.config.get("generator", "Ninja")
        self.project_dir = None
        self.build_dir = None

    def log(self, level, msg):
        colors = {
            "INFO": "\033[94m",
            "OK": "\033[92m",
            "WARN": "\033[93m",
            "FAIL": "\033[91m",
            "RESET": "\033[0m",
        }
        c = colors.get(level, "")
        r = colors["RESET"]
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"{c}[{ts}] [{level}] {msg}{r}")

    def _get_vcvars_env(self):
        self.log("INFO", "Setting up MSVC environment...")
        bat = f'@echo off\r\ncall "{self.vcvarsall_path}" x64 >nul 2>&1\r\nset\r\n'
        tmp_bat = Path(os.environ.get("TEMP", ".")) / "_qt_autopilot_vcvars.bat"
        tmp_bat.write_text(bat, encoding="utf-8")
        try:
            result = subprocess.run(
                ["cmd", "/c", str(tmp_bat)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            env = {}
            for line in result.stdout.splitlines():
                if "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip()
            return env
        finally:
            tmp_bat.unlink(missing_ok=True)

    def _find_windows_sdk(self):
        kits_dir = Path(r"C:\Program Files (x86)\Windows Kits\10\bin")
        if not kits_dir.exists():
            return None, None
        sdk_versions = sorted(kits_dir.iterdir(), reverse=True)
        for v in sdk_versions:
            rc_path = v / "x64" / "rc.exe"
            if rc_path.exists():
                bin_dir = str(v / "x64")
                lib_dir = str(v).replace("\\bin", "\\Lib")
                return bin_dir, lib_dir
        return None, None

    def _build_env(self):
        env = os.environ.copy()

        vcvars = self._get_vcvars_env()
        env.update(vcvars)

        sdk_bin, sdk_lib = self._find_windows_sdk()

        extra_paths = [
            str(self.qt_dir / "bin"),
            str(self.cmake_path.parent),
            str(self.ninja_path.parent),
        ]
        if sdk_bin:
            extra_paths.append(sdk_bin)

        env["PATH"] = ";".join(extra_paths) + ";" + env.get("PATH", "")

        if sdk_lib:
            msvc_lib = str(Path(r"C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.50.35717\lib\x64"))
            env["LIB"] = f"{sdk_lib}\\um\\x64;{sdk_lib}\\ucrt\\x64;{msvc_lib};" + env.get("LIB", "")
            sdk_include = sdk_lib.replace("\\Lib", "\\Include")
            env["INCLUDE"] = f"{sdk_include}\\um;{sdk_include}\\ucrt;" + env.get("INCLUDE", "")

        env["CMAKE_PREFIX_PATH"] = str(self.qt_dir)
        env["Qt6_DIR"] = str(self.qt_dir / "lib" / "cmake" / "Qt6")
        return env

    def create_project(self, name, qt_components=None):
        if qt_components is None:
            qt_components = ["Widgets"]

        self.project_dir = self.workspace_dir / name
        self.build_dir = self.project_dir / "build"

        if self.project_dir.exists():
            self.log("WARN", f"Project dir exists, cleaning: {self.project_dir}")
            shutil.rmtree(self.project_dir)

        self.project_dir.mkdir(parents=True, exist_ok=True)
        src_dir = self.project_dir / "src"
        src_dir.mkdir(exist_ok=True)
        tests_dir = self.project_dir / "tests"
        tests_dir.mkdir(exist_ok=True)

        components_str = " ".join(qt_components)
        cmake_components = " ".join([f"Qt6::{c}" for c in qt_components])

        cmake_content = f"""cmake_minimum_required(VERSION 3.20)
project({name} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_FLAGS "${{CMAKE_CXX_FLAGS}} /W4 /utf-8")
set(CMAKE_CXX_FLAGS_RELEASE "${{CMAKE_CXX_FLAGS_RELEASE}} /O2")

find_package(Qt6 COMPONENTS {components_str} REQUIRED)

file(GLOB_RECURSE APP_SOURCES "src/*.cpp" "src/*.h")

add_executable(${{PROJECT_NAME}} ${{APP_SOURCES}})
target_link_libraries(${{PROJECT_NAME}} PRIVATE {cmake_components})

enable_testing()

file(GLOB_RECURSE TEST_SOURCES "tests/*.cpp" "tests/*.h")

if(TEST_SOURCES)
    find_package(Qt6 COMPONENTS Test REQUIRED)
    add_executable(${{PROJECT_NAME}}_tests ${{TEST_SOURCES}})
    target_link_libraries(${{PROJECT_NAME}}_tests PRIVATE {cmake_components} Qt6::Test)
    target_include_directories(${{PROJECT_NAME}}_tests PRIVATE "${{CMAKE_SOURCE_DIR}}/src")

    foreach(TEST_FILE ${{TEST_SOURCES}})
        get_filename_component(TEST_NAME ${{TEST_FILE}} NAME_WE)
        add_test(NAME ${{TEST_NAME}} COMMAND ${{PROJECT_NAME}}_tests)
    endforeach()
endif()
"""
        (self.project_dir / "CMakeLists.txt").write_text(cmake_content, encoding="utf-8")

        main_content = f"""#include <QApplication>
#include <QWidget>
#include <QLabel>
#include <QVBoxLayout>

int main(int argc, char *argv[])
{{
    QApplication app(argc, argv);

    QWidget window;
    window.setWindowTitle("{name}");
    window.resize(400, 300);

    QVBoxLayout *layout = new QVBoxLayout(&window);
    QLabel *label = new QLabel("Hello from {name}!");
    label->setAlignment(Qt::AlignCenter);
    layout->addWidget(label);

    window.show();
    return app.exec();
}}
"""
        (src_dir / "main.cpp").write_text(main_content, encoding="utf-8")

        test_content = f"""#include <QtTest/QtTest>
#include <QLabel>
#include <QWidget>

class Test{name} : public QObject
{{
    Q_OBJECT

private slots:
    void testLabelCreation()
    {{
        QLabel label("test");
        QVERIFY(!label.text().isEmpty());
    }}

    void testWidgetShow()
    {{
        QWidget widget;
        widget.show();
        QVERIFY(widget.isVisible());
    }}
}};

QTEST_MAIN(Test{name})
#include "Test{name}.moc"
"""
        (tests_dir / f"Test{name}.cpp").write_text(test_content, encoding="utf-8")

        self.log("OK", f"Project created: {self.project_dir}")
        return self.project_dir

    def add_source(self, filename, content, is_header=False):
        if self.project_dir is None:
            self.log("FAIL", "No project. Call create_project() first.")
            return

        src_dir = self.project_dir / "src"
        filepath = src_dir / filename
        filepath.write_text(content, encoding="utf-8")
        self.log("OK", f"Source added: {filename}")

    def add_test(self, filename, content):
        if self.project_dir is None:
            self.log("FAIL", "No project. Call create_project() first.")
            return

        tests_dir = self.project_dir / "tests"
        filepath = tests_dir / filename
        filepath.write_text(content, encoding="utf-8")
        self.log("OK", f"Test added: {filename}")

    def build(self):
        if self.project_dir is None:
            self.log("FAIL", "No project. Call create_project() first.")
            return False

        self.log("INFO", f"Building: {self.project_dir.name}")
        self.build_dir = self.project_dir / "build"
        self.build_dir.mkdir(exist_ok=True)

        env = self._build_env()

        configure_cmd = [
            str(self.cmake_path),
            "-G", self.generator,
            "-DCMAKE_BUILD_TYPE=" + self.build_type,
            "-DCMAKE_PREFIX_PATH=" + str(self.qt_dir),
            "-B", str(self.build_dir),
            "-S", str(self.project_dir),
        ]

        self.log("INFO", "Running CMake configure...")
        result = subprocess.run(
            configure_cmd, env=env, capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            self.log("FAIL", "CMake configure failed!")
            self._print_output(result.stdout, result.stderr)
            return False
        self.log("OK", "CMake configure succeeded")

        build_cmd = [
            str(self.cmake_path),
            "--build", str(self.build_dir),
            "--config", self.build_type,
        ]

        self.log("INFO", "Compiling...")
        result = subprocess.run(
            build_cmd, env=env, capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            self.log("FAIL", "Build failed!")
            self._print_output(result.stdout, result.stderr)
            return False

        self.log("OK", "Build succeeded!")
        return True

    def test(self):
        if self.build_dir is None or not self.build_dir.exists():
            self.log("FAIL", "Build directory not found. Run build() first.")
            return False

        env = self._build_env()

        test_cmd = [
            str(self.cmake_path),
            "--build", str(self.build_dir),
            "--config", self.build_type,
            "--target", "test",
        ]

        self.log("INFO", "Running tests...")
        result = subprocess.run(
            test_cmd, env=env, capture_output=True, text=True, timeout=120
        )

        ctest_cmd = [
            str(self.cmake_path),
            "-E", "chdir", str(self.build_dir),
            "ctest",
            "--output-on-failure",
            "-C", self.build_type,
        ]

        result = subprocess.run(
            ctest_cmd, env=env, capture_output=True, text=True, timeout=120
        )

        output = result.stdout + result.stderr
        if "0 tests failed" in output or "100% tests passed" in output or result.returncode == 0:
            self.log("OK", "All tests passed!")
            return True
        else:
            self.log("FAIL", "Some tests failed!")
            self._print_output(result.stdout, result.stderr)
            return False

    def run(self):
        if self.build_dir is None:
            self.log("FAIL", "Build first.")
            return

        env = self._build_env()
        exe_name = self.project_dir.name + ".exe"
        exe_path = self.build_dir / exe_name

        if not exe_path.exists():
            exe_path = self.build_dir / self.build_type / exe_name

        if not exe_path.exists():
            self.log("FAIL", f"Executable not found: {exe_path}")
            return

        self.log("INFO", f"Running: {exe_path}")
        subprocess.run([str(exe_path)], env=env)

    def full_pipeline(self, name, qt_components=None):
        self.log("INFO", "=" * 50)
        self.log("INFO", f"  Qt Autopilot Pipeline: {name}")
        self.log("INFO", "=" * 50)

        steps = [
            ("CREATE", lambda: self.create_project(name, qt_components)),
            ("BUILD", self.build),
            ("TEST", self.test),
        ]

        results = {}
        for step_name, step_fn in steps:
            self.log("INFO", f"--- Step: {step_name} ---")
            try:
                result = step_fn()
                if result is False:
                    results[step_name] = "FAILED"
                    self.log("FAIL", f"Pipeline stopped at: {step_name}")
                    break
                results[step_name] = "PASSED"
            except Exception as e:
                results[step_name] = f"ERROR: {e}"
                self.log("FAIL", f"Exception at {step_name}: {e}")
                break

        self.log("INFO", "=" * 50)
        self.log("INFO", "  Pipeline Results:")
        for k, v in results.items():
            level = "OK" if v == "PASSED" else "FAIL"
            self.log(level, f"  {k}: {v}")
        self.log("INFO", "=" * 50)

        return all(v == "PASSED" for v in results.values())

    def _print_output(self, stdout, stderr):
        if stdout:
            for line in stdout.splitlines()[-20:]:
                print(f"  {line}")
        if stderr:
            for line in stderr.splitlines()[-20:]:
                print(f"  {line}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python qt_autopilot.py <command> [args]")
        print()
        print("Commands:")
        print("  create <name> [Widgets|Network|Sql|...]  - Create Qt project")
        print("  build                                    - Build project")
        print("  test                                     - Run tests")
        print("  run                                      - Run executable")
        print("  pipeline <name> [Widgets|Network|...]    - Full pipeline")
        print("  add-source <filename> <content>          - Add source file")
        print("  add-test <filename> <content>            - Add test file")
        return

    pilot = QtAutopilot()
    cmd = sys.argv[1]

    if cmd == "create":
        name = sys.argv[2] if len(sys.argv) > 2 else "MyApp"
        components = sys.argv[3:] if len(sys.argv) > 3 else ["Widgets"]
        pilot.create_project(name, components)

    elif cmd == "build":
        if len(sys.argv) > 2:
            pilot.project_dir = Path(sys.argv[2])
            pilot.build_dir = pilot.project_dir / "build"
        pilot.build()

    elif cmd == "test":
        if len(sys.argv) > 2:
            pilot.project_dir = Path(sys.argv[2])
            pilot.build_dir = pilot.project_dir / "build"
        pilot.test()

    elif cmd == "run":
        if len(sys.argv) > 2:
            pilot.project_dir = Path(sys.argv[2])
            pilot.build_dir = pilot.project_dir / "build"
        pilot.run()

    elif cmd == "pipeline":
        name = sys.argv[2] if len(sys.argv) > 2 else "MyApp"
        components = sys.argv[3:] if len(sys.argv) > 3 else ["Widgets"]
        pilot.full_pipeline(name, components)

    elif cmd == "add-source":
        filename = sys.argv[2]
        content = sys.argv[3] if len(sys.argv) > 3 else ""
        pilot.add_source(filename, content)

    elif cmd == "add-test":
        filename = sys.argv[2]
        content = sys.argv[3] if len(sys.argv) > 3 else ""
        pilot.add_test(filename, content)

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
