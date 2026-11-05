# FileForge
A simple file organization tool for naming and organizing university files on macOS built with Python and PySide 6.
  **Status**: Early development

## About
FileForge is a personal project I am working on as a computer science major at the University of the Cumberlands. It is intended to help university students by making the organization of repetitive assignment names more streamlined by setting consistent rules for file name structures. For example, a coding lab might be structured with the file name "ITCS131-CodingLab2_BinarySearch.py". 

## Features
- Basic desktop application window
- Support for custom Qt stylesheet (.qss) files
- Initial drag-and-drop interface

## Technologies
- Python3
- PySide6
- Qt Stylesheets (QSS)
- Automator (MacOS)
- PyInstaller

## Deployment
To install clone the repository and create a virtual environment:
```
git clone https://github.com/lukasdebord/fileforge.git
cd fileforge

python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:
```
pip install -r requirements.txt
```

Run the main application:
```
python -m fileforge.main
```

Run rename dialog through CLI
```
python -m fileforge.main --rename [file-path ...]
```
When multiple files are provided, FileForge appends incrementing numbers to the
entered filename (for example, `screenshot1.png` and `screenshot2.png`) while
preserving each file's original extension.

Set up build
```
python -m PyInstaller --clean FileForge.spec
```
### MacOS
If you are MacOS you need to add a quick action to use File Forge on any file type
1. Open Automater and create a new document
2. Click Quick Action
3. Set Workflow recieves current files or folders in Finder.app
4. Add Run Shell Script
5. Set Pass Input: to as arguments
5. Paste into the script and set location of build in \<build-path\>
```
for file in "$@"; do
    /usr/bin/open -n -a "<build-path>" --args --rename "$file"
done
```
7. Save it with command + s and name it Rename with FileForge

If you have installed the build into your applications folder you can copy Rename with File Forge.workflow
into ~/Library/Services

## License
This project is currently for personal development and experience.
