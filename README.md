# VCN Compiler

This tool creates an executable that contains a batch file. When the executable is run, it extracts the batch file to a temporary location and runs it in the original directory.

## Features

- Simple and fast way to convert batch files to executables
- Hidden execution of batch files
- Custom icons support
- Administrator privileges request option
- Small output file size

## Requirements

- Python 3.6 or higher
- PyInstaller (will be installed automatically if not present)

## Usage

```
python batch_packer.py <path_to_batch_file> [options]
```

Or if using the compiled version:

```
vcn-compiler.exe <path_to_batch_file> [options]
```

### Options

- `--icon PATH` - Use custom icon for the executable
- `--admin` - Create an executable that requests administrator privileges
- `--compile-self` - Compile the script itself into an executable (vcn-compiler.exe)

### Examples

Basic usage:
```
python batch_packer.py test_script.bat
```

Using a custom icon:
```
python batch_packer.py test_script.bat --icon my_icon.ico
```

Creating an executable that requires admin rights:
```
python batch_packer.py test_script.bat --admin
```

Compiling the tool itself:
```
python batch_packer.py --compile-self
```

## How it works

1. The batch file is compressed into a zip archive
2. PyInstaller creates a standalone executable containing the zip archive
3. When run, the executable extracts the batch file to a temporary directory
4. The batch file is copied to the current directory (with hidden attribute) and executed
5. Both the temporary directory and the batch file are automatically cleaned up after execution

## Notes

- If a file named `vcn-compiler-app.ico` exists in the current directory, it will be used as the default icon
- The output executable will have the same name as the batch file but with an .exe extension 