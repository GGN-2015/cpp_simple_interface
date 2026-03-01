# cpp_simple_interface
compile and run C++ executable in python with local compiler.

## Install

```bash
pip install cpp-simple-interface
```

## Usage

```python
import cpp_simple_interface

# create test file
with open("a.cpp", "w") as fp:
    fp.write(
"""
#include <cstdio>
int main() {
    printf("hello world!");
    return 0;
}
""")

# compile test file
suc, msg = cpp_simple_interface.compile_cpp_files(["./a.cpp"], "./a.exe")
if not suc:
    print(msg)
```
