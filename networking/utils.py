import json
import socket

from game import Move

def send_json(conn: socket.socket, payload: str) -> None:
    message = payload + "\n"
    conn.sendall(message.encode())

def send_move(conn: socket.socket, move: Move) -> None:
    send_json(conn, json.dumps({"move": json.loads(Move.to_json(move))}))
    
def send_error(conn: socket.socket, message: str) -> None:
    send_json(conn, json.dumps({"error": message}))