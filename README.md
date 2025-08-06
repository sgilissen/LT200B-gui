# LT200B-gui
Python-based (CustomTkinter) GUI to print labels on the Dymo LetraTag LT200B.
The Dymo LetraTag 200B is a Bluetooth label printer that comes with an iOS and Android app. The app only allows you to print text using a couple of installed fonts. 
This Python app aims to provide a relatively user friendly experience on the Desktop to print text and image labels from your computer.

## Features
- Allows printing labels on a Dymo LT200B printer from desktops (mostly tested in Linux)
- Scanning functionality to scan for your printer
- Both text labels and images are supported

## Usage
### From the source
It is recommended to use a Virtual Environment when using this script from the source.
#### Instruction for Linux/Mac/WSL (only tested on Linux)
`python -m venv lt200b_venv`

Activate the Virtual Environment

`source lt200b_venv/bin/activate`

Install the requirements

`pip install -r requirements.txt`

Run the script

`python main.py`

### Release version
Currently available for Linux and Windows. 
#### Linux
Unzip the file. 

`chmod +x LT200B`

Run the executable

#### Windows
Unzip the file. 
Run the executable.

## Screenshots

![Main window](https://github.com/sgilissen/LT200B-gui/blob/main/screenshots/main.png?raw=true)
![Scanning for devices](https://github.com/sgilissen/LT200B-gui/blob/main/screenshots/scan.png?raw=true)

## Acknowledgements
[Alexander Horn](https://github.com/alexhorn) for his [LT200B Python repository](https://github.com/alexhorn/lt200b). His code has been used as a base here, I've just wrapped it in a GUI and added the scanning functionality.

