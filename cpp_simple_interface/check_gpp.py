import subprocess
import platform
import sys

def check_gpp_availability(cmd_name, sub_cmd_name="--version"):
    """
    Check if <cmd_name> is available by running '<cmd_name> --version'
    Returns: (bool: is_available, str: message)
    """
    if isinstance(cmd_name, (list, tuple)):
        cmd = [*cmd_name, sub_cmd_name]
        display_name = " ".join(cmd_name)
    else:
        cmd = [cmd_name, sub_cmd_name]
        display_name = cmd_name

    # Base command to verify GPP_FILEPATH version
    # Configure subprocess parameters with platform-specific flags
    subprocess_kwargs = {
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'text': True,
        'timeout': 10
    }
    
    # Explicitly set creationflags only for Windows (hide console window)
    if platform.system() == 'Windows':
        subprocess_kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
    # For Linux/macOS: no creationflags needed (parameter is Windows-only)
    
    try:
        # Execute the command with platform-specific parameters
        result = subprocess.run(cmd, **subprocess_kwargs)
        
        if result.returncode == 0:
            # Extract first line of version info for brevity
            version = result.stdout.strip().split('\n')[0]
            return (True, f"{display_name} is available. Version: {version}")
        else:
            return (False, f"{display_name} execution failed: {result.stderr.strip()}")
    
    except FileNotFoundError:
        return (False, f"{display_name} not found. Ensure GCC/MinGW is installed and added to PATH.")
    except subprocess.TimeoutExpired:
        return (False, f"{display_name} --version timed out (10s limit)")
    except Exception as e:
        return (False, f"Unexpected error checking g++: {str(e)}")

def main():
    print("=== C++ Compiler Availability Check ===")
    print(f"OS: {platform.system()} {platform.machine()}")
    print(f"Python Version: {sys.version.split()[0]}")
    print("-" * 35)

    try:
        from .main import GPP_FILEPATH, _compiler_command_parts
    except ImportError:
        from main import GPP_FILEPATH, _compiler_command_parts
    
    # Perform g++ availability check
    try:
        compiler_parts = _compiler_command_parts(GPP_FILEPATH)
        is_available, message = check_gpp_availability(compiler_parts)
    except ValueError as exc:
        is_available = False
        message = f"Invalid compiler path: {str(exc)}"
    
    # Print result with clear status indicators
    if is_available:
        print(f"INFO: {message}")
    else:
        print(f"ERROR: {message}")
        
    # Provide OS-specific installation guidance for troubleshooting
    if not is_available:
        os_type = platform.system()
        print("\nInstallation Suggestions:")
        if os_type == 'Windows':
            print("   - Install MinGW-w64 (https://sourceforge.net/projects/mingw-w64/)")
            print("   - Add 'mingw64/bin' directory to your system PATH environment variable")
        elif os_type == 'Linux':
            print("   - Debian/Ubuntu-based systems: sudo apt update && sudo apt install g++")
            print("   - RHEL/CentOS-based systems: sudo dnf install gcc-c++")
        elif os_type == 'Darwin':
            print("   - Install Xcode Command Line Tools: xcode-select --install")

if __name__ == "__main__":
    main()
