# cpp_simple_interface

`cpp_simple_interface` is a small Python package for compiling C++ source files
with a local `g++` or MinGW compiler. It is useful when a Python workflow needs
to build a temporary C++ executable without introducing a larger build system.

## Features

- Compile one or more `.cpp` files into an executable from Python.
- Use the system `g++` by default, the `CXX` environment variable, or a custom
  compiler path.
- Check whether the configured compiler is available before compiling.
- Capture compiler errors and return them as plain Python values.
- Hide the extra console window when running on Windows.

## Requirements

- Python 3.10 or later.
- A working `g++` compatible compiler.

Install `g++` if it is not already available:

- Windows: install MinGW-w64 and add the `mingw64/bin` directory to `PATH`.
- Debian/Ubuntu: `sudo apt update && sudo apt install g++`
- RHEL/CentOS/Fedora: `sudo dnf install gcc-c++`
- macOS: `xcode-select --install`

You can verify your compiler from a terminal:

```bash
g++ --version
```

The package also respects the standard `CXX` environment variable:

```bash
CXX=clang++ python your_script.py
```

On Windows PowerShell:

```powershell
$env:CXX = "C:\msys64\mingw64\bin\g++.exe"
python your_script.py
```

## Installation

```bash
pip install cpp-simple-interface
```

## Quick Start

```python
from pathlib import Path

import cpp_simple_interface

source = Path("hello.cpp")
source.write_text(
    """
#include <cstdio>

int main() {
    std::printf("hello world!\\n");
    return 0;
}
""".strip(),
    encoding="utf-8",
)

success, message = cpp_simple_interface.compile_cpp_files(
    [str(source)],
    "hello.exe",
)

print(message)
if not success:
    raise RuntimeError("C++ compilation failed")
```

On Linux or macOS, you may prefer an output path without the `.exe` suffix:

```python
success, message = cpp_simple_interface.compile_cpp_files(
    ["hello.cpp"],
    "./hello",
)
```

## Compiler Selection

The compiler is selected in this order:

1. `set_gpp_filepath(...)`, when called by your Python code.
2. The `CXX` environment variable, when it is set before importing the package.
3. The default command `g++`.

`CXX` and `set_gpp_filepath()` may contain either a compiler executable path or
a compiler command:

```bash
CXX=clang++
CXX="ccache g++"
CXX="/opt/homebrew/opt/llvm/bin/clang++"
```

For Windows paths with spaces, quote the path in the environment variable:

```powershell
$env:CXX = '"C:\Program Files\LLVM\bin\clang++.exe"'
```

## API Reference

### `compile_cpp_files(cpp_files, exe_output_path, other_flags=["-std=c++17"])`

Compile one or more C++ source files into an executable.

Parameters:

- `cpp_files`: a list of `.cpp` file paths.
- `exe_output_path`: the output executable path.
- `other_flags`: additional compiler flags. The default is `["-std=c++17"]`.

Returns:

- `(True, message)` when compilation succeeds and the output file exists.
- `(False, message)` when validation fails, compilation fails, or the compiler
  cannot be found.

Example with multiple source files:

```python
success, message = cpp_simple_interface.compile_cpp_files(
    ["src/main.cpp", "src/math_utils.cpp"],
    "build/app.exe",
    other_flags=["-std=c++20", "-O2", "-Wall"],
)
```

### `check_gpp_exists()`

Return `True` when the configured compiler can be executed with `--version`.
Otherwise return `False`.

```python
if not cpp_simple_interface.check_gpp_exists():
    raise RuntimeError("g++ is not available")
```

### `set_gpp_filepath(gpp_filepath)`

Set a custom compiler executable path or compiler command. The compiler is
checked immediately with `--version`. If the compiler cannot be executed,
`FileNotFoundError` is raised and the previously configured compiler is kept.

```python
cpp_simple_interface.set_gpp_filepath(r"C:\msys64\mingw64\bin\g++.exe")
```

You can also select another compatible compiler:

```python
cpp_simple_interface.set_gpp_filepath("clang++")
cpp_simple_interface.set_gpp_filepath("ccache g++")
```

### `get_gpp_filepath()`

Return the compiler command or path currently used by the package.

```python
print(cpp_simple_interface.get_gpp_filepath())
```

## Checking Compiler Availability

The package also includes a small command-line diagnostic module:

```bash
python -m cpp_simple_interface.check_gpp
```

It prints the detected operating system, Python version, compiler availability,
and basic installation suggestions when `g++` cannot be found.

## Troubleshooting

### `Error: g++ not found`

Install GCC/MinGW and make sure the compiler directory is available in your
system `PATH`. If your compiler is installed in a custom location, call
`set_gpp_filepath()` before compiling or set the `CXX` environment variable
before starting Python.

### `FileNotFoundError` from `set_gpp_filepath()`

The requested compiler did not pass the immediate `--version` check. The package
keeps using the previous compiler, so a failed call does not leave the module in
a broken state.

### `Error: .cpp file not found`

Check that each path in `cpp_files` exists relative to the current working
directory of your Python process.

### `Error: Not a valid .cpp file`

Only files ending in `.cpp` are accepted by `compile_cpp_files()`.

### Warnings do not fail compilation

Compilation success is determined only by the compiler return code. Warnings are
captured by the compiler but do not make `compile_cpp_files()` return `False`.

## License

This project is licensed under the MIT License.
