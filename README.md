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

Run the application:
```
python -m fileforge.main
```

## License
This project is currently for personal development and experience.
