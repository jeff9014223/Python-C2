import socketio, json, os, requests

socket = socketio.Client()

@socket.event
def connect():
    ip_adress = requests.get("https://api.ipify.org").text
    socket.emit("init", json.dumps({"ip": ip_adress, "username": os.getlogin()}))

socket.connect("http://127.0.0.1:5000")
socket.wait()
