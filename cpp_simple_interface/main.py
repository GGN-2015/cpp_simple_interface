import subprocess
import platform
import os

try:
    from .check_gpp import check_gpp_availability
except:
    from check_gpp import check_gpp_availability

def check_gpp_exists() -> bool:
    is_available, msg = check_gpp_availability("g++", "--version")
    return is_available

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
    
    # 2. Construct g++ compilation command
    # Core command format: g++ [source files] -o [output] -std=c++17
    compile_cmd = [
        "g++",
        *cpp_files,  # Unpack source file list
        "-o", exe_output_path,
        *other_flags
    ]
    
    # 3. Configure subprocess parameters (cross-platform support)
    subprocess_kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True
    }
    # Hide console window on Windows platform
    if platform.system() == "Windows":
        subprocess_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    
    # 4. Execute compilation command and judge result
    try:
        # Run g++ compilation command
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
        return False, "Error: g++ not found. Please install GCC/MinGW and add to system PATH."
    except Exception as e:
        return False, f"Error: Unexpected exception during compilation - {str(e)}"
