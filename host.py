import socketio
import pyautogui
import base64
import io
import pyaudio
from time import sleep
import platform
import subprocess
import threading
import os

# Connect to the Node.js server
sio = socketio.Client()
sio.connect('http://localhost:3000')

clint = ''
pc = ''
user = 'UltronPC'
password = '1'

enable_move = True
enable_click = True
enable_keyboard = True
enable_shutdown = True
enable_restart = True
current_fps = 60

fps = lambda fps: 1/60 if fps > 60 else (1 if fps < 1 else 1/fps)

def clear_screen():
    """
    Clears the screen based on the operating system.
    """
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Linux and macOS
        os.system('clear')

def handle_input():
    global enable_shutdown
    global enable_restart
    global enable_keyboard
    global enable_move
    global enable_click
    global user
    global pc
    global current_fps

    while True:
        print(f'###CONTROL: {user} | {pc}\n')
        print("Press 's' to toggle shutdown, 'r' for restart, 'k' for keyboard, 'm' for move, 'c' for click.")
        print(f'\nMouse Move: {enable_move}\nMouse Click: {enable_click}\nKeyboard: {enable_keyboard}\nShutdown: {enable_shutdown}\nRestart: {enable_restart}\nFPS: {current_fps}\n')
        key = input("Press: ")
        if key == 's':
            enable_shutdown = not enable_shutdown
            clear_screen()
        elif key == 'r':
            enable_restart = not enable_restart
            clear_screen()
        elif key == 'k':
            enable_keyboard = not enable_keyboard
            clear_screen()
        elif key == 'm':
            enable_move = not enable_move
            clear_screen()
        elif key == 'c':
            enable_click = not enable_click
            clear_screen()
        elif key == 'x':
            clear_screen()
        else:
            try:
                current_fps = int(key)
            except: pass

# Start a separate thread to handle user input
input_thread = threading.Thread(target=handle_input)
input_thread.daemon = True

@sio.event
def connect():
    print("Connected to the server")

@sio.event
def disconnect():
    print("Disconnected from the server")

@sio.on('control_id')
def on_control_id(data):
    global pc
    pc = data

    sio.emit('host_info', [pc, user])
    input_thread.start()

@sio.on('host')
def on_host(data):
    global clint
    global password

    if data['password'] == password and clint == '':
        clint = data['clint']
        width, height = pyautogui.size()
        sio.emit('screen_size', {'width': width, 'height': height, 'to': clint})
        print(f'CLINT: {width}x{height} {clint}')

@sio.on('clint_left')
def on_clint_left(data):
    global clint
    if data == clint:
        print(f'CLINT {clint} LEFT')
        clint = ''

@sio.on('remote_control')
def on_remote_control(data):
    global password
    
    control_type = data['type']
    Password = data['password']

    if Password == password and clint == data['me']:
        if control_type == 'mouse_move' and enable_move:
            x, y = data['x'], data['y']
            pyautogui.moveTo(x, y)
        elif control_type == 'mouse_click' and enable_click:
            x, y = data['x'], data['y']
            button = data['button']
            if button == 'left':
                pyautogui.click(x, y, button='left')
            elif button == 'right':
                pyautogui.click(x, y, button='right')
        elif control_type == 'keypress' and enable_keyboard:
            key = data['key']
            pyautogui.press(key)
        elif control_type == 'shutdown' and enable_shutdown:
            try:
                operating_system = platform.system()

                if operating_system == "Windows":
                    subprocess.run(["shutdown", "/s"])
                elif operating_system == "Linux" or operating_system == "Darwin":
                    subprocess.run(["shutdown", "-h", "now"])
                else:
                    return "Operating system not supported.", 500
            except Exception as e:
                print(f"Error during shutdown: {e}")
        elif control_type == 'restart' and enable_restart:
            try:
                operating_system = platform.system()

                if operating_system == "Windows":
                    subprocess.run(["shutdown", "/r", "/t", "0"])
                elif operating_system == "Linux" or operating_system == "Darwin":
                    subprocess.run(["shutdown", "-r", "now"])
                else:
                    return "Operating system not supported.", 500
            except Exception as e:
                print(f"Error during restart: {e}")

def capture_screen():    
    while True:
        # Capture the screen
        screen = pyautogui.screenshot()
        img_bytes = io.BytesIO()
        screen.save(img_bytes, format='JPEG')
        
        # Encode the image as base64
        img_data = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        
        # Emit the screen data to the server
        sio.emit('screen_share', {'image': img_data, "to": clint})
        
        # Sleep for a bit to control the refresh rate
        sleep(fps(current_fps))

def capture_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024)

    while True:
        data = stream.read(1024)
        audio_data = base64.b64encode(data).decode('utf-8')
        sio.emit('audio_share', {'audio': audio_data, 'to': clint})

if __name__ == '__main__':
    try:
        screen_thread = threading.Thread(target=capture_screen)
        audio_thread = threading.Thread(target=capture_audio)
        
        screen_thread.start()
        audio_thread.start()
        
        screen_thread.join()
        audio_thread.join()
    except KeyboardInterrupt:
        print("Screen and audio sharing stopped.")
