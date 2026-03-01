import subprocess
import platform
import sys

def check_gpp_availability(cmd_name="g++", sub_cmd_name="--version"):
    """
    Check if <cmd_name> is available in system PATH by running '<cmd_name> --version'
    Returns: (bool: is_available, str: message)
    """
    # Base command to verify g++ version
    cmd = [cmd_name, sub_cmd_name]
    
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
            return (True, f"{cmd_name} is available. Version: {version}")
        else:
            return (False, f"{cmd_name} execution failed: {result.stderr.strip()}")
    
    except FileNotFoundError:
        return (False, f"{cmd_name} not found. Ensure GCC/MinGW is installed and added to PATH.")
    except subprocess.TimeoutExpired:
        return (False, f"{cmd_name} --version timed out (10s limit)")
    except Exception as e:
        return (False, f"Unexpected error checking g++: {str(e)}")

def main():
    print("=== g++ Availability Check ===")
    print(f"OS: {platform.system()} {platform.machine()}")
    print(f"Python Version: {sys.version.split()[0]}")
    print("-" * 35)
    
    # Perform g++ availability check
    is_available, message = check_gpp_availability()
    
    # Print result with clear status indicators
    if is_available:
        print(f"INFO: {message}")
    else:
        print(f"ERROR: {message}")
        
    # Provide OS-specific installation guidance for troubleshooting
    if not is_available:
        os_type = platform.system()
        print("\n💡 Installation Suggestions:")
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