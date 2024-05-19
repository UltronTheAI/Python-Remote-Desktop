# Python Remote Desktop
The Python Remote Desktop project allows users to control their PC remotely using Python. It provides features like screen sharing, audio sharing, remote control, and more.

## Getting Started
1. Clone this repository:
    
        git clone https://github.com/UltrontheAI/Python-Remote-Desktop.git

2. Install the required dependencies:
    
        pip install python-socketio PyAutoGUI PyAudio
        npm i

4. Run the server (index.js):
        
        node index.js

5. Connect to the server using the Python client (host.py):

        python host.py

## Features
1. Screen sharing
2. Audio sharing
3. Remote control (mouse and keyboard)
4. Toggle shutdown and restart
5. Adjustable frame rate (FPS)
## Usage
1. Start the server using node index.js.
2. Run the Python client (host.py) on the target machine.
3. Use the provided controls to interact with the remote PC.
## Control Commands
1. Press ‘s’ to toggle shutdown.
2. Press ‘r’ to toggle restart.
3. Press ‘k’ to toggle keyboard control.
4. Press ‘m’ to toggle mouse movement.
5. Press ‘c’ to toggle mouse click.

Feel free to customize and enhance this project according to your needs! If you have any questions or need further assistance, don’t hesitate to ask. 🚀

# License: MIT
