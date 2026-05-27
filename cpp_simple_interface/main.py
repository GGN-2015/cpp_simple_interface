import subprocess
import platform
import os
import shlex

# Default filepath
DEFAULT_GPP_FILEPATH = "g++"
GPP_FILEPATH = os.environ.get("CXX", "").strip() or DEFAULT_GPP_FILEPATH

def _compiler_command_parts(compiler: str) -> list[str]:
    compiler = compiler.strip()
    if not compiler:
        raise ValueError("Compiler path cannot be empty.")

    unquoted_compiler = compiler
    if len(compiler) >= 2 and compiler[0] == compiler[-1] and compiler[0] in ('"', "'"):
        unquoted_compiler = compiler[1:-1]

    if os.path.exists(unquoted_compiler) or not any(char.isspace() for char in unquoted_compiler):
        return [unquoted_compiler]

    parts = shlex.split(compiler, posix=True)
    if not parts:
        raise ValueError("Compiler path cannot be empty.")
    return parts

def check_gpp_exists() -> bool:
    try:
        from .check_gpp import check_gpp_availability
    except ImportError:
        from check_gpp import check_gpp_availability

    try:
        compiler_parts = _compiler_command_parts(GPP_FILEPATH)
    except ValueError:
        return False

    is_available, msg = check_gpp_availability(compiler_parts, "--version")
    return is_available

def set_gpp_filepath(gpp_filepath:str):
    global GPP_FILEPATH

    try:
        compiler_parts = _compiler_command_parts(gpp_filepath)
        try:
            from .check_gpp import check_gpp_availability
        except ImportError:
            from check_gpp import check_gpp_availability

        is_available, msg = check_gpp_availability(compiler_parts, "--version")
    except ValueError as exc:
        raise ValueError(str(exc)) from exc

    if not is_available:
        raise FileNotFoundError(f"{gpp_filepath} is not an available C++ compiler.")

    GPP_FILEPATH = gpp_filepath.strip()

def get_gpp_filepath() -> str:
    return GPP_FILEPATH

def compile_cpp_files(cpp_files: list[str], exe_output_path: str, other_flags=["-std=c++17"]) -> tuple[bool, str]:
    """
    Compile specified .cpp files into an executable .exe file using g++ compiler.
    Only judge compilation success by return code (ignore warnings completely).
    
    Args:
        cpp_files: List of strings, containing paths to all .cpp files to compile (e.g., ["main.cpp", "utils.cpp"])
        exe_output_path: Full path of the generated exe file (e.g., "./output/app.exe")
    
    Returns:
        tuple: (is_compilation_successful, message)
            - First element: True for successful compilation, False for failure
            - Second element: Detailed prompt message (success/failure reason)
    """
    # 1. Validate input parameters
    # Check if cpp file list is empty
    if not cpp_files:
        return False, "Error: The list of .cpp files is empty."
    
    # Check if specified .cpp files exist and have valid extension
    for cpp_file in cpp_files:
        if not os.path.exists(cpp_file):
            return False, f"Error: .cpp file not found - {cpp_file}"
        if not cpp_file.endswith(".cpp"):
            return False, f"Error: Not a valid .cpp file - {cpp_file}"
    
    # 2. Configure subprocess parameters (cross-platform support)
    subprocess_kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True
    }
    # Hide console window on Windows platform
    if platform.system() == "Windows":
        subprocess_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    
    # 3. Execute compilation command and judge result
    try:
        # Core command format: compiler [source files] -o [output] -std=c++17
        compile_cmd = [
            *_compiler_command_parts(GPP_FILEPATH),
            *cpp_files,  # Unpack source file list
            "-o", exe_output_path,
            *other_flags
        ]

        # Run GPP_FILEPATH compilation command
        result = subprocess.run(compile_cmd, **subprocess_kwargs)
        
        # Judge success only by return code (0 = success, non-0 = failure)
        if result.returncode == 0:
            # Additional check: verify exe file is generated
            if os.path.exists(exe_output_path):
                return True, f"Success: Compilation completed. Output file - {exe_output_path}"
            else:
                return False, f"Error: Return code is 0 but exe file not generated - {exe_output_path}"
        else:
            # Get error details from stderr (empty if no error message)
            error_detail = result.stderr.strip() if result.stderr else "No specific error message"
            return False, f"Error: Compilation failed (return code: {result.returncode})\nError details: {error_detail}"
    
    except FileNotFoundError:
        return False, f"Error: {GPP_FILEPATH} not found. Please install GCC/MinGW and add to system PATH."
    except ValueError as e:
        return False, f"Error: Invalid compiler path - {str(e)}"
    except Exception as e:
        return False, f"Error: Unexpected exception during compilation - {str(e)}"
