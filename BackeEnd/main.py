import asyncio
import websockets
import socket
from flask import Flask, send_from_directory
from threading import Thread

# Definir un conjunto global para los clientes conectados
connected_clients = set()

def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

async def handler(websocket, path):
    # Añadir el nuevo cliente a la lista de clientes conectados
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Mensaje recibido: {message}")
            # Enviar el mensaje a todos los clientes conectados
            if connected_clients:  # Verificar si hay clientes conectados
                await asyncio.gather(*(asyncio.create_task(client.send(message)) for client in connected_clients if client.open))
    except websockets.exceptions.ConnectionClosed:
        print("Un cliente se ha desconectado.")
    finally:
        # Eliminar el cliente de la lista cuando se desconecta
        connected_clients.remove(websocket)

async def websocket_server():
    local_ip = get_local_ip()
    async with websockets.serve(handler, "0.0.0.0", 5000): 
        print(f"Servidor WebSocket activo en ws://{local_ip}:5000")
        await asyncio.Future()  

def run_flask():
    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)  

app = Flask(__name__, static_folder='../FrontEnd/dist', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('../FrontEnd/dist', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../FrontEnd/dist', path)

if __name__ == '__main__':
    # Inicia el servidor WebSocket en un hilo separado
    websocket_thread = Thread(target=lambda: asyncio.run(websocket_server()))
    websocket_thread.start()

    # Inicia el servidor Flask en el hilo principal
    run_flask()
