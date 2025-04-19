import sys
import os
import zipfile
import tempfile
import shutil
import subprocess
from pathlib import Path
import argparse
import time

# ASCII баннер VCN
BANNER = r"""
 __      __ _____  _   _
 \ \    / /|  __ \| \ | |
  \ \  / / | |    |  \| |
   \ \/ /  | |    | . ` |
    \  /   | |____| |\  |
     \/     \_____|_| \_|
                                                                   
    VCN Compiler        
    {}                  
""".format("Github: https://github.com/irefuse2sync/VCN-Compiler")

# Шаблон launcher скрипта
LAUNCHER_TEMPLATE = r'''
import os
import sys
import zipfile
import tempfile
import subprocess
import atexit
import shutil
import time
import argparse

 

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def check_admin():
    """Check if the application has administrator privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart the application with administrator privileges"""
    import ctypes
    import sys
    
    ctypes.windll.shell32.ShellExecuteW(
        None, 
        "runas", 
        sys.executable, 
        " ".join(sys.argv), 
        None, 
        1
    )

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='VCN Compiler Launcher')
    parser.add_argument('-admin', '-a', action='store_true', help='Run with administrator privileges')
    args, unknown = parser.parse_known_args()
    
    # If admin rights are requested but not available, restart with elevation
    if args.admin and not check_admin():
        run_as_admin()
        return
    
 
    
    # Get current directory
    current_dir = os.getcwd()
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Function to clean up temporary directory
    def cleanup():
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
    
    # Register cleanup function
    atexit.register(cleanup)
    
    try:
        # Extract the zip file embedded in the exe
        zip_path = resource_path("batch_archive.zip")
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # Find the batch file in the extracted directory
        batch_files = [f for f in os.listdir(temp_dir) if f.endswith('.bat') or f.endswith('.cmd')]
        if not batch_files:
            print("Error: No batch file found in the archive")
            return
        
        source_batch_file = os.path.join(temp_dir, batch_files[0])
        
        # Create a temporary batch file in the current directory
        temp_batch_file = os.path.join(current_dir, f"temp_{int(time.time())}_{batch_files[0]}")
        
        try:
            # Copy the batch file to current directory
            shutil.copy2(source_batch_file, temp_batch_file)
            
            # Set the hidden attribute for the temp batch file
            subprocess.call(["attrib", "+h", temp_batch_file])
            
            # Run the batch file in the current directory
            subprocess.call([temp_batch_file], shell=True)
            
        finally:
            # Clean up the temporary batch file if it exists
            if os.path.exists(temp_batch_file):
                try:
                    os.remove(temp_batch_file)
                except:
                    pass
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
'''

def find_python_executable():
    """Находит путь к Python-интерпретатору, даже если программа запущена как exe"""
    # Если запущено как Python скрипт
    if not getattr(sys, 'frozen', False):
        return sys.executable
    
    # Если запущено как exe, ищем Python в системе
    try:
        # Пробуем найти python в PATH
        python_paths = ["python", "python3"]
        for path in python_paths:
            try:
                result = subprocess.run(
                    [path, "--version"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    print(f"Found Python: {path}")
                    return path
            except:
                pass
        
        # Если не нашли в PATH, ищем стандартные места установки
        possible_paths = [
            r"C:\Python39\python.exe",
            r"C:\Python38\python.exe",
            r"C:\Python37\python.exe",
            r"C:\Python36\python.exe",
            r"C:\Program Files\Python39\python.exe",
            r"C:\Program Files\Python38\python.exe",
            r"C:\Program Files\Python37\python.exe",
            r"C:\Program Files\Python36\python.exe",
            r"C:\Program Files (x86)\Python39\python.exe",
            r"C:\Program Files (x86)\Python38\python.exe",
            r"C:\Program Files (x86)\Python37\python.exe",
            r"C:\Program Files (x86)\Python36\python.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found Python at: {path}")
                return path
                
        print("Python interpreter not found. Please make sure Python is installed.")
        return None
    except Exception as e:
        print(f"Error finding Python: {str(e)}")
        return None

def run_pyinstaller(command):
    """Запустить PyInstaller с заданными аргументами в отдельном процессе"""
    try:
        # Находим путь к Python
        python_exe = find_python_executable()
        if not python_exe:
            print("Error: Python interpreter not found")
            return False
        
        print(f"Using Python: {python_exe}")
        
        # Создаем временную директорию для работы
        temp_dir = tempfile.mkdtemp()
        try:
            # Создаем временный скрипт для установки PyInstaller
            pip_script = os.path.join(temp_dir, "install_pyinstaller.py")
            with open(pip_script, 'w', encoding='utf-8') as f:
                f.write("""
import subprocess
import sys

try:
    import PyInstaller
    print("PyInstaller already installed")
except ImportError:
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("PyInstaller installed successfully")
""")
            
            # Устанавливаем PyInstaller
            print("Checking/Installing PyInstaller...")
            install_result = subprocess.run(
                [python_exe, pip_script],
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            if install_result.returncode != 0:
                print(f"Error installing PyInstaller:")
                print(install_result.stdout)
                print(install_result.stderr)
                return False
            
            print(install_result.stdout)
            
            # Парсим аргументы PyInstaller, разделяем их вручную
            args = []
            current_arg = ""
            in_quotes = False
            for char in command:
                if char == '"' and (not current_arg or current_arg[-1] != '\\'):
                    in_quotes = not in_quotes
                    current_arg += char
                elif char == ' ' and not in_quotes:
                    if current_arg:
                        args.append(current_arg)
                        current_arg = ""
                else:
                    current_arg += char
            if current_arg:
                args.append(current_arg)
            
            # Очищаем аргументы от кавычек
            clean_args = []
            for arg in args:
                if arg.startswith('"') and arg.endswith('"'):
                    clean_args.append(arg[1:-1])
                else:
                    clean_args.append(arg)
            
            # Создаем временный скрипт для запуска PyInstaller
            pyinstaller_script = os.path.join(temp_dir, "run_pyinstaller.py")
            with open(pyinstaller_script, 'w', encoding='utf-8') as f:
                f.write("""
# -*- coding: utf-8 -*-
import PyInstaller.__main__
import sys
import os

# Validate paths
args = []
for arg in {0}:
    if arg.startswith('--'):
        args.append(arg)
    elif '=' in arg:
        key, value = arg.split('=', 1)
        if os.path.exists(value):
            args.append(f'{{key}}={{value}}')
        else:
            print(f"Warning: Path '{{value}}' in argument '{{arg}}' does not exist")
            args.append(arg)
    elif os.path.exists(arg):
        args.append(arg)
    else:
        print(f"Warning: Path '{{arg}}' does not exist")
        args.append(arg)

print("PyInstaller arguments:", args)

# Run PyInstaller
PyInstaller.__main__.run(args)
""".format(repr(clean_args)))
            
            # Запускаем PyInstaller
            print(f"Running PyInstaller with parsed arguments: {clean_args}")
            pyinstaller_process = subprocess.run(
                [python_exe, pyinstaller_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Проверяем результат выполнения
            if pyinstaller_process.returncode != 0:
                print("PyInstaller failed with error:")
                print(pyinstaller_process.stdout)
                print(pyinstaller_process.stderr)
                return False
            
            print(pyinstaller_process.stdout)
            return True
            
        finally:
            # Очищаем временную директорию
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
                
    except Exception as e:
        print(f"Error running PyInstaller: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_exe_wrapper(batch_file_path, icon_path=None, require_admin=False):
    # Check if batch file exists
    if not os.path.exists(batch_file_path):
        print(f"Error: Batch file '{batch_file_path}' not found.")
        return False
    
    # Create base name for the executable (same as batch file without extension)
    base_name = os.path.splitext(os.path.basename(batch_file_path))[0]
    output_exe = f"{base_name}.exe"
    
    # По умолчанию всегда используем эту иконку, если не указана другая
    default_icon = ".\\viso-compiler-app.ico"
    if icon_path is None:
        print(f"No icon specified, using default: {default_icon}")
        icon_path = default_icon
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a zip file containing the batch file
        zip_path = os.path.join(temp_dir, "batch_archive.zip")
        batch_filename = os.path.basename(batch_file_path)
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(batch_file_path, batch_filename)
        
        # Replace placeholders in the template
        launcher_content = LAUNCHER_TEMPLATE.replace('{{BANNER}}', BANNER)
        
        # Write the launcher script
        launcher_script = os.path.join(temp_dir, "launcher.py")
        with open(launcher_script, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        # Use PyInstaller to create an executable
        try:
            # Prepare PyInstaller command
            pyinstaller_cmd = f'--onefile --add-data "{zip_path}{os.pathsep}." '
            
            # Always add icon parameter, even if the icon doesn't exist
            # PyInstaller will simply ignore it if file doesn't exist
            pyinstaller_cmd += f'--icon "{icon_path}" '
            
            # Add UAC admin flag if required
            if require_admin:
                pyinstaller_cmd += '--uac-admin '
            
            # Add the launcher script
            pyinstaller_cmd += f'"{launcher_script}"'
            
            # Run PyInstaller
            if not run_pyinstaller(pyinstaller_cmd):
                print("Error: Failed to run PyInstaller")
                return False
            
            # Move the executable from dist folder to current directory
            dist_exe = os.path.join("dist", "launcher.exe")
            if os.path.exists(dist_exe):
                shutil.move(dist_exe, output_exe)
                print(f"Successfully created executable: {output_exe}")
                
                # Clean up PyInstaller directories
                if os.path.exists("dist"):
                    shutil.rmtree("dist")
                if os.path.exists("build"):
                    shutil.rmtree("build")
                if os.path.exists("launcher.spec"):
                    os.remove("launcher.spec")
                    
                return True
            else:
                print("Error: Failed to create executable")
                return False
                
        except Exception as e:
            print(f"Error creating executable: {str(e)}")
            return False
    
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
    
    return False

def compile_self():
    """Компилирует сам скрипт batch_packer.py в исполняемый файл"""
    try:
        print("Compiling batch_packer.py into an executable...")
        
        # Проверяем абсолютный путь к скрипту
        script_path = os.path.abspath(__file__)
        print(f"Script path: {script_path}")
        
        if not os.path.exists(script_path):
            print(f"Error: Script file '{script_path}' does not exist")
            return False
        
        # Prepare PyInstaller command
        pyinstaller_cmd = '--onefile '
        
        # Always try to use the default icon
        default_icon = "vcn-compiler-app.ico"
        if os.path.exists(default_icon):
            icon_path = os.path.abspath(default_icon)
            pyinstaller_cmd += f'--icon "{icon_path}" '
            print(f"Using icon: {icon_path}")
        else:
            print(f"Warning: Default icon '{default_icon}' not found. Executable will use system default icon.")
        
        # Add the main script - убираем кавычки, т.к. они добавляются внутри run_pyinstaller
        script_path_clean = script_path.replace('"', '')
        pyinstaller_cmd += f'{script_path_clean}'
        
        # Run PyInstaller
        if not run_pyinstaller(pyinstaller_cmd):
            print("Error: Failed to run PyInstaller")
            return False
        
        # Check if executable was created
        dist_exe = os.path.join("dist", os.path.basename(script_path).replace('.py', '.exe'))
        if os.path.exists(dist_exe):
            # Move to current directory
            output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vcn-compiler.exe")
            shutil.move(dist_exe, output_path)
            print(f"Successfully compiled to: {output_path}")
            
            return True
        else:
            print("Error: Failed to compile batch_packer.py")
            return False
            
    except Exception as e:
        print(f"Error during compilation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Display banner
    print(BANNER)
    
    # Create command line argument parser
    parser = argparse.ArgumentParser(description=f'VCN Batch File Compiler\n\nUsage: {sys.argv[0]} <path_to_batch_file>')
    parser.add_argument('batch_file', nargs='?', help='Path to the batch file to package')
    parser.add_argument('--icon', help='Path to the icon file for the executable')
    parser.add_argument('--admin', action='store_true', help='Create an executable that requests administrator privileges')
    parser.add_argument('--compile-self', action='store_true', help='Compile this script into an executable')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if we need to compile self
    if args.compile_self:
        return compile_self()
    
    # Check if batch file is provided
    if not args.batch_file:
        parser.print_help()
        return False
    
    # Check icon file existence - даже если иконка не указана, пытаемся использовать дефолтную
    icon_path = args.icon
    
    # Start compilation
    return create_exe_wrapper(args.batch_file, icon_path, args.admin)

if __name__ == "__main__":
    main() 